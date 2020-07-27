import ctypes
from collections import OrderedDict

from .utils import check_name_dup, fetch_fields, get_pack_factor


class MetaRawStruct(type(ctypes.Structure)):
    """ 
    Метакласс для структур, отображаемых в память
    """
    def __new__(meta, name, bases, attrs):
        pack_byte = get_pack_factor(bases, attrs)
        fields = fetch_fields(bases, attrs)
        check_name_dup(name, fields)

        attrs['_fields_'] = fields
        if pack_byte:
            attrs['_pack_'] = pack_byte

        cls = super().__new__(meta, name, (ctypes.Structure, ), attrs)

        cls.size = ctypes.sizeof(cls)
        return cls

    @classmethod
    def __prepare__(metacls, cls, bases):
        # till python 3.5 dict has no order, use OrderedDict for hold field definition order
        return OrderedDict()


class RawStruct(metaclass=MetaRawStruct):
    """ структура, от которой следует наследоваться, 
        для получения структуры отображаемой в память 
    """
    pass

    def __hash__(self):
        struct_name = self.__class__.__name__
        return hash(bytes(self)) ^ hash(struct_name)

    def __str__(self):
        struct_name = self.__class__.__name__
        values = ('%s=%s' % (n, v) for n, v in self.to_dict().items())
        return '<%s: %s>' % (struct_name, ', '.join(values))

    def to_dict(self):
        type_ctype_arry = type(ctypes.c_uint8 * 2)
        res = OrderedDict()
        for n, t in self._fields_:
            v = getattr(self, n)
            if not isinstance(v, bytes) and isinstance(t, type_ctype_arry):
                v = tuple(v)
            res[n] = v
        return res

    def pack(self):
        return bytes(self)

    @classmethod
    def unpack(cls, buf):
        return cls.from_buffer_copy(buf)
