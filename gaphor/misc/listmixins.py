"""
This module contains some support code for queries on lists.

Two mixin classes are provided:

1. ``querymixin``
2. ``recursemixin``

See the documentation on the mixins.

"""

__all__ = [ 'querymixin', 'recursemixin' ]


def match(element, expr):
    """
    Returns True if the expression returns True.
    The context for the expression is the element.

    Given a class:

    >>> class A(object):
    ...     def __init__(self, name): self.name = name

    We can create a path for each object:

    >>> a = A('root')
    >>> a.a = A('level1')
    >>> a.b = A('b')
    >>> a.a.text = 'help'

    If we want to match, ``it`` is used to refer to the subjected object:

    >>> match(a, 'it.name=="root"')
    True
    >>> match(a, 'it.b.name=="b"')
    True
    >>> match(a, 'it.name=="blah"')
    False
    >>> match(a, 'it.nonexistent=="root"')
    False

    """
    g = { 'it': element }

    try:
        return eval(expr, g, {})
    except (AttributeError, NameError):
        # attribute does not (yet) exist
        #print 'No attribute', expr, d
        return False


class Matcher(object):

    def __init__(self, expr):
        self.expr = expr

    def __call__(self, element):
        return match(element, self.expr)


class querymixin(object):
    """
    Implementation of the matcher as a mixin for lists.

    Given a class:

    >>> class A(object):
    ...     def __init__(self, name): self.name = name

    We can do nice things with this list:

    >>> class MList(querymixin, list):
    ...     pass
    >>> m = MList()
    >>> m.append(A('one'))
    >>> m.append(A('two'))
    >>> m.append(A('three'))
    >>> m[1].name
    'two'
    >>> m['it.name=="one"'] # doctest: +ELLIPSIS
    [<gaphor.misc.listmixins.A object at 0x...>]
    >>> m['it.name=="two"', 0].name
    'two'
    """

    def __getitem__(self, key):
        try:
            # See if the list can deal with it (don't change default behaviour)
            return super(querymixin, self).__getitem__(key)
        except TypeError:
            # Nope, try our matcher trick
            if type(key) is tuple:
                key, remainder = key[0], key[1:]
            else:
                remainder = None

            matcher = Matcher(key)
            matched = filter(matcher, self)
            if remainder:
                return type(self)(matched).__getitem__(*remainder)
            else:
                return type(self)(matched)


def issafeiterable(obj):
    """
    Checks if the object is iteable, but not a string.
    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, basestring)


class recurseproxy(object):
    """
    Proxy object (helper) for the recusemixin.
    """

    def __init__(self, sequence, key=None):
        self.__sequence = sequence
        self.__key = key

    def list_class(self):
        return list

    def __getitem__(self, key):
        return self.list_class()(self).__getitem__(key)

    def __iter__(self):
        """
        Iterate over the items. If there is some level of nesting, the parent
        items are iterated as well.
        """
        key = self.__key
        sequence = self.__sequence
        if key is None:
            # top level - always iterate
            for e in sequence:
                #print 'root element', e
                yield e
        else:
            for e in sequence:
                try:
                    obj = getattr(e, key)
                except AttributeError:
                    pass # No such attribute, just fetch the next
                else:
                    # Either flatten or return the value as is.
                    if issafeiterable(obj):
                        for o in obj:
                            yield o
                    else:
                        yield obj


    def __getattr__(self, key):
        """
        Create a new proxy for the attribute.
        """
        return type(self)(self, key)


class recursemixin(object):
    """
    Mixin class for lists, sets, etc. If data is requested using ``[:]``,
    a ``recurseproxy`` instance is created.

    The basic idea is you have a class that can contain children:

    >>> class A(object):
    ...     def __init__(self, name, *children):
    ...         self.name = name
    ...         self.children = list(children)
    ...     def dump(self, level=0):
    ...         print ' ' * level, self.name
    ...         for c in self.children: c.dump(level+1)

    Now if we make a (complex) structure out of it:

    >>> a = A('root', A('a', A('b'), A('c'), A('d')), A('e', A('one'), A('two')))
    >>> a.dump()   # doctest: +ELLIPSIS
     root
      a
       b
       c
       d
      e
       one
       two
    >>> a.children[1].name
    'e'

    Given ``a``, I want to iterate all grand-children (b, c, d, one, two) and the
    structure I want to do that with is:

      ``a.children[:].children``

    In order to do this we have to use a special list class, so we can handle our
    specific case. ``__getslice__`` should be overridden, so we can make it behave
    like a normal python object (legacy, yes...).

    >>> import sys
    >>> class rlist(recursemixin, list):
    ...     def __getslice__(self, a, b, c=None):
    ...         if a == 0: a = None
    ...         if b == sys.maxint: b = None
    ...         return self.__getitem__(slice(a, b, c))

    >>> class A(object):
    ...     def __init__(self, name, *children):
    ...         self.name = name
    ...         self.children = rlist(children)
    ...     def dump(self, level=0):
    ...         print ' ' * level, self.name
    ...         for c in self.children: c.dump(level+1)

    >>> a = A('root', A('a', A('b'), A('c'), A('d')), A('e', A('one'), A('two')))
    >>> a.children[1].name
    'e'

    Invoking ``a.children[:]`` should now return a recurseproxy object:

    >>> a.children[:]                                       # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(a.children[:].name)                            # doctest: +ELLIPSIS
    ['a', 'e']

    Now calling a child on the list will return a list of all children:

    >>> a.children[:].children                              # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(a.children[:].children)                        # doctest: +ELLIPSIS
    [<gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>]

    And of course we're interested in the names:

    >>> a.children[:].children.name                         # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(a.children[:].children.name)
    ['b', 'c', 'd', 'one', 'two']
    """
    _recursemixin_trigger = slice(None, None, None)
    #_recurse_mixin_root = object()

    def proxy_class(self):
        return recurseproxy

    def __getitem__(self, key):
        if key == self._recursemixin_trigger:
            return self.proxy_class()(self, None)
        else:
            return super(recursemixin, self).__getitem__(key)


# vim: sw=4:et:ai
