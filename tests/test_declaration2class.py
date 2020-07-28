from raw_struct.declaration2class import declaration2class


def test_d2c():
    decl = ''' 
    struct Test
    {
        LONG    id;
        char    name[4];
        DWORD   x[3];
        GUID    g;
    }; '''
    expt = '''\
class Test(RawStruct)
    _pack_ = 2
    id = ctypes.c_long
    name = ctypes.c_char * 4
    x = ctypes.c_ulong * 3
    g = ctypes.c_char * 16'''

    text = declaration2class(decl, pack=2)
    # print(text)
    assert text == expt
