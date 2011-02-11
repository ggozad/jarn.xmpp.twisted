from zope.component.interfaces import IObjectEvent
from zope.interface import Interface, implements


class IZopeReactor(Interface):
    """Initializes and provides the twisted reactor.
    """
    pass


class IDeferredXMPPClient(Interface):
    """ Marker interface for the DeferredXMPPClient utility.
    """


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
