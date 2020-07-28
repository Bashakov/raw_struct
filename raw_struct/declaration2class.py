import ctypes

from .parse_declaration import parse_declaration

_ctype_array = type(ctypes.c_char*2)


def declaration2class(declaration, pack=None):
    ofs = '    '
    struct_name, fields = parse_declaration(declaration)
    res = ['class %s(RawStruct)' % struct_name]
    if pack:
        res.append('%s_pack_ = %d' % (ofs, pack))
    for name, tp in fields:
        str_type = ''
        if isinstance(tp, _ctype_array):
            str_type = "%s * %d" % (tp._type_.__name__, tp._length_)
        else:
            str_type = tp.__name__
        res.append('%s%s = ctypes.%s' % (ofs, name, str_type))
    text = '\n'.join(res)
    return text
