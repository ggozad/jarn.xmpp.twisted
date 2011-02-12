import commands
import os
import time

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


def wait_on_client_deferreds(client, seconds=10):
    while client.xmlstream.iqDeferreds:
        time.sleep(0.1)


def wait_for_client_state(client, state, seconds=10):
    for i in range(seconds*10):
        if client.state == state:
            return True
        time.sleep(0.1)
    else:
        assert False, 'Client never reached state %s.' % state


class FactoryWithJID(object):

    class Object(object):
        pass

    authenticator = Object()
    authenticator.jid = JID(u'user@example.com')


class EJabberdLayer(Layer):

    def setUp(self):
        """Start ejabberd
        Hopefully, the tests are run through the current buildout, which also
        installs ejabberd...
        """
        if 'EJABBERDCTL' in os.environ:
            self.ejabberdctl = os.environ['EJABBERDCTL']
        else:
            print """
            You need to make available a running ejabberd server in order
            to run the functional tests, as well as give the user with JID
            admin@localhost and password 'admin' administrator privileges.
            Make sure the environment variable EJABBERDCTL is set pointing to
            the ejabberdctl command path. Aborting tests...
            """
            exit(1)

        # Start ejabberd
        start = "%s start" % self.ejabberdctl
        out = commands.getoutput(start)
        if out:
            print "Problem starting ejabberd"
            exit(1)
        time.sleep(1.0)

    def tearDown(self):
        # Stop ejabberd
        stop = "%s stop" % self.ejabberdctl
        commands.getoutput(stop)


EJABBERD_LAYER = EJabberdLayer()


class ReactorFixture(PloneSandboxLayer):

    defaultBases = (EJABBERD_LAYER, PLONE_FIXTURE, )

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
