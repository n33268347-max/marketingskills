import type { Config } from "@netlify/functions"

// Reads one property listing page (Bayut, Property Finder, Dubizzle) when a viewer pastes its link,
// like a chat app building a link preview, and returns the key facts as plain text lines.
const ALLOWED = [/(^|\.)bayut\.com$/i, /(^|\.)propertyfinder\.ae$/i, /(^|\.)dubizzle\.com$/i]
const allowed = (u: URL) => u.protocol === "https:" && ALLOWED.some(rx => rx.test(u.hostname))

const decode = (s: string) => s.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;|&#x27;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ")
function meta(html: string, key: string) {
  const re = new RegExp(`<meta[^>]+(?:property|name)=["']${key}["'][^>]*>`, "i")
  const tag = html.match(re)?.[0]; if (!tag) return ""
  return decode(tag.match(/content=["']([^"']*)["']/i)?.[1] || "")
}

function walk(node: unknown, out: Record<string, unknown>) {
  if (Array.isArray(node)) { node.forEach(n => walk(n, out)); return }
  if (!node || typeof node !== "object") return
  const o = node as Record<string, unknown>
  for (const [k, v] of Object.entries(o)) {
    const key = k.toLowerCase()
    if (["numberofrooms", "numberofbedrooms", "bedrooms"].includes(key) && out.beds == null && (typeof v === "number" || typeof v === "string")) out.beds = v
    else if (key === "floorsize" && v && typeof v === "object" && out.size == null) { const f = v as Record<string, unknown>; out.size = f.value; out.sizeUnit = f.unitCode || f.unitText }
    else if (key === "price" && out.price == null && (typeof v === "number" || typeof v === "string") && Number(String(v).replace(/,/g, "")) > 1000) out.price = v
    else if (key === "addresslocality" && typeof v === "string" && !out.locality) out.locality = v
    else if (key === "streetaddress" && typeof v === "string" && !out.street) out.street = v
    else if ((key === "name" || key === "headline") && typeof v === "string" && !out.name && v.length > 10) out.name = v
    else if (key === "description" && typeof v === "string" && !out.description) out.description = v
    else if (key === "unittext" && typeof v === "string" && /year|month/i.test(v)) out.period = v
    if (v && typeof v === "object") walk(v, out)
  }
}

export function extract(html: string) {
  const lines: string[] = []
  const title = decode(html.match(/<title[^>]*>([^<]*)<\/title>/i)?.[1] || "")
  for (const s of [meta(html, "og:title"), title, meta(html, "og:description"), meta(html, "description")]) if (s && !lines.includes(s)) lines.push(s)
  const facts: Record<string, unknown> = {}
  for (const m of html.matchAll(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)) {
    try { walk(JSON.parse(m[1]), facts) } catch { /* skip malformed block */ }
  }
  if (facts.price) lines.push(`AED ${facts.price}${facts.period ? " " + facts.period : ""}`)
  if (facts.beds) lines.push(`${facts.beds} Beds`)
  if (facts.size) lines.push(`${facts.size} ${/mtk|sqm|m2/i.test(String(facts.sizeUnit || "")) ? "sqm" : "sqft"}`)
  if (facts.street || facts.locality) lines.push(`Location: ${[facts.street, facts.locality].filter(Boolean).join(", ")}`)
  if (facts.name && !lines.includes(String(facts.name))) lines.push(String(facts.name))
  if (facts.description) lines.push(String(facts.description).slice(0, 1500))
  return lines.join("\n").slice(0, 8000)
}

export default async (req: Request) => {
  const target = new URL(req.url).searchParams.get("url") || ""
  let url: URL
  try { url = new URL(target) } catch { return Response.json({ ok: false, reason: "bad_link" }, { status: 400 }) }
  if (!allowed(url)) return Response.json({ ok: false, reason: "not_supported" }, { status: 400 })
  try {
    let res: Response | null = null
    for (let hop = 0; hop < 5; hop++) {
      res = await fetch(url, { redirect: "manual", signal: AbortSignal.timeout(12000), headers: { "User-Agent": "Mozilla/5.0 (compatible; TomDubaiHomes/1.0; listing link preview)", "Accept": "text/html", "Accept-Language": "en" } })
      const loc = res.headers.get("location")
      if (res.status >= 300 && res.status < 400 && loc) { const next = new URL(loc, url); if (!allowed(next)) return Response.json({ ok: false, reason: "not_supported" }); url = next; continue }
      break
    }
    if (!res || !res.ok) return Response.json({ ok: false, reason: "blocked", status: res?.status ?? 0 })
    const html = (await res.text()).slice(0, 3_000_000)
    const text = extract(html)
    if (!text.trim()) return Response.json({ ok: false, reason: "no_details" })
    return Response.json({ ok: true, url: url.toString(), text }, { headers: { "Cache-Control": "no-store" } })
  } catch {
    return Response.json({ ok: false, reason: "unreachable" })
  }
}

export const config: Config = {
  path: "/api/lookup",
  method: "GET",
  rateLimit: { action: "rate_limit", aggregateBy: ["ip", "domain"], windowSize: 60, windowLimit: 20 }
}
