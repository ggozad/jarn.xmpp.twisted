"""
XMPP subprotocol handler that for:
    * XMPP admin.
"""
import logging
from twisted.words.protocols.jabber.jid import JID
from wokkel import client
from wokkel.xmppim import AvailablePresence
from wokkel.pubsub import PubSubClient
from plone.messaging.twisted.protocols import AdminClient

logger = logging.getLogger('plone.messaging.twisted')


class Admin(AdminClient):
    """
    """

    def connectionInitialized(self):
        logger.info("Admin user %s has logged in" % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))
        self.sendAnnouncement('Kaka')


class PubSub(PubSubClient):
    def connectionInitialized(self):
        logger.info("Pubsub user %s has logged in" % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))
        def showRes(result):
            import pdb; pdb.set_trace( )
        d = self.createNode(JID("pubsub.localhost"), nodeIdentifier="Testing123")
        d.addCallback(showRes)

def adminClientFactory(jid, secret):
    admin = client.XMPPClient(jid, secret)
    adminHandler = Admin()
    pubsubHandler = PubSub()
    adminHandler.setHandlerParent(admin)
    pubsubHandler.setHandlerParent(admin)
    return admin
