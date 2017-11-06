# coding=utf-8

class SingletonMetaclass(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):

        result = None

        instances = cls.__class__._instances

        if cls in instances:

            result = instances[cls]

        else:

            result = instances[cls] = super().__call__(*args, **kwargs)

        return result


class SubclassMetaclass(type):

    _baseclasses = []

    def __new__(mcs, name, bases, attrs):

        subclass = r'.'.join([attrs[r'__module__'], attrs[r'__qualname__']])

        for base in bases:

            if base in mcs._baseclasses:

                base._subclasses.append(subclass)

            else:

                mcs._baseclasses.append(base)

                setattr(base, r'_subclasses', [subclass])

        return type.__new__(mcs, name, bases, attrs)
