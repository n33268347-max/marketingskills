"""Pure-Python port of PHP's mt_srand()/mt_rand() (PHP >= 7.1, MT_RAND_MT19937).

Used ONLY to reproduce draws an operator has already published, from the seed
the operator published, so the result can be independently audited. It is not
used, and must not be used, to anticipate any future draw.

Reference behaviour (php-src ext/random, formerly ext/standard/mt_rand.c):
  * mt_srand(int $seed): the seed is truncated to uint32 and the state is
    initialised with the standard MT19937 init_genrand recurrence.
  * mt_rand($min, $max): umax = max - min; draws 32-bit outputs, rejecting
    values above the largest multiple of (umax + 1) to avoid modulo bias,
    returns min + (r % (umax + 1)).
"""

from __future__ import annotations

N, M = 624, 397
MATRIX_A, UPPER, LOWER = 0x9908B0DF, 0x80000000, 0x7FFFFFFF
MASK32 = 0xFFFFFFFF


class PhpMt:
    def __init__(self, seed: int) -> None:
        self.seed(seed)

    def seed(self, seed: int) -> None:
        s = [0] * N
        s[0] = seed & MASK32
        for i in range(1, N):
            s[i] = (1812433253 * (s[i - 1] ^ (s[i - 1] >> 30)) + i) & MASK32
        self.state = s
        self.index = N  # force a reload before first output

    def _reload(self) -> None:
        s = self.state
        for i in range(N):
            y = (s[i] & UPPER) | (s[(i + 1) % N] & LOWER)
            s[i] = s[(i + M) % N] ^ (y >> 1) ^ (MATRIX_A if y & 1 else 0)
        self.index = 0

    def next_u32(self) -> int:
        if self.index >= N:
            self._reload()
        y = self.state[self.index]
        self.index += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        return y & MASK32

    def rand(self, lo: int | None = None, hi: int | None = None) -> int:
        if lo is None:
            return self.next_u32() >> 1  # mt_rand() with no args
        if hi < lo:
            raise ValueError("max < min")
        umax = hi - lo
        r = self.next_u32()
        if umax == MASK32:
            return lo + r
        umax += 1
        if umax & (umax - 1):  # not a power of two: reject to remove modulo bias
            limit = MASK32 - (MASK32 % umax) - 1
            while r > limit:
                r = self.next_u32()
        return lo + (r % umax)


def mt_rand_once(seed: int, lo: int, hi: int) -> int:
    return PhpMt(seed).rand(lo, hi)
