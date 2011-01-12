from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from twisted.words.protocols.jabber.jid import JID
from zope.configuration import xmlconfig


class FactoryWithJID(object):

    class Object(object):
        pass

    authenticator = Object()
    authenticator.jid = JID(u'user@example.com')


class ReactorFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import plone.messaging.twisted
        xmlconfig.file('configure.zcml', plone.messaging.twisted,
                       context=configurationContext)


REACTOR_FIXTURE = ReactorFixture()

REACTOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REACTOR_FIXTURE, ), name="ReactorFixture:Integration")
REACTOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REACTOR_FIXTURE, ), name="ReactorFixture:Functional")
