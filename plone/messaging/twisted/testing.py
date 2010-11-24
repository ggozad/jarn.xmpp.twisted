from zope.configuration import xmlconfig
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting


from zope.component import getUtility, getSiteManager
from plone.messaging.twisted.interfaces import IZopeReactor
from plone.messaging.twisted.reactor import ZopeReactor

class ReactorFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.messaging.twisted
        xmlconfig.file('configure.zcml', plone.messaging.twisted, context=configurationContext)
        gsm = getSiteManager()
        zr = getUtility(IZopeReactor)
        #import pdb; pdb.set_trace( )
        #zr.stop()
        #gsm.unregisterUtility(zr)

    def testSetUp(self):
        #pass
        #gsm = getSiteManager()
        #gsm.registerUtility(ZopeReactor())
        zr = getUtility(IZopeReactor)
        from plone.messaging.twisted.interfaces import ReactorStarted
        from zope.event import notify
        notify(ReactorStarted(zr.reactor))
        # #zr.start()
        #import pdb; pdb.set_trace( )
    #def testTearDown(self):
        #pass
        #zr = getUtility(IZopeReactor)
        #zr.stop()
        #gsm = getSiteManager()
        #gsm.unregisterUtility(zr)

REACTOR_FIXTURE = ReactorFixture()

REACTOR_INTEGRATION_TESTING = IntegrationTesting(bases=(REACTOR_FIXTURE,), name="ReactorFixture:Integration")
REACTOR_FUNCTIONAL_TESTING = FunctionalTesting(bases=(REACTOR_FIXTURE,), name="ReactorFixture:Functional")
