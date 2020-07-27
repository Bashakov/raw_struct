import ctypes
from collections import OrderedDict

_type_ctype_elem = type(ctypes.c_uint8)
_type_ctype_arry = type(ctypes.c_uint8 * 2)


def _fetch_fields_from_bases(bases):
    """ собираем все поля с родительских классов """
    fields = []
    for base in bases:
        cur_fields = getattr(base, '_fields_', [])
        for n, t in cur_fields:
            fields.append((n, t))
    return fields


def _check_name_dup(struct_name, fields):
    """ проверяем на дублирование имен атрибутов """
    s = set()
    for n, v in fields:
        if n in s:
            raise TypeError('Struct [%s], duplicate [%s]' % (struct_name, n))
        s.add(n)


def _to_dict(obj):
    """ конвертация объекта в словарь """
    res = OrderedDict()
    for n, t in obj._fields_:
        v = getattr(obj, n)
        if not isinstance(v, bytes) and isinstance(t, _type_ctype_arry):
            v = tuple(v)
        res[n] = v
    return res


def _get_hash(struct_name):
    """ генерация хеша для структуры """
    def wrapper(obj):
        return hash(bytes(obj)) ^ hash(struct_name)

    return wrapper


def _get_str(name):
    """ генерация строкового описания структуры """
    def wrapper(obj):
        values = ('%s=%s' % (n, v) for n, v in obj.to_dict().items())
        return '<%s: %s>' % (name, ', '.join(values))

    return wrapper


def _get_pack_factor(bases, attrs):
    """ вычисление варианта выравнивания структуры """
    pack_byte = attrs.get('_pack_')
    for base in bases:
        cur_pack = getattr(base, '_pack_', None)
        if cur_pack:
            pack_byte = pack_byte and min(cur_pack, pack_byte) or cur_pack
    return pack_byte


class MetaRawStruct(type(ctypes.Structure)):
    """ 
    Метакласс для структур, отображаемых в память
    """
    def __new__(meta, name, bases, attrs):
        fields = _fetch_fields_from_bases(bases)
        pack_byte = _get_pack_factor(bases, attrs)

        for n, t in attrs.items():
            if isinstance(t, (_type_ctype_elem, _type_ctype_arry)):
                fields.append((n, t))
        for n, t in fields:
            if n in attrs:
                del attrs[n]
        _check_name_dup(name, fields)

        attrs['_fields_'] = fields
        if pack_byte:
            attrs['_pack_'] = pack_byte

        cls = super().__new__(meta, name, (ctypes.Structure, ), attrs)

        cls.size = ctypes.sizeof(cls)
        cls.unpack = cls.from_buffer_copy
        cls.to_dict = _to_dict
        cls.__hash__ = _get_hash(name)
        cls.__str__ = _get_str(name)
        return cls

    @classmethod
    def __prepare__(metacls, cls, bases):
        return OrderedDict(
        )  # till python 3.5 dict has no order, use OrderedDict for hold field definition order


class RawStruct(metaclass=MetaRawStruct):
    """ структура, от которой следует наследоваться, 
        для получения структуры отображаемой в память 
    """

    pass
