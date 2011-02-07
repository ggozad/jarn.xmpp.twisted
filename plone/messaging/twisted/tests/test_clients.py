import unittest2 as unittest

#from twisted.internet import reactor
#from twisted.trial import unittest
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import IQ
from zope.component import getUtility

from plone.messaging.twisted.client import DeferredXMPPClient
from plone.messaging.twisted.client import XMPPClient
from plone.messaging.twisted.interfaces import IZopeReactor
from plone.messaging.twisted.testing import REACTOR_INTEGRATION_TESTING
from plone.messaging.twisted.testing import wait_on_deferred
from plone.messaging.twisted.testing import wait_for_connection

NS_VERSION = 'jabber:iq:version'


class ClientNetworkTest(unittest.TestCase):

    layer = REACTOR_INTEGRATION_TESTING

    def test_deferred_client(self):

        def getVersion(xmlstream):
            iq = IQ(xmlstream, 'get')
            iq.addElement((NS_VERSION, 'query'))
            d = iq.send('localhost')
            return d

        self.deferred_results = False
        client = DeferredXMPPClient()
        d = client.execute(JID('admin@localhost'), 'admin', getVersion)
        self.assertTrue(wait_on_deferred(d))
        self.assertEqual(d.result['type'], 'result')

    def test_client(self):

        def getVersion(xmlstream):
            iq = IQ(xmlstream, 'get')
            iq.addElement((NS_VERSION, 'query'))
            d = iq.send('localhost')
            return d

        client = XMPPClient(JID('admin@localhost'), 'admin')
        self.assertTrue(wait_for_connection(client))
        d = getVersion(client.xmlstream)
        self.assertTrue(wait_on_deferred(d))
        self.assertEqual(d.result['type'], 'result')
        client.disconnect()
