"""
XMPP Admin.

The XMPP Service Administration protocol is documented in
U{XEP-0133<http://xmpp.org/extensions/xep-0133.html>}.
"""

import logging
from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber.xmlstream import IQ

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import data_form


NS_COMMANDS = 'http://jabber.org/protocol/commands'
NODE_ADMIN = 'http://jabber.org/protocol/admin'
NODE_ADMIN_ADD_USER = NODE_ADMIN + '#add-user'
NODE_ADMIN_DELETE_USER = NODE_ADMIN + '#delete-user'
NODE_ADMIN_ANNOUNCE = NODE_ADMIN + '#announce'

ADMIN_REQUEST = "/iq[@type='get' or @type='set']" \
                "/command[@xmlns='%s' and @node='/%s']" % \
                (NS_COMMANDS, NODE_ADMIN)

logger = logging.getLogger('plone.messaging.twisted')


class AdminClient(XMPPHandler):
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
