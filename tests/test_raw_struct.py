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
    c = A.unpack(b'\xaa\xbb\xcc\xdd\xee\xff\x11\x22\x33', offset=0)
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


def test_eq():
    class A(RawStruct):
        f = ctypes.c_uint32

    class B(RawStruct):
        f = ctypes.c_uint32

    a1 = A(1)
    a2 = A(2)
    a11 = A(1)
    b1 = B(1)
    assert a1 != a2
    assert a1 == a11
    assert a1 != b1
    assert bytes(a1) == bytes(a11)
    assert bytes(a1) == bytes(b1)
    assert bytes(a1) != bytes(a2)


def test_unpack_offset():
    class A(RawStruct):
        v = ctypes.c_uint16

    with pytest.raises(ValueError):
        A.unpack(b'1')
    with pytest.raises(ValueError):
        A.unpack(b'123')

    with pytest.raises(ValueError):
        A.unpack(b'1', offset=0)
    with pytest.raises(ValueError):
        A.unpack(b'12', offset=1)

    b = b'\x12\x34\x56\x78\x90'
    assert A.unpack(b[:2]).v == 0x3412
    assert A.unpack(b, offset=0).v == 0x3412
    assert A.unpack(b, offset=1).v == 0x5634
    assert A.unpack(b, offset=2).v == 0x7856
    assert A.unpack(b, offset=3).v == 0x9078


def test_iter_unpack():
    b = b'\x12\x34\x56\x78\x90'

    class A(RawStruct):
        v = ctypes.c_uint16

    assert [o.v for o in A.iter_unpack(b)] == [0x3412, 0x7856]
    assert [o.v for o in A.iter_unpack(b, offset=0)] == [0x3412, 0x7856]
    assert [o.v for o in A.iter_unpack(b, offset=1)] == [0x5634, 0x9078]
    assert [o.v for o in A.iter_unpack(b, offset=2)] == [0x7856]
    assert [o.v for o in A.iter_unpack(b, offset=3)] == [0x9078]
    assert [o.v for o in A.iter_unpack(b, offset=4)] == []