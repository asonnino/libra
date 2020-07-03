address 0x42 {
module M {
    const NO: u8 = {
        (1: u8) << 8;
        (1: u64) << 64;
        (1: u128) << 128;

        (0: u8) >> 8;
        (0: u64) >> 64;
        (0: u128) >> 128;

        (1: u8) / 0;
        (1: u64) / 0;
        (1: u128) / 0;

        (1: u8) % 0;
        (1: u64) % 0;
        (1: u128) % 0;

        (255: u8) + 255;
        (18446744073709551615: u64) + 18446744073709551615;
        (340282366920938463463374607431768211450: u128) + 340282366920938463463374607431768211450;

        (0: u8) - 1;
        (0: u64) - 1;
        (0: u128) - 1;

        ((256: u64) as u8);
        ((340282366920938463463374607431768211450: u128) as u64);

        0
    };
}
}
