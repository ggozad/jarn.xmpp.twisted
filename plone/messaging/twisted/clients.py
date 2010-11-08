"""
XMPP subprotocol handler that for:
    * XMPP admin.
"""
import logging
from wokkel import client
from wokkel.xmppim import AvailablePresence
from plone.messaging.twisted.protocols import AdminClientProtocol

logger = logging.getLogger('plone.messaging.twisted')


class Admin(AdminClientProtocol):
    """
    """

    def __init__(self):
        pass

    def connectionInitialized(self):
        logger.info("Admin user %s has logged in" % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))

def adminClientFactory(jid, secret):
    adminClient = client.XMPPClient(jid, secret)
    adminHandler = Admin()
    adminHandler.setHandlerParent(adminClient)
    return adminClient
