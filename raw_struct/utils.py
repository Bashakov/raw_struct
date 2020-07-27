import ctypes


_ctype_types = type(ctypes.c_uint8), type(ctypes.c_uint8 * 2)  # element, array


def fetch_fields(bases, attrs):
    """ собрать описание полей из базовых классов и атрибутов """
    fields = []
    for base in bases:
        fields.extend(getattr(base, '_fields_', []))
        for n, v in base.__dict__.items():
            if callable(v) or isinstance(v, classmethod):
                attrs[n] = v

    for n, t in attrs.items():
        if isinstance(t, _ctype_types):
            fields.append((n, t))
    for n, t in fields:
        if n in attrs:
            del attrs[n]
    return fields


def check_name_dup(struct_name, fields):
    """ проверяем на дублирование имен атрибутов """
    s = set()
    for n, v in fields:
        if n in s:
            raise TypeError('Struct [%s], duplicate [%s]' % (struct_name, n))
        s.add(n)


def get_pack_factor(bases, attrs):
    """ вычисление варианта выравнивания структуры """
    pack_byte = attrs.get('_pack_')
    for base in bases:
        cur_pack = getattr(base, '_pack_', None)
        if cur_pack:
            pack_byte = pack_byte and min(cur_pack, pack_byte) or cur_pack
    return pack_byte