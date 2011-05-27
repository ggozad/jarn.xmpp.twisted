import unittest2 as unittest

from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import IQ

from jarn.xmpp.twisted.client import DeferredXMPPClient
from jarn.xmpp.twisted.client import XMPPClient
from jarn.xmpp.twisted.testing import REACTOR_INTEGRATION_TESTING
from jarn.xmpp.twisted.testing import wait_on_deferred
from jarn.xmpp.twisted.testing import wait_for_client_state

NS_VERSION = 'jabber:iq:version'


class ClientNetworkTest(unittest.TestCase):

    layer = REACTOR_INTEGRATION_TESTING
    level = 2

    def test_deferred_client(self):

        def getVersion(xmlstream):
            iq = IQ(xmlstream, 'get')
            iq.addElement((NS_VERSION, 'query'))
            d = iq.send('localhost')
            return d

        client = DeferredXMPPClient()
        d = client.execute(JID('admin@localhost'), 'admin', 'localhost', getVersion)
        self.assertTrue(wait_on_deferred(d))
        self.assertEqual(d.result['type'], 'result')

    def test_client(self):

        def getVersion(xmlstream):
            iq = IQ(xmlstream, 'get')
            iq.addElement((NS_VERSION, 'query'))
            d = iq.send('localhost')
            return d

        client = XMPPClient(JID('admin@localhost'), 'admin')
        self.assertTrue(wait_for_client_state(client, 'authenticated'))
        d = getVersion(client.xmlstream)
        self.assertTrue(wait_on_deferred(d))
        self.assertEqual(d.result['type'], 'result')
        client.disconnect()
