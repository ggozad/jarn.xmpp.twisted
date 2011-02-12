import string
import random
import logging

from twisted.words.xish.domish import Element
from twisted.words.protocols.jabber.jid import JID
from twisted.words.protocols.jabber.xmlstream import IQ
from wokkel import data_form
from wokkel.disco import NS_DISCO_INFO, NS_DISCO_ITEMS
from wokkel.pubsub import PubSubClient as WokkelPubSubClient
from wokkel.subprotocols import XMPPHandler
from wokkel.pubsub import NS_PUBSUB_OWNER, NS_PUBSUB_NODE_CONFIG

NS_CLIENT = 'jabber:client'
NS_ROSTER_X = 'http://jabber.org/protocol/rosterx'
NS_COMMANDS = 'http://jabber.org/protocol/commands'
NODE_ADMIN = 'http://jabber.org/protocol/admin'
NODE_ADMIN_GET_REGISTERED_USERS = NODE_ADMIN + '#get-registered-users-list'
NODE_ADMIN_ADD_USER = NODE_ADMIN + '#add-user'
NODE_ADMIN_DELETE_USER = NODE_ADMIN + '#delete-user'
NODE_ADMIN_ANNOUNCE = NODE_ADMIN + '#announce'
XHTML_IM = 'http://jabber.org/protocol/xhtml-im'
XHTML = 'http://www.w3.org/1999/xhtml'

ADMIN_REQUEST = "/iq[@type='get' or @type='set']" \
                "/command[@xmlns='%s' and @node='/%s']" % \
                (NS_COMMANDS, NODE_ADMIN)

logger = logging.getLogger('jarn.xmpp.twisted')


def getRandomId():
    chars = string.letters + string.digits
    return ''.join([random.choice(chars) for i in range(10)])


class ChatHandler(XMPPHandler):
    """
    Simple chat client.
    http://xmpp.org/extensions/xep-0071.html
    """

    def sendMessage(self, to, body):
        """ Send a text message
        """
        message = Element((None, "message", ))
        message["id"] = getRandomId()
        message["from"] = self.xmlstream.factory.authenticator.jid.full()
        message["to"] = to.full()
        message["type"] = 'chat'
        message.addElement('body', content=body)
        self.xmlstream.send(message)
        return True

    def sendXHTMLMessage(self, to, body, xhtml_body):
        """ Send an HTML message.
        """
        message = Element((NS_CLIENT, "message", ))
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

    def sendRosterItemAddSuggestion(self, to, items, group=None):
        """ Suggest a user(s) to be added in the roster.
        """
        message = Element((None, "message", ))
        message["id"] = getRandomId()
        message["from"] = self.xmlstream.factory.authenticator.jid.full()
        message["to"] = to.userhost()
        x = message.addElement((NS_ROSTER_X, 'x'))
        for jid in items:
            item = x.addElement('item')
            item["action"]='add'
            item["jid"] = jid.userhost()
            if group:
                item.addElement('group', content=group)
        self.xmlstream.send(message)
        return True


