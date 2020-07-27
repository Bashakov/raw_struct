import ctypes

import pytest
from raw_struct import RawStruct


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