from twisted.words.protocols.jabber import component
from twisted.words.xish import domish
from zope.component import getUtility
from wokkel.subprotocols import StreamManager

from jarn.xmpp.twisted.interfaces import IZopeReactor


class XMPPComponent(StreamManager):

    def __init__(self, host, port, domain, password, extra_handlers=[]):
        self.host = host
        self.port = port

        self._state = None
        factory = component.componentFactory(domain, password)

        StreamManager.__init__(self, factory)
        for handler in extra_handlers:
            handler.setHandlerParent(self)

        self._state = u'connecting'
        zr = getUtility(IZopeReactor)
        zr.reactor.callFromThread(self.connect)

    def _authd(self, xs):
        #Set JID
        self.jid = self.xmlstream.thisEntity

        #Patch send to always include from.
        old_send = xs.send

        def send(obj):
            if domish.IElement.providedBy(obj) and \
                    not obj.getAttribute('from'):
                obj['from'] = self.jid.full()
            old_send(obj)

        xs.send = send

        StreamManager._authd(self, xs)
        self._state = u'authenticated'

    def connect(self):
        zr = getUtility(IZopeReactor)
        self._connector = zr.reactor.connectTCP(self.host,
                                                self.port,
                                                self.factory)

    def disconnect(self):
        self.xmlstream.sendFooter()
        self._connector.disconnect()

    def _connected(self, xs):
        self._state = u'connected'
        super(XMPPComponent, self)._connected(xs)

    def _disconnected(self, _):
        self._state = u'disconnected'
        super(XMPPComponent, self)._disconnected(_)

    @property
    def state(self):
        return self._state

    def initializationFailed(self, reason):
        """
        Called when stream initialization has failed.

        Disconnect the current stream and raise the exception.
        """
        self.disconnect()
        reason.raiseException()
