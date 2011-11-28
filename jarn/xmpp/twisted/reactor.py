import atexit
import logging
import threading

from jarn.xmpp.twisted.interfaces import IZopeReactor
from jarn.xmpp.twisted.interfaces import ReactorStarted, ReactorStoped
import  twisted.internet.selectreactor
from zope.event import notify
from zope.interface import implements

logger = logging.getLogger('jarn.xmpp.twisted')


class ZopeReactor(object):

    implements(IZopeReactor)

    def __init__(self,
                 reactor_factory=twisted.internet.selectreactor.SelectReactor,
                 poll_interval=1):
        self.reactor = reactor_factory()
        self.poll_interval = poll_interval
        self.start()

    def start(self):
        if self.reactor.running:
            return

        def run_reactor():
            logger.info("Starting Twisted reactor...")
            self.reactor.callWhenRunning(self.reactorStarted)
            self.reactor.run(installSignalHandlers=0)

        atexit.register(self.stop)
        self.thread = threading.Thread(target=run_reactor)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        """This will stop the running reactor. NEVER call it, it's
        only useful for tests.
        """
        if not self.reactor.running:
            return
        self.reactor.callFromThread(self.reactor.stop)
        self.thread.join(3)
        if self.thread.isAlive():
            # Not dead yet? Well I guess you will have to!
            self.reactor.callFromThread(self.reactor.crash)
            self.thread.join(3)
        event = ReactorStoped(self.reactor)
        notify(event)

    def reactorStarted(self):
        logger.info("Twisted reactor started")
        event = ReactorStarted(self.reactor)
        notify(event)
        if self.poll_interval:
            self.reactor.callLater(self.poll_interval, self.reactorPoll)

    def reactorPoll(self):
        self.reactor.callLater(self.poll_interval, self.reactorPoll)
