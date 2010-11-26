import unittest2 as unittest
from zope.component import getUtility
from twisted.internet import defer
from plone.messaging.twisted.testing import REACTOR_INTEGRATION_TESTING
from plone.messaging.twisted.interfaces import IZopeReactor

class ReactorTests(unittest.TestCase):

    layer = REACTOR_INTEGRATION_TESTING

    def test_reactor_alive(self):
        zr = getUtility(IZopeReactor)
        self.failUnless(zr.reactor.running)

    def test_stop_start(self):
        zr = getUtility(IZopeReactor)
        zr.stop()
        self.failIf(zr.reactor.running)
        # Start again
        zr.start()
        self.failUnless(zr.reactor.running)

