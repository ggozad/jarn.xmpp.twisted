import random
import string
import logging
from zope.interface import implements
from zope.component import queryUtility
from wokkel import client
from wokkel.xmppim import AvailablePresence
from wokkel.pubsub import PubSubClient
from plone.messaging.twisted.protocols import AdminHandler, ChatHandler
from plone.messaging.twisted.interfaces import IJabberClient
from plone.messaging.twisted.interfaces import IZopeReactor

logger = logging.getLogger('plone.messaging.twisted')


class Admin(AdminHandler):

    def connectionInitialized(self):
        logger.info("Admin user %s has logged in." %
            self.xmlstream.factory.authenticator.jid.full())

    def connectionLost(self, reason):
        logger.info("Admin user %s has logged out." %
            self.xmlstream.factory.authenticator.jid.full())


class Chatter(ChatHandler):

    def connectionInitialized(self):
        logger.info("User %s has logged in." %
            self.xmlstream.factory.authenticator.jid.full())

    def connectionLost(self, reason):
        logger.info("User %s has logged out." %
            self.xmlstream.factory.authenticator.jid.full())


class PubSub(PubSubClient):

    def connectionInitialized(self):
        logger.info("Pubsub user %s has logged in" %
            self.xmlstream.factory.authenticator.jid.full())


class JabberClient(object):

    implements(IJabberClient)

    def execute(self, jid, password,
                callback, extra_handlers=[], errback=None):

        chars = string.letters + string.digits
        resource = 'auto-' + ''.join([random.choice(chars) for i in range(10)])
        jid.resource=resource

        factory = client.DeferredClientFactory(jid, password)
        for handler in extra_handlers:
            handler.setHandlerParent(factory.streamManager)

        d = client.clientCreator(factory)

        def disconnect(result):
            factory.streamManager.xmlstream.sendFooter()
            factory.streamManager.xmlstream.transport.connector.disconnect()
            return result

        def defaultErrBack(error_stanza):
            logger.error(error_stanza.getErrorMessage())
            logger.error("StanzaError: %s" % error_stanza.value.stanza.toXml())

        d.addCallback(callback)
        d.addCallback(disconnect)
        if errback:
            d.addErrback(errback)
        else:
            d.addErrback(defaultErrBack)

        zr = queryUtility(IZopeReactor)
        if zr:
            zr.reactor.callFromThread(zr.reactor.connectTCP, "localhost", 5222, factory)
        return d
