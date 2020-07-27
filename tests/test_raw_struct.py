import ctypes
from collections import OrderedDict
import pytest
from raw_struct import RawStruct


def test_pack():
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


def test_derived():
    class A(RawStruct):
        a1 = ctypes.c_uint8
        a2 = ctypes.c_uint8

    class B(A):
        b1 = ctypes.c_uint8
        b2 = ctypes.c_uint8

    a = A(a1=0x12, a2=0x34)
    b = B(a1=0x56, a2=0x78, b1=0x9a, b2=0xbc)
    assert 2 == a.size
    assert 4 == b.size
    assert b'\x12\x34' == bytes(a)
    assert b'\x56\x78\x9a\xbc' == bytes(b)
    a = A.unpack(b)
    assert 0x56 == a.a1
    assert 0x78 == a.a2


def test_check_dup():
    class A(RawStruct):
        a1 = ctypes.c_uint8
        a2 = ctypes.c_uint8

    class B(A):
        b1 = ctypes.c_uint8
        b2 = ctypes.c_uint8

    with pytest.raises(TypeError):
        class C(B):
            a1 = ctypes.c_uint16


def test_bo():
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


def test_hash():
    class S1(RawStruct):
        _pack_ = 1
        s1 = ctypes.c_uint8

    class S2(RawStruct):
        _pack_ = 1
        s2 = ctypes.c_uint32

    class S3(S1, S2):
        _pack_ = 1

    class CI(RawStruct):
        _pack_ = 1
        id = ctypes.c_uint8
        line_count = ctypes.c_uint16
        len_point = ctypes.c_float
        inner = ctypes.c_uint8

    sc1 = S1(s1=1)
    sc2 = S1(s1=2)
    sc3 = S1(s1=1)
    assert hash(sc1) == hash(sc3)
    assert hash(sc1) != hash(sc2)

    ci1 = CI(line_count=1, len_point=10.0)
    ci2 = CI(line_count=1, len_point=10.01)
    ci3 = CI(line_count=2, len_point=10.0)
    ci4 = CI(line_count=1, len_point=10.0)
    assert hash(ci1) == hash(ci4)
    assert hash(ci1) != hash(ci2)
    assert hash(ci1) != hash(ci3)
    assert hash(ci2) != hash(ci3)

    sci0 = S3(s1=1, s2=1)
    sci1 = S3(s1=1, s2=2)
    sci2 = S3(s1=2, s2=1)
    sci3 = S3(s1=1, s2=1)
    assert hash(sci1) != hash(sci2)
    assert hash(sci1) != hash(sci3)
    assert hash(sci2) != hash(sci3)
    assert hash(sci0) == hash(sci3)


def test_array():
    class A(RawStruct):
        a1 = ctypes.c_uint8 * 4
        a2 = ctypes.c_uint8

    a = A((1, 2, 3, 4), 5)
    assert 5 == a.size
    assert 1 == a.a1[0]
    assert 2 == a.a1[1]
    assert 3 == a.a1[2]
    assert 4 == a.a1[3]
    assert 5 == a.a2
    assert b'\x01\x02\x03\x04\x05' == bytes(a)


def test_to_dicts():
    class A(RawStruct):
        a1 = ctypes.c_uint16 * 4
        a2 = ctypes.c_uint8
        a3 = ctypes.c_char * 6

    a = A((1, 2, 3, 4), 5, b'test')
    d = a.to_dict()
    assert OrderedDict(a1=(1, 2, 3, 4), a2=5, a3=b'test') == d


def test_to_string():
    class A(RawStruct):
        a1 = ctypes.c_uint8 * 2
        a2 = ctypes.c_uint8
    a = A((1,2),3)
    s = str(a)
    assert '<A: a1=(1, 2), a2=3>' == s


def test_pack_merge():
    class P1(RawStruct):
        _pack_ = 1
        u8_1 = ctypes.c_uint8
        u32_1 = ctypes.c_uint32

    class PN(RawStruct):
        u8_n = ctypes.c_uint8
        u32_n = ctypes.c_uint32

    class PN1(PN, P1): pass
    class P1N(P1, PN): pass

    p1n = P1N(u8_n=0x11, u32_n=0x55443322, u8_1=0x66, u32_1=0xaa998877)
    pn1 = PN1(u8_n=0x11, u32_n=0x55443322, u8_1=0x66, u32_1=0xaa998877)

    assert 10 == p1n.size
    assert 10 == pn1.size

    assert b'\x66\x77\x88\x99\xaa\x11\x22\x33\x44\x55' == bytes(p1n)
    assert b'\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa' == bytes(pn1)
