import ctypes
from collections import OrderedDict

from raw_struct import RawStruct



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

    a = A((1, 2), 3)
    s = str(a)
    assert '<A: a1=(1, 2), a2=3>' == s


def test_hash():
    class S1(RawStruct):
        _pack_ = 1
        s1 = ctypes.c_uint8

    class S11(RawStruct):
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

    sc11 = S11(s1=1)
    assert hash(sc1) != hash(sc11)
    assert hash(sc2) != hash(sc11)
    assert hash(sc3) != hash(sc11)

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
