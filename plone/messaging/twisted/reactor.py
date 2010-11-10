import threading
import logging
from zope.interface import implements
from zope.event import notify
import  twisted.internet.selectreactor
from plone.messaging.twisted.interfaces import IZopeReactor
from plone.messaging.twisted.interfaces import ReactorStarted

logger = logging.getLogger('plone.messaging.twisted')


class ZopeReactor(object):

    implements(IZopeReactor)

    def __init__(self,
                 reactor_factory=twisted.internet.selectreactor.SelectReactor,
                 poll_interval=0):

        self.reactor = reactor_factory()
        self.poll_interval = poll_interval
        def start():
            logger.info("Starting Twisted reactor...")
            self.reactor.run(installSignalHandlers=0)

        self.thread = threading.Thread(target=start)
        self.thread.setDaemon(True)
        self.thread.start()

        self.reactor.callWhenRunning(self.reactorStarted)

    def reactorStarted(self):
        logger.info("Twisted reactor started")
        event = ReactorStarted(self.reactor)
        notify(event)
        if self.poll_interval:
            self.reactor.callLater(self.poll_interval, self.reactorPoll)

    def reactorPoll(self):
        logger.info("Twisted poll")
        self.reactor.callLater(self.poll_interval, self.reactorPoll)