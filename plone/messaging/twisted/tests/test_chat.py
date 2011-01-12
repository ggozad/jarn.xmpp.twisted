from twisted.trial import unittest
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.test.helpers import XmlStreamStub

from plone.messaging.twisted import protocols
from plone.messaging.twisted.testing import FactoryWithJID


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
