"""PHP 8.2+ Random extension engines, for re-computing ALREADY PUBLISHED draws.

Implements, following php-src ext/random:
  * Xoshiro256StarStar seeded from a 32-byte string (4 x little-endian uint64)
    or from an int via SplitMix64;
  * Random\\Randomizer::getInt(min, max) range reduction for ranges < 2^32
    (php_random_range32: low 32 bits of each 64-bit output, rejection sampling,
    power-of-two masking).
Used only for audit of past results; never to anticipate future draws.
"""
from __future__ import annotations

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1


def _rotl(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & M64


def splitmix64(state: list[int]) -> int:
    state[0] = (state[0] + 0x9E3779B97F4A7C15) & M64
    z = state[0]
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


class Xoshiro256StarStar:
    def __init__(self, seed: bytes | int):
        if isinstance(seed, (bytes, bytearray)):
            if len(seed) != 32:
                raise ValueError("string seed must be 32 bytes")
            self.s = [int.from_bytes(seed[i * 8:(i + 1) * 8], "little") for i in range(4)]
        else:
            st = [seed & M64]
            self.s = [splitmix64(st) for _ in range(4)]

    def next64(self) -> int:
        s = self.s
        result = (_rotl((s[1] * 5) & M64, 7) * 9) & M64
        t = (s[1] << 17) & M64
        s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t
        s[3] = _rotl(s[3], 45)
        return result


def get_int(engine, lo: int, hi: int) -> int:
    umax = hi - lo
    if umax > M32:
        raise NotImplementedError("range64 not needed for these draws")
    r = engine.next64() & M32
    if umax == M32:
        return lo + r
    umax += 1
    if umax & (umax - 1) == 0:
        return lo + (r & (umax - 1))
    limit = M32 - (M32 % umax) - 1
    while r > limit:
        r = engine.next64() & M32
    return lo + (r % umax)
