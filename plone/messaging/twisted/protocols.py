"""
XMPP Ping.

The XMPP Service Administration protocol is documented in
U{XEP-0133<http://xmpp.org/extensions/xep-0133.html>}.
"""

from zope.interface import implements

from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber.xmlstream import IQ, toResponse

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import disco, iwokkel

NS_COMMANDS = 'http://jabber.org/protocol/commands'
NODE_ADMIN = 'http://jabber.org/protocol/admin'
ADMIN_REQUEST = "/iq[@type='get' or @type='set']" \
                "/command[@xmlns='%s' and @node='/%s']" % (NS_COMMANDS, NODE_ADMIN)

class AdminClientProtocol(XMPPHandler):
    """
    Admin client.

    This handler implements the protocol for sending out XMPP admin requests.
    """

class AdminHandler(XMPPHandler):
    """
    Admin responder.

    This handler executes XMPP admin commands.
    """

    implements(iwokkel.IDisco)

    def connectionInitialized(self):
        """
        Called when the XML stream has been initialized.

        This sets up an observer for incoming admin command requests.
        """
        self.xmlstream.addObserver(ADMIN_REQUEST, self.onAdminCommand)


    def onAdminCommand(self, iq):
        """
        Called when an admin command request has been received.

        It does stuff.
        """
        response = toResponse(iq, 'result')
        self.xmlstream.send(response)
        iq.handled = True


    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        """
        Get identity and features from this entity, node.

        This handler supports XMPP Ping, but only without a nodeIdentifier
        specified.
        """
        if not nodeIdentifier:
            return [disco.DiscoFeature(NS_COMMANDS)]
        else:
            import pdb; pdb.set_trace( )
            return []


    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        """
        Get contained items for this entity, node.

        This handler does not support items.
        """
        import pdb; pdb.set_trace( )
        return []


