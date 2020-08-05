import ctypes
from collections import OrderedDict

from .utils import check_name_dup, fetch_fields, get_pack_factor
from .parse_declaration import parse_declaration


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

    def __eq__(self, another):
        if not isinstance(another, self.__class__):
            return False
        for n, t in self._fields_:
            v1 = getattr(self, n)
            v2 = getattr(another, n)
            if v1 != v2:
                return False
        return True

    def __ne__(self, another):
        return not self == another


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
    def unpack(cls, buffer, offset=None):
        if isinstance(buffer, ctypes.Structure):
            buf_size = ctypes.sizeof(buffer)
        else:
            buf_size = len(buffer)

        if offset is None:
            if buf_size != cls.size:
                raise ValueError(
                    "Unpack [%s] wrong buffer size: %d instead %d bytes" %
                    (cls.__name__, buf_size, cls.size))
            else:
                offset = 0
        else:
            assert isinstance(offset, int) and offset >= 0
            if buf_size - offset < cls.size:
                raise ValueError(
                    "Buffer size for [%s] too small: %d (offset: %d) instead of %d bytes"
                    % (cls.__name__, buf_size, offset, cls.size))
        return cls.from_buffer_copy(buffer, offset)

    @classmethod
    def iter_unpack(cls, buffer, offset=0):
        if isinstance(buffer, ctypes.Structure):
            buf_size = ctypes.sizeof(buffer)
        else:
            buf_size = len(buffer)

        for o in range(offset, buf_size - cls.size + 1, cls.size):
            yield cls.from_buffer_copy(buffer, o)


def from_declaration(declaration, pack=None):
    struct_name, fields = parse_declaration(declaration)
    attrs = dict()
    attrs['_fields_'] = fields
    if pack is not None:
        attrs['_pack_'] = pack
    cls = type(struct_name, (RawStruct, ), attrs)
    return cls
