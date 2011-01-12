from twisted.trial import unittest
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.test.helpers import XmlStreamStub

from plone.messaging.twisted import protocols
from plone.messaging.twisted.testing import FactoryWithJID


class PubSubCommandsProtocolTest(unittest.TestCase):
    """
    """

    def setUp(self):
        self.stub = XmlStreamStub()
        self.stub.xmlstream.factory = FactoryWithJID()
        self.protocol = protocols.PubSubHandler()
        self.protocol.xmlstream = self.stub.xmlstream
        self.protocol.connectionInitialized()

    def test_getNodes(self):
        d = self.protocol.getNodes(JID(u'pubsub.example.com'),
                                   u'foo_node')
        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'get', iq.getAttribute(u'type'))
        self.failIf(iq.query is None)
        self.assertEqual(protocols.NS_DISCO_ITEMS, iq.query.uri)
        self.assertEqual(u'foo_node', iq.query.getAttribute(u'node'))
        response = toResponse(iq, u'result')
        response['to'] = \
            self.protocol.xmlstream.factory.authenticator.jid.full()
        raise NotImplementedError()
        return d

    def test_getSubscriptions(self):
        raise NotImplementedError()

    def test_setSubscriptions(self):
        raise NotImplementedError()

    def test_getNodeType(self):
        raise NotImplementedError()

    def test_getDefaultNodeConfiguration(self):
        raise NotImplementedError()

    def test_getNodeConfiguration(self):
        raise NotImplementedError()

    def test_configureNode(self):
        raise NotImplementedError()

    def test_associateNodeToCollection(self):
        raise NotImplementedError()

    def test_getAffiliations(self):
        d = self.protocol.getAffiliations(JID(u'pubsub.example.com'),
                                          u'foo_node')
        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'get', iq.getAttribute(u'type'))
        self.failIf(iq.pubsub is None)
        self.assertEqual(protocols.NS_PUBSUB_OWNER, iq.pubsub.uri)
        self.failIf(iq.pubsub.affiliations is None)
        self.assertEqual('foo_node',
                         iq.pubsub.affiliations['node'])
        response = toResponse(iq, u'result')
        response['to'] = \
            self.protocol.xmlstream.factory.authenticator.jid.full()
        pubsub = response.addElement((protocols.NS_PUBSUB_OWNER, u'pubsub'))

        affiliations = pubsub.addElement(u'affiliations')
        affiliations['node'] = u'foo_node'
        user = affiliations.addElement(u'affiliation')
        user['jid'] = 'user@example.com'
        user['affiliation'] = 'owner'
        foo = affiliations.addElement(u'affiliation')
        foo['jid'] = 'foo@example.com'
        foo['affiliation'] = 'publisher'
        self.stub.send(response)

        def cb(result):
            self.assertEqual(result,
            [(JID(u'user@example.com'), 'owner'),
             (JID(u'foo@example.com'), 'publisher')])

        d.addCallback(cb)
        return d

    def test_modifyAffiliations(self):
        d = self.protocol.modifyAffiliations(JID(u'pubsub.example.com'),
            u'foo_node', [(JID(u'foo@example.com'), 'none')])
        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.failIf(iq.pubsub is None)
        self.assertEqual(protocols.NS_PUBSUB_OWNER, iq.pubsub.uri)
        self.failIf(iq.pubsub.affiliations is None)
        self.assertEqual('foo_node',
                         iq.pubsub.affiliations['node'])
        affiliation = iq.pubsub.affiliations.affiliation
        self.assertEqual('foo@example.com', affiliation['jid'])
        self.assertEqual('none', affiliation['affiliation'])

        response = toResponse(iq, u'result')
        response['to'] = \
            self.protocol.xmlstream.factory.authenticator.jid.full()
        self.stub.send(response)

        def cb(result):
            self.assertEqual(result, True)

        d.addCallback(cb)
        return d