class AdminHandler(XMPPHandler):
    """
    Admin client.
    http://xmpp.org/extensions/xep-0133.html
    """

    def getRegisteredUsers(self):
        """ XXX: This is ejabberd specific. ejabberd does not implement
        the #get-registered-users-list command, instead does it with an iq/get.
        """

        def resultReceived(result):
            items = result.query.children
            result = [item.attributes for item in items]
            logger.info("Got registered users: %s" % result)
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = self.xmlstream.factory.authenticator.jid.host
        query = iq.addElement((NS_DISCO_ITEMS, 'query'))
        query['node'] = 'all users'
        d = iq.send()
        d.addCallbacks(resultReceived, error)
        return d

    def addUser(self, userjid, password):
        """Add a user.
        """

        def resultReceived(iq):
            logger.info("Added user %s" % userjid)
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
            logger.info("Deleted users %s" % userjids)
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
            logger.info("Sent announcement %s." % body)
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
    """ Pubslish-Subscribe
    http://xmpp.org/extensions/xep-0060.html
    http://xmpp.org/extensions/xep-0248.html
    """

    def publish(self, service, nodeIdentifier, items=[]):

        def cb(result):
            logger.info("Published to node %s." % nodeIdentifier)
            return True

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False


        d = super(PubSubHandler, self).publish(service, nodeIdentifier, items)
        d.addCallbacks(cb, error)
        return d

    def itemsReceived(self, event):
        logger.info("Items received. %s." % event.items)
        if hasattr(self.parent, 'itemsReceived'):
            self.parent.itemsReceived(event)

    def createNode(self, service, nodeIdentifier, options=None):

        def cb(result):
            logger.info("Created node %s." % nodeIdentifier)
            return True

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False
        d = super(PubSubHandler, self).createNode(
            service,
            nodeIdentifier=nodeIdentifier,
            options=options)
        d.addCallbacks(cb, error)
        return d

    def deleteNode(self, service, nodeIdentifier):

        def cb(result):
            logger.info("Deleted node %s." % nodeIdentifier)
            return True

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        d = super(PubSubHandler, self).deleteNode(service, nodeIdentifier)
        d.addCallbacks(cb, error)
        return d

    def getNodes(self, service, nodeIdentifier=None):

        def cb(result):
            items = result.query.children
            result = [item.attributes for item in items]
            logger.info("Got nodes of %s: %s ." % (nodeIdentifier, result))
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return []

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = service.full()
        query = iq.addElement((NS_DISCO_ITEMS, 'query'))
        if nodeIdentifier is not None:
            query['node'] = nodeIdentifier
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def getSubscriptions(self, service, nodeIdentifier):

        def cb(result):
            subscriptions = result.pubsub.subscriptions.children
            result = [(JID(item['jid']), item['subscription'])
                     for item in subscriptions]
            logger.info("Got subscriptions for %s: %s ." % \
                (nodeIdentifier, result))
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return []

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        subscriptions = pubsub.addElement('subscriptions')
        subscriptions['node'] = nodeIdentifier
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def setSubscriptions(self, service, nodeIdentifier, delta):

        def cb(result):
            if result['type']==u'result':
                logger.info("Set subscriptions for %s: %s ." % \
                    (nodeIdentifier, delta))
                return True
            return False

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'set')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        subscriptions = pubsub.addElement('subscriptions')
        subscriptions['node']=nodeIdentifier
        for jid, subscription in delta:
            el = subscriptions.addElement('subscription')
            el['jid'] = jid.userhost()
            el['subscription'] = subscription

        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def getNodeType(self, service, nodeIdentifier):

        def cb(result):
            result = result.query.identity['type']
            logger.info("Got node type %s: %s ." % (nodeIdentifier, result))
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return []

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = service.full()
        query = iq.addElement((NS_DISCO_INFO, 'query'))
        query['node'] = nodeIdentifier
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def getDefaultNodeConfiguration(self, service):

        def cb(result):
            fields = [field
                      for field in result.pubsub.default.x.children
                      if field[u'type']!=u'hidden']
            result = dict()
            for field in fields:
                value = None
                try:
                    value = field.value.children[0]
                except (AttributeError, IndexError):
                    pass
                result[field['var']] = value
            logger.info("Got default node configuration: %s ." % result)
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return []

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        pubsub.addElement('default')
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def getNodeConfiguration(self, service, nodeIdentifier):

        def cb(result):
            fields = [field
                      for field in result.pubsub.configure.x.children
                      if field[u'type']!=u'hidden']
            result = dict()
            for field in fields:
                value = None
                try:
                    value = field.value.children[0]
                except (AttributeError, IndexError):
                    pass
                result[field['var']] = value
            logger.info("Got node config  %s: %s ." % (nodeIdentifier, result))
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return []

        iq = IQ(self.xmlstream, 'get')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        configure = pubsub.addElement('configure')
        configure['node'] = nodeIdentifier
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def configureNode(self, service, nodeIdentifier, options):

        def cb(result):
            logger.info("Configured %s: %s ." % (nodeIdentifier, options))
            return True

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        form = data_form.Form(formType='submit',
                              formNamespace=NS_PUBSUB_NODE_CONFIG)
        form.makeFields(options)
        iq = IQ(self.xmlstream, 'set')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        configure = pubsub.addElement('configure')
        configure['node'] = nodeIdentifier
        configure = configure.addChild(form.toElement())
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def associateNodeWithCollection(self, service,
                                    nodeIdentifier, collectionIdentifier):
        """ XXX: Not supported by ejabberd
        """

        def cb(result):
            return True

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return False

        iq = IQ(self.xmlstream, 'set')
        iq['to'] = service.full()
        pubsub = iq.addElement((NS_PUBSUB_OWNER, 'pubsub'))
        collection = pubsub.addElement('collection')
        collection['node'] = collectionIdentifier
        associate = collection.addElement('associate')
        associate['node'] = nodeIdentifier
        d = iq.send()
        d.addCallbacks(cb, error)
        return d

    def getAffiliations(self, service, nodeIdentifier):

        def cb(result):
            affiliations = result.pubsub.affiliations
            result = []
            for affiliate in affiliations.children:
                result.append((JID(affiliate['jid']),
                               affiliate['affiliation'], ))
            logger.info("Got affiliations for %s: %s ." % \
                (nodeIdentifier, result))
            return result

        def error(failure):
            # TODO: Handle gracefully?
            logger.error(failure.getTraceback())
            return []

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
                logger.info("Modified affiliations for %s: %s ." % \
                    (nodeIdentifier, delta))
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
