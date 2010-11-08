import threading
import logging
from zope.interface import implements
from zope.event import notify
from zope.component.interfaces import ObjectEvent
import  twisted.internet.selectreactor
from plone.messaging.twisted.interfaces import IZopeReactor
from plone.messaging.twisted.interfaces import IReactorStarted, ReactorStarted

logger = logging.getLogger('plone.messaging.twisted')


class ZopeReactor(object):

    implements(IZopeReactor)

    def __init__(self,
                 reactor_factory=twisted.internet.selectreactor.SelectReactor):

        self.reactor = reactor_factory()

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
        self.reactor.callLater(2, self.reactorPoll)

    def reactorPoll(self):
        logger.info("Twisted poll")
        self.reactor.callLater(2, self.reactorPoll)

