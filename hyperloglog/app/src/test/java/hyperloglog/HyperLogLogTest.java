package hyperloglog;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class HyperLogLogTest {

    private static final int[] MATRIX_ROWS = {
        0x21ae4036, 0x32435171, 0xac3338cf,
        0xea97b40c, 0x0e504b22, 0x9ff9a4ef,
        0x111d014d, 0x934f3787, 0x6cd079bf,
        0x69db5c31, 0xdf3c28ed, 0x40daf2ad,
        0x82a5891c, 0x4659c7b0, 0x73dc0ca8,
        0xdad3aca2, 0x00c74c7e, 0x9a2521e2,
        0xf38eb6aa, 0x64711ab6, 0x5823150a,
        0xd13a3a9a, 0x30a5aa04, 0x0fb9a1da,
        0xef785119, 0xc9f0b067, 0x1e7dde42,
        0xdda4a7b2, 0x1a1c2640, 0x297c0633,
        0x744edb48, 0x19adce93
    };

    private int slowHash(int x) {
        int hash = 0;
        for (int i = 0; i < MATRIX_ROWS.length; i++) {
            int parity = 0;
            int row = MATRIX_ROWS[i];
            for (int bit = 0; bit < 32; bit++) {
                parity ^= ((row >>> bit) & 1) & ((x >>> bit) & 1);
            }
            hash |= parity << i;
        }
        return hash;
    }

    private int slowRho(int x) {
        if (x == 0) {
            throw new IllegalArgumentException("rho(0) is undefined");
        }
        for (int bit = 31; bit >= 0; bit--) {
            if (((x >>> bit) & 1) == 1) {
                return 32 - bit;
            }
        }
        throw new AssertionError("Input should have at least one bit set");
    }

    @Test
    public void hMatchesSlowHashForRepresentativeInputs() {
        HyperLogLog hll = new HyperLogLog();
        int[] samples = {0, 1, 42, 5000, 123456789, -1, 0x80000000};
        for (int sample : samples) {
            assertEquals(slowHash(sample), hll.h(sample));
        }
    }

    @Test(expected = IllegalArgumentException.class)
    public void rhoThrowsOnZero() {
        HyperLogLog.rho(0);
    }

    @Test
    public void rhoMatchesSlowRhoForRepresentativeInputs() {
        int[] samples = {1, 2, 3, 0x00008000, 0x7fffffff, 0x80000000, -1, -2, 123456789};
        for (int sample : samples) {
            assertEquals(slowRho(sample), HyperLogLog.rho(sample));
        }
    }
}
