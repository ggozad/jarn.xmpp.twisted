import threading
import logging
from zope.interface import implements
from zope.event import notify
import  twisted.internet.selectreactor
from plone.messaging.twisted.interfaces import IZopeReactor
from plone.messaging.twisted.interfaces import ReactorStarted, ReactorStoped

logger = logging.getLogger('plone.messaging.twisted')


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
            self.reactor.run(installSignalHandlers=0)
        self.thread = threading.Thread(target=run_reactor)
        self.thread.setDaemon(True)
        self.thread.start()
        self.reactor.callWhenRunning(self.reactorStarted)

    def stop(self):
        if not self.reactor.running:
            return
        self.reactor.callFromThread(self.reactor.stop)
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
        #logger.info("Twisted poll")
        self.reactor.callLater(self.poll_interval, self.reactorPoll)
