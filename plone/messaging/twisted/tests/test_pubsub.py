from twisted.trial import unittest
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.data_form import NS_X_DATA
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
        query = response.addElement((protocols.NS_DISCO_ITEMS, u'query'))
        query[u'node'] = u'foo_node'
        child1 = query.addElement('item')
        child1['node'] = 'foodoo_child_1'
        child1['name'] = 'Foodoo child one'
        child1['jid'] = u'pubsub.example.com'
        child2 = query.addElement('item')
        child2['node'] = 'foodoo_child_2'
        child2['jid'] = u'pubsub.example.com'

        self.stub.send(response)

        def cb(result):
            self.assertEqual(
                [{'node': 'foodoo_child_1',
                  'jid': u'pubsub.example.com',
                  'name': 'Foodoo child one'},
                 {'node': 'foodoo_child_2',
                  'jid': u'pubsub.example.com'}],
                 result)

        d.addCallback(cb)
        return d

    def test_getSubscriptions(self):
        d = self.protocol.getSubscriptions(JID(u'pubsub.example.com'),
                                           u'foo_node')
        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'get', iq.getAttribute(u'type'))
        self.failIf(iq.pubsub is None)
        self.assertEqual(protocols.NS_PUBSUB_OWNER, iq.pubsub.uri)
        self.failIf(iq.pubsub.subscriptions is None)
        self.assertEqual(u'foo_node',
                         iq.pubsub.subscriptions.getAttribute(u'node'))
        response = toResponse(iq, u'result')
        response.addElement((protocols.NS_PUBSUB_OWNER, u'pubsub'))
        subscriptions = response.pubsub.addElement(u'subscriptions')
        subscriptions[u'node'] = u'foo_node'
        subscription1 = subscriptions.addElement(u'subscription')
        subscription1[u'jid'] = u'foo@example.com'
        subscription1[u'subscription'] = u'unconfigured'
        subscription2 = subscriptions.addElement(u'subscription')
        subscription2[u'jid'] = u'bar@example.com'
        subscription2[u'subscription'] = u'subscribed'
        subscription2[u'subid'] = u'123-abc'

        self.stub.send(response)

        def cb(result):
            self.assertEqual(
                [(JID(u'foo@example.com'), u'unconfigured'),
                 (JID(u'bar@example.com'), u'subscribed')],
                 result)

        d.addCallback(cb)
        return d

    def test_setSubscriptions(self):
        d = self.protocol.setSubscriptions(
            JID(u'pubsub.example.com'),
            u'foo_node',
            [(JID(u'foo@example.com'), u'subscribed'),
             (JID(u'bar@example.com'), u'none')])

        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.failIf(iq.pubsub is None)
        self.assertEqual(protocols.NS_PUBSUB_OWNER, iq.pubsub.uri)
        self.failIf(iq.pubsub.subscriptions is None)
        self.assertEqual(u'foo_node',
                         iq.pubsub.subscriptions.getAttribute(u'node'))
        subscriptions = iq.pubsub.subscriptions.children
        self.assertEqual(2, len(subscriptions))
        self.assertEqual(u'foo@example.com', subscriptions[0]['jid'])
        self.assertEqual(u'subscribed', subscriptions[0]['subscription'])
        self.assertEqual(u'bar@example.com', subscriptions[1]['jid'])
        self.assertEqual(u'none', subscriptions[1]['subscription'])

        response = toResponse(iq, u'result')
        self.stub.send(response)

        def cb(result):
            self.assertEqual(True, result)

        d.addCallback(cb)
        return d

    def test_getNodeType(self):
        d = self.protocol.getNodeType(JID(u'pubsub.example.com'),
                                      u'foo_node')
        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'get', iq.getAttribute(u'type'))
        self.failIf(iq.query is None)
        self.assertEqual(protocols.NS_DISCO_INFO, iq.query.uri)
        self.assertEqual(u'foo_node', iq.query['node'])

        response = toResponse(iq, u'result')
        query = response.addElement((protocols.NS_DISCO_INFO, u'query'))
        query[u'node'] = u'foo_node'
        identity = query.addElement(u'identity')
        identity[u'category'] = u'pubsub'
        identity[u'type'] = u'collection'

        self.stub.send(response)

        def cb(result):
            self.assertEqual(u'collection', result)

        d.addCallback(cb)
        return d

    def test_getDefaultNodeConfiguration(self):
        raise NotImplementedError()

    def test_getNodeConfiguration(self):
        raise NotImplementedError()

    def test_configureNode(self):
        d = self.protocol.configureNode(JID(u'pubsub.example.com'),
                                        u'foo_node',
                                        {u'pubsub#collection': u'bar_node'})
        iq = self.stub.output[-1]
        self.assertEqual(u'pubsub.example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.failIf(iq.pubsub is None)
        self.assertEqual(protocols.NS_PUBSUB_OWNER, iq.pubsub.uri)
        self.failIf(iq.pubsub.configure is None)
        self.assertEqual(u'foo_node',
                         iq.pubsub.configure.getAttribute(u'node'))
        self.failIf(iq.pubsub.configure.x is None)
        x = iq.pubsub.configure.x
        self.assertEqual(NS_X_DATA, x.uri)
        self.assertEqual(u'submit', x.getAttribute('type'))
        self.assertEqual(2, len(x.children))
        fields = x.children
        self.failIf(fields[0].value is None)
        self.assertEqual([protocols.NS_PUBSUB_NODE_CONFIG],
                         fields[0].value.children)
        self.assertEqual(u'pubsub#collection', fields[1].getAttribute(u'var'))
        self.failIf(fields[1].value is None)
        self.assertEqual([u'bar_node'], fields[1].value.children)
        self.assertEqual(fields[0].value.children,
            [protocols.NS_PUBSUB_NODE_CONFIG])

        response = toResponse(iq, u'result')
        self.stub.send(response)

        def cb(result):
            self.assertEqual(True, result)

        d.addCallback(cb)
        return d

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
