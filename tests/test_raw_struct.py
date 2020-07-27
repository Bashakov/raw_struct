import ctypes
import pytest

from raw_struct import RawStruct


def test_simple():
    class A(RawStruct):
        a1 = ctypes.c_uint32
        a2 = ctypes.c_uint8

    assert A.size == 8
    a = A(a1=0x11223344, a2=0x55)
    assert a.size == 8
    b = a.pack()
    assert b'\x44\x33\x22\x11' == b[0:4]
    assert b'\x55' == b[4:5]
    c = A.unpack(b'\xaa\xbb\xcc\xdd\xee\xff\x11\x22\x33')
    assert c.a1 == 0xddccbbaa
    assert c.a2 == 0xee


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
