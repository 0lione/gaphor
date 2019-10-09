"""Support for actions in generic files.

"""

from typing import Optional, Sequence, get_type_hints
import platform

from gaphor.application import Application


_primary = "⌘" if platform.system() == "Darwin" else "Ctrl"


def primary():
    global _primary
    return _primary


class action:
    """
    Decorator. Turns a regular function (/method) into a full blown
    Action class.

    >>> class A:
    ...     @action(name="my_action", label="my action")
    ...     def myaction(self):
    ...         print('action called')
    >>> a = A()
    >>> a.myaction()
    action called
    >>> is_action(a.myaction)
    True
    >>> for method in dir(A):
    ...     if is_action(getattr(A, method, None)):
    ...         print(method)
    myaction
    >>> A.myaction.__action__.name
    'my_action'
    >>> A.myaction.__action__.label
    'my action'
    """

    def __init__(
        self,
        name,
        label=None,
        tooltip=None,
        icon_name=None,
        shortcut=None,
        state=None,
        **kwargs,
    ):
        self.scope, self.name = name.split(".", 2) if "." in name else ("win", name)
        self.label = label
        self.tooltip = tooltip
        self.icon_name = icon_name
        self.shortcut = shortcut
        self.state = state
        self.arg_type = None
        self.__dict__.update(kwargs)

    def __call__(self, func):
        type_hints = get_type_hints(func)
        if len(type_hints) == 1:
            # assume the first argument (exclusing self) is our parameter
            self.arg_type = next(iter(type_hints.values()))
        func.__action__ = self
        return func


class radio_action(action):
    """
    Radio buttons take a list of names, a list of labels and a list of
    tooltips (and optionally, a list of icon names).
    The callback function should have an extra value property, which is
    given the index number of the activated radio button action.
    """

    names: Sequence[str]
    labels: Sequence[Optional[str]]
    tooltips: Sequence[Optional[str]]
    icon_names: Sequence[Optional[str]]
    shortcuts: Sequence[Optional[str]]
    active: int

    def __init__(
        self,
        names,
        labels=None,
        tooltips=None,
        icon_names=None,
        shortcuts=None,
        active=0,
    ):
        super().__init__(
            names[0],
            names=names,
            labels=labels,
            tooltips=tooltips,
            icon_names=icon_names,
            shortcuts=shortcuts,
            active=active,
        )


def is_action(func):
    return hasattr(func, "__action__")


def build_action_group(obj, name=None):
    """
    Build actions and a Gtk.ActionGroup for each Action instance found in obj()
    (that's why Action is a class ;) ). This function requires GTK+.
    """
    from gi.repository import Gtk

    group = Gtk.ActionGroup.new(name or str(obj))
    objtype = type(obj)

    for attrname in dir(obj):
        try:
            # Fetch the methods from the object's type instead of the object
            # itself. This prevents some descriptors from executing.
            # Otherwise stuff like dependency resolving may kick in
            # too early.
            method = getattr(objtype, attrname)
        except:
            continue
        act = getattr(method, "__action__", None)
        if isinstance(act, radio_action):
            actgroup = None
            if not act.labels:
                act.labels = [None] * len(act.names)
            if not act.tooltips:
                act.tooltips = [None] * len(act.names)
            if not act.icon_names:
                act.icon_names = [None] * len(act.names)
            if not act.shortcuts:
                act.shortcuts = [None] * len(act.names)
            assert len(act.names) == len(act.labels)
            assert len(act.names) == len(act.tooltips)
            assert len(act.names) == len(act.icon_names)
            assert len(act.names) == len(act.shortcuts)
            for i, n in enumerate(act.names):
                gtkact = Gtk.RadioAction.new(
                    n, act.labels[i], act.tooltips[i], None, value=i
                )
                if act.icon_name:
                    gtkact.set_icon_name(act.icon_names[i])

                if not actgroup:
                    actgroup = gtkact
                else:
                    gtkact.props.group = actgroup
                group.add_action_with_accel(gtkact, act.shortcuts[i])

            assert actgroup
            actgroup.connect("changed", _radio_action_changed, obj, attrname)
            actgroup.set_current_value(act.active)

        elif isinstance(act, action):
            gtkact = Gtk.Action.new(act.name, act.label, act.tooltip, None)
            if act.icon_name:
                gtkact.set_icon_name(act.icon_name)
            gtkact.connect("activate", _action_activate, obj, attrname)
            group.add_action_with_accel(gtkact, act.shortcut)

        elif act is not None:
            raise TypeError(f"Invalid action type: {action}")
    return group


def _action_activate(action, obj, name):
    method = getattr(obj, name)
    method()


def _toggle_action_activate(action, obj, name):
    method = getattr(obj, name)
    method(action.props.active)


def _radio_action_changed(action, current_action, obj, name):
    method = getattr(obj, name)
    method(current_action.props.value)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
