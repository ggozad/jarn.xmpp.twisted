from twisted.trial import unittest
from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.test.helpers import XmlStreamStub
from wokkel import data_form
from plone.messaging.twisted import protocols


class ParentWithJID(object):
    jid = JID("user@example.com")


class AdminCommandsProtocolTest(unittest.TestCase):
    """
    """

    def setUp(self):
        self.stub = XmlStreamStub()
        self.protocol = protocols.AdminClient()
        self.protocol.xmlstream = self.stub.xmlstream
        self.protocol.connectionInitialized()
        self.protocol.parent = ParentWithJID()

    def test_sendAnnouncement(self):
        """
        Pinging a service should fire a deferred with None
        """

        self.protocol.sendAnnouncement(u"Hello world")
        iq = self.stub.output[-1]
        self.assertEqual(u'example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.failIf(iq.command is None)
        self.assertEqual(protocols.NODE_ADMIN_ANNOUNCE,
                         iq.command.getAttribute('node'))
        self.assertEqual('execute',iq.command.getAttribute('action'))

        response = toResponse(iq, u'result')
        response ['to'] = self.protocol.parent.jid.full()
        command = response.addElement((protocols.NS_COMMANDS, u'command'))
        command[u'node'] = protocols.NODE_ADMIN_ANNOUNCE
        command[u'status'] = u'executing'
        command[u'sessionid'] = u'sid-0'
        form = data_form.Form(u'form')
        form_type = data_form.Field(u'hidden', var=u'FORM_TYPE',
                                    value=protocols.NODE_ADMIN)
        subject = data_form.Field(u'text-single', var=u'subject')
        body = data_form.Field(u'text-multi', var=u'body')
        form.addField(form_type)
        form.addField(subject)
        form.addField(body)
        command.addContent(form.toElement())
        self.stub.send(response)

        iq = self.stub.output[-1]
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.assertEqual(protocols.NODE_ADMIN_ANNOUNCE, iq.command[u'node'])
        self.assertEqual(u'sid-0', iq.command.getAttribute(u'sessionid'))
        form = data_form.findForm(iq.command, protocols.NODE_ADMIN)
        self.assertEqual(u'submit', form.formType)
        self.failUnless(u'subject' in form.fields)
        self.assertEqual(u'Announce', form.fields['subject'].value)
        self.failUnless(u'body' in form.fields)
        self.assertEqual(u'Hello world', form.fields['body'].value)
