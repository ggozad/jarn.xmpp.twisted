from zope.interface import Interface, implements
from zope.component.interfaces import IObjectEvent


class IZopeReactor(Interface):
    """Initializes and provides the twisted reactor.
    """
    pass


class IReactorStarted(IObjectEvent):
    """Reactor has been started.
    """
    pass


class ReactorStarted(object):
    implements(IReactorStarted)

    def __init__(self, obj):
        self.object = obj


class IReactorStoped(IObjectEvent):
    """Reactor has been stoped.
    """
    pass


class ReactorStoped(object):
    implements(IReactorStoped)

    def __init__(self, obj):
        self.object = obj
