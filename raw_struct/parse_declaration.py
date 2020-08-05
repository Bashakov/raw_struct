import re
import ctypes

_ctype_array = type(ctypes.c_char * 2)

_type2ctype = {
    'char': ctypes.c_char,
    'unsigned char': ctypes.c_char,
    'BYTE': ctypes.c_ubyte,

    'short': ctypes.c_int16,
    'SHORT': ctypes.c_int16,
    'WORD': ctypes.c_uint16,

    'int': ctypes.c_int,
    'long': ctypes.c_int,
    'LONG': ctypes.c_int,
    'DWORD': ctypes.c_uint,
    'BOOL': ctypes.c_uint,

    '__int64': ctypes.c_longlong,
}

_spec_types = {
    'GUID': ('char', 16)
}


def parse_declaration(declaration):
    p = re.match(r'\s*(?:class|struct)\s+(?P<name>\w+)\s*{(?P<items>[^}]+)}\s*;+', declaration)
    if not p:
        raise Exception("bad struct definition:" + declaration)
    struct_name = p.group('name')

    line_pattern = '\s*(?P<type>\w+)\s+(?P<name>\w+)\s*(?:\[(?P<count>\d+)\])?\s*;'
    fields = []
    for g in re.finditer(line_pattern, p.group('items')):
        field_name, field_type, item_count = g.group('name', 'type', 'count')

        if field_type in _spec_types:
            field_type, item_count = _spec_types[field_type]
        field_type = _type2ctype[field_type]
        if item_count:
            field_type = field_type * int(item_count)
        fields.append((field_name, field_type))
    return struct_name, fields


def from_c_to_python_declaration(declaration, pack=None):
    """построить класс на основе определения С/С++

    Args:
        declaration (str): определение класс или структуры
        pack (int, optional): параметр упаковки в памяти. Defaults to None.

    Returns:
        str: строка с описанием класса Python
    """
    ofs = '    '
    struct_name, fields = parse_declaration(declaration)
    res = ['class %s(RawStruct):' % struct_name]
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
