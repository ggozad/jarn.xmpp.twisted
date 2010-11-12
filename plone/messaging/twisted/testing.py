from zope.configuration import xmlconfig
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting


class ReactorFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.messaging.twisted
        xmlconfig.file('configure.zcml', plone.messaging.twisted, context=configurationContext)


REACTOR_FIXTURE = ReactorFixture()

REACTOR_INTEGRATION_TESTING = IntegrationTesting(bases=(REACTOR_FIXTURE,), name="ReactorFixture:Integration")
REACTOR_FUNCTIONAL_TESTING = FunctionalTesting(bases=(REACTOR_FIXTURE,), name="ReactorFixture:Functional")
