import ctypes

import pytest
from raw_struct import RawStruct


def test_bitfield_1():
    class A(RawStruct):
        _pack_ = 1
        a1 = ctypes.c_uint16, 1
        a2 = ctypes.c_uint16, 2
        a3 = ctypes.c_uint16, 3
        a4 = ctypes.c_uint16, 4
        a5 = ctypes.c_uint16, 5
    a = A(a1=0xffff, a2=0, a3=0xffff, a4=0, a5=0xffff)
    s = str(a)
    assert a.size == 2
    b = a.pack()
    assert bin(b[0]) == bin(0b00111001)
    assert bin(b[1]) == bin(0b01111100)


def test_bitfield_2():
    class A(RawStruct):
        _pack_ = 1
        a1 = ctypes.c_uint8, 1
        a2 = ctypes.c_uint8, 2
        a3 = ctypes.c_uint8, 3
        a4 = ctypes.c_uint8, 4
        a5 = ctypes.c_uint8, 5
        a6 = ctypes.c_uint8, 6
        a7 = ctypes.c_uint8, 7
    a = A(a1=0xff, a2=0, a3=0xff, a4=0xff, a5=0xff, a6=0xff, a7=0xff)
    s = str(a)
    assert a.size == 5
    b = a.pack()
    assert bin(b[0]) == bin(0b00111001)
    assert bin(b[1]) == bin(0b00001111)
    assert bin(b[2]) == bin(0b00011111)
    assert bin(b[3]) == bin(0b00111111)
    assert bin(b[4]) == bin(0b01111111)

