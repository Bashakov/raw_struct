import ctypes

from raw_struct import RawStruct

def test_pack_same():
    class C1(RawStruct):
        c = ctypes.c_uint32

    class C2(RawStruct):
        _pack_ = 1
        c = ctypes.c_uint32

    c1 = C1(c=0x12345678)
    c2 = C2(c=0x12345678)
    assert 4 == c1.size
    assert 4 == c2.size

    assert b'\x78\x56\x34\x12' == bytes(c1)
    assert b'\x78\x56\x34\x12' == bytes(c2)

    c1 = C1.unpack(b'12345678')
    c2 = C2.unpack(b'12345678')

    assert 0x34333231 == c1.c
    assert 0x34333231 == c2.c


def test_pack_lvl():
    class P1(RawStruct):
        _pack_ = 1
        u8 = ctypes.c_uint8
        u32 = ctypes.c_uint32

    class P2(RawStruct):
        _pack_ = 2
        u8 = ctypes.c_uint8
        u32 = ctypes.c_uint32

    class P4(RawStruct):
        _pack_ = 4
        u8 = ctypes.c_uint8
        u32 = ctypes.c_uint32

    class PN(RawStruct):
        u8 = ctypes.c_uint8
        u32 = ctypes.c_uint32

    p1 = P1(u8=0x12, u32=0x3456789a)
    p2 = P2(u8=0x12, u32=0x3456789a)
    p4 = P4(u8=0x12, u32=0x3456789a)
    pn = PN(u8=0x12, u32=0x3456789a)

    assert 5 == p1.size
    assert 6 == p2.size
    assert 8 == p4.size
    assert 8 == pn.size

    assert b'\x12\x9a\x78\x56\x34' == bytes(p1)
    assert b'\x12\x00\x9a\x78\x56\x34' == bytes(p2)
    assert b'\x12\x00\x00\x00\x9a\x78\x56\x34' == bytes(p4)
    assert b'\x12\x00\x00\x00\x9a\x78\x56\x34' == bytes(pn)


def test_pack_merge():
    class P1(RawStruct):
        _pack_ = 1
        u8_1 = ctypes.c_uint8
        u32_1 = ctypes.c_uint32

    class PN(RawStruct):
        u8_n = ctypes.c_uint8
        u32_n = ctypes.c_uint32

    class PN1(PN, P1):
        pass

    class P1N(P1, PN):
        pass

    p1n = P1N(u8_n=0x11, u32_n=0x55443322, u8_1=0x66, u32_1=0xaa998877)
    pn1 = PN1(u8_n=0x11, u32_n=0x55443322, u8_1=0x66, u32_1=0xaa998877)

    assert 10 == p1n.size
    assert 10 == pn1.size

    assert b'\x66\x77\x88\x99\xaa\x11\x22\x33\x44\x55' == bytes(p1n)
    assert b'\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa' == bytes(pn1)
