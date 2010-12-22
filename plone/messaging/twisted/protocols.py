"""
XMPP Admin.

The XMPP Service Administration protocol is documented in
U{XEP-0133<http://xmpp.org/extensions/xep-0133.html>}.
"""

import string
import random
import logging
from twisted.words.xish.domish import Element
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import IQ
from wokkel.pubsub import PubSubClient as WokkelPubSubClient
from wokkel.subprotocols import XMPPHandler
from wokkel import data_form
from wokkel.pubsub import NS_PUBSUB, NS_PUBSUB_OWNER

NS_CLIENT = 'jabber:client'
XHTML_IM = 'http://jabber.org/protocol/xhtml-im'
XHTML = 'http://www.w3.org/1999/xhtml'
NS_COMMANDS = 'http://jabber.org/protocol/commands'
NODE_ADMIN = 'http://jabber.org/protocol/admin'
NODE_ADMIN_ADD_USER = NODE_ADMIN + '#add-user'
NODE_ADMIN_DELETE_USER = NODE_ADMIN + '#delete-user'
NODE_ADMIN_ANNOUNCE = NODE_ADMIN + '#announce'

ADMIN_REQUEST = "/iq[@type='get' or @type='set']" \
                "/command[@xmlns='%s' and @node='/%s']" % \
                (NS_COMMANDS, NODE_ADMIN)

logger = logging.getLogger('plone.messaging.twisted')


def getRandomId():
    chars = string.letters + string.digits
    return ''.join([random.choice(chars) for i in range(10)])


class ChatHandler(XMPPHandler):
    """
    Simple chat client.
    This handler can send text/XHTML messages.
    """

    def sendMessage(self, to, body):
        message = Element((None, "message",))
        message["id"] = getRandomId()
        message["from"] = self.xmlstream.factory.authenticator.jid.full()
        message["to"] = to.full()
        message["type"] = 'chat'
        message.addElement('body', content=body)
        self.xmlstream.send(message)
        return True

    def sendXHTMLMessage(self, to, body, xhtml_body):
        message = Element((NS_CLIENT, "message",))
        message["id"] = getRandomId()
        message["from"] = self.xmlstream.factory.authenticator.jid.full()
        message["to"] = to.full()
        message["type"] = 'chat'
        message.addElement('body', content=body)
        html = message.addElement((XHTML_IM, 'html'))
        html_body = html.addElement((XHTML, 'body'))
        html_body.addRawXml(xhtml_body)
        self.xmlstream.send(message)
        return True


class AdminHandler(XMPPHandler):
    """
    Admin client.
    This handler implements the protocol for sending out XMPP admin requests.
    """

    def addUser(self, userjid, password):
        """Add a user.
        """

        def resultReceived(iq):
            logger.info("%s: Added user %s" % \
                (self.xmlstream.factory.authenticator.jid.full(), userjid))
            return True

        def formReceived(iq):
            command = iq.command
            sessionid = command['sessionid']
            form = data_form.findForm(command, NODE_ADMIN)

            response = IQ(self.xmlstream, 'set')
            response['to'] = iq['from']
            response['id'] = iq['id']

            command = response.addElement((NS_COMMANDS, 'command'))
            command['node'] = NODE_ADMIN_ADD_USER
            command['sessionid'] = sessionid

            form.formType = 'submit'
            form.fields['accountjid'].value = userjid
            form.fields['password'].value = password
            form.fields['password-verify'].value = password

            command.addChild(form.toElement())
            d = response.send()
            d.addCallbacks(resultReceived, error)
            return d

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'set')
        iq['to'] = self.xmlstream.factory.authenticator.jid.host
        command = iq.addElement((NS_COMMANDS, 'command'))
        command['action'] = 'execute'
        command['node'] = NODE_ADMIN_ADD_USER
        d = iq.send()
        d.addCallbacks(formReceived, error)
        return d

    def deleteUsers(self, userjids):
        """Add a user.
        """

        def resultReceived(iq):
            logger.info("%s: Deleted users %s" % \
                (self.xmlstream.factory.authenticator.jid.full(), userjids))
            return True

        def formReceived(iq):
            command = iq.command
            sessionid = command['sessionid']
            form = data_form.findForm(command, NODE_ADMIN)

            response = IQ(self.xmlstream, 'set')
            response['to'] = iq['from']
            response['id'] = iq['id']

            command = response.addElement((NS_COMMANDS, 'command'))
            command['node'] = NODE_ADMIN_DELETE_USER
            command['sessionid'] = sessionid

            form.formType = 'submit'
            form.fields['accountjids'].values = userjids

            command.addChild(form.toElement())
            d = response.send()
            d.addCallbacks(resultReceived, error)
            return d

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        if isinstance(userjids, basestring):
            userjids = [userjids]
        iq = IQ(self.xmlstream, 'set')
        iq['to'] = self.xmlstream.factory.authenticator.jid.host
        command = iq.addElement((NS_COMMANDS, 'command'))
        command['action'] = 'execute'
        command['node'] = NODE_ADMIN_DELETE_USER
        d = iq.send()
        d.addCallbacks(formReceived, error)
        return d

    def sendAnnouncement(self, body, subject='Announce'):
        """Send an announement to all users.
        """

        def resultReceived(iq):
            return True

        def formReceived(iq):
            command = iq.command
            sessionid = command['sessionid']
            form = data_form.findForm(command, NODE_ADMIN)

            #from twisted.words.protocols.jabber.xmlstream import toResponse
            #response = toResponse(iq, 'set')
            response = IQ(self.xmlstream, 'set')
            response['to'] = iq['from']
            response['id'] = iq['id']

            command = response.addElement((NS_COMMANDS, 'command'))
            command['node'] = NODE_ADMIN_ANNOUNCE
            command['sessionid'] = sessionid

            form.formType = 'submit'
            form.fields['subject'].value = subject
            form.fields['body'].value = body

            command.addChild(form.toElement())
            d = response.send()
            d.addCallbacks(resultReceived, error)
            return d

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'set')
        iq['to'] = self.xmlstream.factory.authenticator.jid.host
        command = iq.addElement((NS_COMMANDS, 'command'))
        command['action'] = 'execute'
        command['node'] = NODE_ADMIN_ANNOUNCE
        d = iq.send()
        d.addCallbacks(formReceived, error)
        return d


class PubSubHandler(WokkelPubSubClient):

    def getAffiliations(self, service, nodeIdentifier):

        def cb(result):
            res = []
            affiliations = result.pubsub.affiliations
            for affiliate in affiliations.children:
                res.append((JID(affiliate['jid']), affiliate['affiliation'],))
            return res

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        affiliations = pubsub.addElement('affiliations')
        affiliations['node']=nodeIdentifier
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def modifyAffiliations(self, service, nodeIdentifier, delta):

        def cb(result):
            if result['type']==u'result':
                return True
            return False

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'set')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        affiliations = pubsub.addElement('affiliations')
        affiliations['node']=nodeIdentifier
        for jid, affiliation in delta:
            el = affiliations.addElement('affiliation')
            el['jid'] = jid.userhost()
            el['affiliation'] = affiliation

        d = iq.send()
        d.addCallbacks(cb, error)
        return d
