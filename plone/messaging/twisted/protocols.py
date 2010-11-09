"""
XMPP Ping.

The XMPP Service Administration protocol is documented in
U{XEP-0133<http://xmpp.org/extensions/xep-0133.html>}.
"""

from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber.xmlstream import IQ, toResponse

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import data_form

NS_COMMANDS = 'http://jabber.org/protocol/commands'
NODE_ADMIN = 'http://jabber.org/protocol/admin'
NODE_ADMIN_ANNOUNCE = NODE_ADMIN + '#announce'
ADMIN_REQUEST = "/iq[@type='get' or @type='set']" \
                "/command[@xmlns='%s' and @node='/%s']" % (NS_COMMANDS, NODE_ADMIN)

class AdminClient(XMPPHandler):
    """
    Admin client.

    This handler implements the protocol for sending out XMPP admin requests.
    """

    def sendAnnouncement(self, body, subject='Announce'):
        """Send an announement to all users.        
        """

        def formReceived(iq):
            command = iq.command
            sessionid = command['sessionid']
            form = data_form.findForm(command, NODE_ADMIN)

            response = toResponse(iq, 'set')
            #response = IQ(self.xmlstream, 'set')
            #response['to'] = iq['from']
            #response['id'] = iq['id']
            command = response.addElement((NS_COMMANDS, "command"))
            command['node'] = NODE_ADMIN_ANNOUNCE
            command['sessionid'] = sessionid

            form.formType = 'submit'
            form.fields['subject'].value = subject
            form.fields['body'].value = body

            command.addChild(form.toElement())
            self.send(response)
            #d = response.send()
            #d.addCallback(resultReceived)
            #return d

        iq = IQ(self.xmlstream, 'set')
        iq['to'] = self.parent.jid.host
        command = iq.addElement((NS_COMMANDS, 'command'))
        command['action'] = 'execute'
        command['node'] = NODE_ADMIN_ANNOUNCE
        d = iq.send()
        d.addCallback(formReceived)
        return d