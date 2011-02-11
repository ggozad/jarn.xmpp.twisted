from twisted.trial import unittest
from twisted.words.protocols.jabber.jid import JID
from wokkel.test.helpers import XmlStreamStub

from jarn.xmpp.twisted import protocols
from jarn.xmpp.twisted.testing import FactoryWithJID


class ChatCommandsProtocolTest(unittest.TestCase):
    """
    """

    def setUp(self):
        self.stub = XmlStreamStub()
        self.stub.xmlstream.factory = FactoryWithJID()
        self.protocol = protocols.ChatHandler()
        self.protocol.xmlstream = self.stub.xmlstream
        self.protocol.connectionInitialized()

    def test_sendMessage(self):
        self.protocol.sendMessage(JID(u'joe@example.com'), u'Hello world')
        message = self.stub.output[-1]
        self.assertEqual(u'message', message.name)
        self.assertEqual(u'joe@example.com', message.getAttribute(u'to'))
        self.assertEqual(u'user@example.com', message.getAttribute(u'from'))
        self.assertEqual(u'chat', message.getAttribute(u'type'))
        self.failIf(message.body is None)
        self.assertEqual([u'Hello world'], message.body.children)

    def test_sendXHTMLMessage(self):
        self.protocol.sendXHTMLMessage(JID(u'joe@example.com'),
                                       u'Hello world',
                                       u'<p>Hello world</p>')
        message = self.stub.output[-1]
        self.assertEqual(u'message', message.name)
        self.assertEqual(protocols.NS_CLIENT, message.uri)
        self.assertEqual(u'joe@example.com', message.getAttribute(u'to'))
        self.assertEqual(u'user@example.com', message.getAttribute(u'from'))
        self.assertEqual(u'chat', message.getAttribute(u'type'))
        self.failIf(message.body is None)
        self.assertEqual([u'Hello world'], message.body.children)
        self.failIf(message.html is None)
        html = message.html
        self.assertEqual(protocols.XHTML_IM, html.uri)
        self.assertEqual(protocols.XHTML, html.body.uri)
        self.assertEqual([u'<p>Hello world</p>'], html.body.children)

    def test_sendRosterItemAddSuggestion(self):
        self.protocol.sendRosterItemAddSuggestion(
            JID(u'joe@example.com/resource'),
            [JID(u'bar@example.com/resource')],
            group=u'Friends')
        message = self.stub.output[-1]
        self.assertEqual(u'message', message.name)
        self.assertEqual(u'joe@example.com', message.getAttribute(u'to'))
        self.assertEqual(u'user@example.com', message.getAttribute(u'from'))
        self.failIf(message.x is None)
        x = message.x
        self.assertEqual(protocols.NS_ROSTER_X, x.uri)
        self.failIf(x.item is None)
        item = x.item
        self.assertEqual(u'add', item.getAttribute(u'action'))
        self.assertEqual(u'bar@example.com', item.getAttribute('jid'))
        self.failIf(item.group is None)
        self.assertEqual([u'Friends'], item.group.children)
