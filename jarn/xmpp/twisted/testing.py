import time

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


def wait_on_client_deferreds(client, seconds=10):
    while client.xmlstream.iqDeferreds:
        time.sleep(0.1)


def wait_for_client_state(client, state, seconds=10):
    for i in range(seconds*10):
        if client.state == state:
            return True
        time.sleep(0.1)
    else:
        import pdb; pdb.set_trace( )
        assert False, 'Client never reached state %s.' % state


class FactoryWithJID(object):

    class Object(object):
        pass

    authenticator = Object()
    authenticator.jid = JID(u'user@example.com')


class ReactorFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import jarn.xmpp.twisted
        xmlconfig.file('configure.zcml', jarn.xmpp.twisted,
                       context=configurationContext)
        xmlconfig.file('reactor.zcml', jarn.xmpp.twisted,
                      context=configurationContext)

    def testSetUp(self):
        zr = getUtility(IZopeReactor)
        zr.start()

    def testTearDown(self):
        # Clean ZopeReactor
        zr = getUtility(IZopeReactor)
        for dc in zr.reactor.getDelayedCalls():
            if not dc.cancelled:
                dc.cancel()
        zr.stop()

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