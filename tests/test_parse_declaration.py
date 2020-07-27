import ctypes
from ctypes import windll

import pytest

from raw_struct.parse_declaration import parse_declaration
from raw_struct import RawStruct


def test_t1():
    struct_name, fields = parse_declaration(''' 
    struct Test
    {
        LONG    id;
        char    name[4];
        DWORD   x[3];
        GUID    g;
    }; ''')
    assert struct_name == 'Test'
    assert len(fields) == 4
    assert fields[0] == ('id', ctypes.c_long)
    assert fields[1] == ('name', ctypes.c_char*4)
    assert fields[2] == ('x', ctypes.c_ulong * 3)
    assert fields[3] == ('g', ctypes.c_char * 16)


def test_failed():
    with pytest.raises(Exception):
        parse_declaration('struct Test { LONG id; }')
    with pytest.raises(Exception):
        parse_declaration('struc1t Test { LONG id; };')
    with pytest.raises(Exception):
        parse_declaration('struct Test  LONG id; };')
    with pytest.raises(Exception):
        parse_declaration('struct Test { LONG id; ;')


def test_class():
    Cls = RawStruct.from_declaration(''' 
        struct Test
        {
            LONG    id;
            char    name[4];
            DWORD   x[3];
            GUID    g;
        };''', 1)
    assert Cls.size == 36
    i = Cls(id=1, name = b'1234', x=(10, 20), g=b'1234567890abcdef')
    assert i.size == 36
    assert i.id == 1
    assert i.name == b'1234'
    assert tuple(i.x) == (10, 20, 0)
    assert i.g == b'1234567890abcdef'
    blob = bytes(i)
    assert len(blob) == 36
    assert blob[0:4] == b'\x01\x00\x00\x00'
    assert blob[4:8] == b'1234'
    assert blob[8:20] == b'\x0a\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00'
    assert blob[20:36] == b'1234567890abcdef'

    j = Cls.unpack(blob)

    i.id == 11
    i.name = b'4321'
    i.x = (11, 22, 33)
    i.g = b'90abcdef12345678'

    assert j.size == 36
    assert j.id == 1
    assert j.name == b'1234'
    assert tuple(j.x) == (10, 20, 0)
    assert j.g == b'1234567890abcdef'