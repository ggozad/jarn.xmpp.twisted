from twisted.trial import unittest
from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.test.helpers import XmlStreamStub
from wokkel import data_form

from jarn.xmpp.twisted import protocols
from jarn.xmpp.twisted.testing import FactoryWithJID


class AdminCommandsProtocolTest(unittest.TestCase):
    """
    """

    def setUp(self):
        self.stub = XmlStreamStub()
        self.stub.xmlstream.factory = FactoryWithJID()
        self.protocol = protocols.AdminHandler()
        self.protocol.xmlstream = self.stub.xmlstream
        self.protocol.connectionInitialized()

    def test_addUser(self):
        self.protocol.addUser(u'joe@example.com', u'secret')

        iq = self.stub.output[-1]
        self.assertEqual(u'example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.failIf(iq.command is None)
        self.assertEqual(protocols.NODE_ADMIN_ADD_USER,
                         iq.command.getAttribute('node'))
        self.assertEqual('execute', iq.command.getAttribute('action'))
        response = toResponse(iq, u'result')
        response['to'] = \
            self.protocol.xmlstream.factory.authenticator.jid.full()
        command = response.addElement((protocols.NS_COMMANDS, u'command'))
        command[u'node'] = protocols.NODE_ADMIN_ADD_USER
        command[u'status'] = u'executing'
        command[u'sessionid'] = u'sid-0'
        form = data_form.Form(u'form')
        form_type = data_form.Field(u'hidden',
                                    var=u'FORM_TYPE',
                                    value=protocols.NODE_ADMIN)
        userjid = data_form.Field(u'jid-single',
                                  var=u'accountjid', required=True)
        password = data_form.Field(u'text-private',
                                   var=u'password', required=True)
        password_verify = data_form.Field(u'text-private',
                                          var=u'password-verify',
                                          required=True)
        form.addField(form_type)
        form.addField(userjid)
        form.addField(password)
        form.addField(password_verify)
        command.addContent(form.toElement())
        self.stub.send(response)

        iq = self.stub.output[-1]
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.assertEqual(protocols.NODE_ADMIN_ADD_USER,
                         iq.command.getAttribute(u'node'))
        self.assertEqual(u'sid-0', iq.command.getAttribute(u'sessionid'))
        form = data_form.findForm(iq.command, protocols.NODE_ADMIN)
        self.assertEqual(u'submit', form.formType)
        self.failUnless(u'accountjid' in form.fields)
        self.assertEqual(u'joe@example.com', form.fields['accountjid'].value)
        self.failUnless(u'password' in form.fields)
        self.assertEqual(u'secret', form.fields['password'].value)
        self.failUnless(u'password-verify' in form.fields)
        self.assertEqual(u'secret', form.fields['password-verify'].value)

    def test_deleteUsers(self):
        self.protocol.deleteUsers(u'joe@example.com')

        iq = self.stub.output[-1]
        self.assertEqual(u'example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.failIf(iq.command is None)
        self.assertEqual(protocols.NODE_ADMIN_DELETE_USER,
                         iq.command.getAttribute('node'))
        self.assertEqual('execute', iq.command.getAttribute('action'))
        response = toResponse(iq, u'result')
        response['to'] = \
            self.protocol.xmlstream.factory.authenticator.jid.full()
        command = response.addElement((protocols.NS_COMMANDS, u'command'))
        command[u'node'] = protocols.NODE_ADMIN_DELETE_USER
        command[u'status'] = u'executing'
        command[u'sessionid'] = u'sid-0'
        form = data_form.Form(u'form')
        form_type = data_form.Field(u'hidden',
                                    var=u'FORM_TYPE',
                                    value=protocols.NODE_ADMIN)
        userjids = data_form.Field(u'jid-multi',
                                  var=u'accountjids')
        form.addField(form_type)
        form.addField(userjids)
        command.addContent(form.toElement())
        self.stub.send(response)

        iq = self.stub.output[-1]
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.assertEqual(protocols.NODE_ADMIN_DELETE_USER,
                         iq.command.getAttribute(u'node'))
        self.assertEqual(u'sid-0', iq.command.getAttribute(u'sessionid'))
        form = data_form.findForm(iq.command, protocols.NODE_ADMIN)
        self.assertEqual(u'submit', form.formType)
        self.failUnless(u'accountjids' in form.fields)
        self.assertEqual([u'joe@example.com'],
                         form.fields['accountjids'].values)

    def test_sendAnnouncement(self):
        self.protocol.sendAnnouncement(u'Hello world')

        iq = self.stub.output[-1]
        self.assertEqual(u'example.com', iq.getAttribute(u'to'))
        self.assertEqual(u'set', iq.getAttribute(u'type'))
        self.assertEqual(protocols.NS_COMMANDS, iq.command.uri)
        self.failIf(iq.command is None)
        self.assertEqual(protocols.NODE_ADMIN_ANNOUNCE,
                         iq.command.getAttribute('node'))
        self.assertEqual('execute', iq.command.getAttribute('action'))

        response = toResponse(iq, u'result')
        response['to'] = \
            self.protocol.xmlstream.factory.authenticator.jid.full()
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
        self.assertEqual(protocols.NODE_ADMIN_ANNOUNCE,
                         iq.command.getAttribute(u'node'))
        self.assertEqual(u'sid-0', iq.command.getAttribute(u'sessionid'))
        form = data_form.findForm(iq.command, protocols.NODE_ADMIN)
        self.assertEqual(u'submit', form.formType)
        self.failUnless(u'subject' in form.fields)
        self.assertEqual(u'Announce', form.fields['subject'].value)
        self.failUnless(u'body' in form.fields)
        self.assertEqual(u'Hello world', form.fields['body'].value)
