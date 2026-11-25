import type { Config, Context } from "@netlify/functions";
import { getStore } from "@netlify/blobs";
import { timingSafeEqual, randomUUID } from "node:crypto";

// All data lives in two private Blobs stores, kept in the EU and reached only through this function.
const REGION = "eu-central-1";
const data = () => getStore({ name: "checklist", region: REGION, consistency: "strong" });
const files = () => getStore({ name: "uploads", region: REGION, consistency: "strong" });

const MAX_JSON = 256 * 1024;
const MAX_FILE = 4 * 1024 * 1024; // function payload limit is ~4.5 MB of binary
const TYPES = new Set(["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif", "application/pdf"]);

function same(a: string, b: string) {
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

function role(req: Request): "jason" | "admin" | null {
  const pin = (req.headers.get("x-pin") || "").trim();
  if (!/^\d{8}$/.test(pin)) return null;
  const j = Netlify.env.get("JASON_PIN") || "", a = Netlify.env.get("ADMIN_PIN") || "";
  if (a && same(pin, a)) return "admin";
  if (j && same(pin, j)) return "jason";
  return null;
}

const json = (body: unknown, status = 200) =>
  Response.json(body, { status, headers: { "cache-control": "no-store" } });

export default async (req: Request, context: Context) => {
  const who = role(req);
  if (!who) return json({ error: "wrong_pin" }, 401);

  const route = new URL(req.url).pathname.replace(/^\/api\/?/, "").replace(/\/+$/, "");
  const m = req.method;

  // Who am I (used at login)
  if (route === "me" && m === "GET") return json({ role: who });

  // Answers
  if (route === "answers" && m === "GET") {
    const entry = await data().get("answers", { type: "json" });
    return json(entry || null);
  }
  if (route === "answers" && m === "PUT") {
    const text = await req.text();
    if (text.length > MAX_JSON) return json({ error: "too_large" }, 413);
    let body: any;
    try { body = JSON.parse(text); } catch { return json({ error: "bad_json" }, 400); }
    if (!body || typeof body !== "object" || Array.isArray(body)) return json({ error: "bad_json" }, 400);
    const clean = {
      answers: body.answers && typeof body.answers === "object" ? body.answers : {},
      files: body.files && typeof body.files === "object" ? body.files : {},
      skips: body.skips && typeof body.skips === "object" ? body.skips : {},
      submitted: !!body.submitted,
      submittedAt: typeof body.submittedAt === "string" ? body.submittedAt : null,
      updatedAt: new Date().toISOString(),
      updatedBy: who,
    };
    await data().setJSON("answers", clean);
    return json({ ok: true, updatedAt: clean.updatedAt });
  }

  // Upload a file: raw body, type in content-type, original name in x-name
  if (route === "upload" && m === "POST") {
    const type = (req.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
    if (!TYPES.has(type)) return json({ error: "unsupported_type" }, 415);
    const buf = await req.arrayBuffer();
    if (!buf.byteLength) return json({ error: "empty" }, 400);
    if (buf.byteLength > MAX_FILE) return json({ error: "too_large" }, 413);
    const id = randomUUID();
    const name = decodeURIComponent(req.headers.get("x-name") || "file").slice(0, 120);
    await files().set(id, buf, { metadata: { type, name, by: who, at: new Date().toISOString() } });
    return json({ id, type, name });
  }

  // Read or delete one file
  const fm = route.match(/^file\/([0-9a-f-]{36})$/);
  if (fm && m === "GET") {
    const entry = await files().getWithMetadata(fm[1], { type: "arrayBuffer" });
    if (entry === null) return json({ error: "not_found" }, 404);
    const meta = entry.metadata as { type?: string; name?: string };
    return new Response(entry.data as ArrayBuffer, {
      headers: {
        "content-type": meta.type || "application/octet-stream",
        "content-disposition": `inline; filename="${(meta.name || "file").replace(/[^\w.\- ]/g, "_")}"`,
        "cache-control": "private, no-store",
      },
    });
  }
  if (fm && m === "DELETE") {
    await files().delete(fm[1]);
    return json({ ok: true });
  }

  return json({ error: "not_found" }, 404);
};

export const config: Config = {
  path: "/api/*",
  rateLimit: { windowLimit: 120, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
