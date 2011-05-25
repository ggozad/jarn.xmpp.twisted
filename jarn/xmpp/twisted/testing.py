import time
import urllib2

from plone.testing import Layer
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from twisted.words.protocols.jabber.jid import JID
from zope.configuration import xmlconfig
from zope.component import getUtility

from jarn.xmpp.twisted.interfaces import IZopeReactor


def wait_on_deferred(d, seconds=10):
    for i in range(seconds*10):
        if d.called:
            return True
        time.sleep(0.1)
    else:
        assert False, 'Deferred never completed.'


def wait_on_client_deferreds(client, seconds=15):
    for i in range(seconds*10):
        if not client.xmlstream.iqDeferreds:
            return True
        time.sleep(0.1)
    else:
        assert False, 'Client deferreds never completed'


def wait_for_client_state(client, state, seconds=10):
    for i in range(seconds*10):
        if client.state == state:
            return True
        time.sleep(0.1)
    else:
        assert False, 'Client never reached state %s.' % state


def wait_for_reactor_state(reactor, state=True, seconds=20):
    for i in range(seconds*10):
        if reactor.running == state:
            return True
        time.sleep(0.1)
    else:
        assert False, 'Reactor never reached state %s.' % state


class FactoryWithJID(object):

    class Object(object):
        pass

    authenticator = Object()
    authenticator.jid = JID(u'user@example.com')


class EJabberdLayer(Layer):

    def setUp(self):
        # What follows is making sure we have ejabberd running and an
        # administrator account with JID admin@localhost and password 'admin'
        pm = urllib2.HTTPPasswordMgrWithDefaultRealm()
        url = 'http://localhost:5280/admin/'
        pm.add_password('ejabberd', url, 'admin@localhost', 'admin')
        handler = urllib2.HTTPBasicAuthHandler(pm)
        opener = urllib2.build_opener(handler)
        try:
            urllib2.install_opener(opener)
            urllib2.urlopen(url)
        except urllib2.URLError:
            print """
            You need to make available a running ejabberd server in order
            to run the functional tests, as well as give the user with JID
            admin@localhost and password 'admin' administrator privileges.
            Aborting tests...
            """
            exit(1)


EJABBERD_LAYER = EJabberdLayer()


class NoReactorFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import jarn.xmpp.twisted
        xmlconfig.file('configure.zcml', jarn.xmpp.twisted,
                       context=configurationContext)

NO_REACTOR_FIXTURE = NoReactorFixture()

NO_REACTOR_INTEGRATION_TESTING = IntegrationTesting(
  bases=(NO_REACTOR_FIXTURE, ), name="NoReactorFixture:Integration")
NO_REACTOR_FUNCTIONAL_TESTING = FunctionalTesting(
  bases=(NO_REACTOR_FIXTURE, ), name="NoReactorFixture:Functional")


class ReactorFixture(PloneSandboxLayer):

    defaultBases = (EJABBERD_LAYER, NO_REACTOR_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import jarn.xmpp.twisted
        xmlconfig.file('reactor.zcml', jarn.xmpp.twisted,
                      context=configurationContext)

    def testSetUp(self):
        zr = getUtility(IZopeReactor)
        zr.start()
        wait_for_reactor_state(zr.reactor, state=True)

    def testTearDown(self):
        # Clean ZopeReactor
        zr = getUtility(IZopeReactor)
        for dc in zr.reactor.getDelayedCalls():
            if not dc.cancelled:
                dc.cancel()
        zr.stop()
        wait_for_reactor_state(zr.reactor, state=False)

        #Clean normal reactor for the twisted unit tests.
        from twisted.internet import reactor
        reactor.disconnectAll()
        for dc in reactor.getDelayedCalls():
            if not dc.cancelled:
                dc.cancel()


REACTOR_FIXTURE = ReactorFixture()

REACTOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REACTOR_FIXTURE, ), name="ReactorFixture:Integration")
REACTOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REACTOR_FIXTURE, ), name="ReactorFixture:Functional")
