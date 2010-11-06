import threading
import logging
import  twisted.internet.selectreactor

logger = logging.getLogger('plone.messaging.twisted')

class ReactorInstaller(object):
    def __init__(self, reactor_factory=twisted.internet.selectreactor.SelectReactor):
        self.reactor_factory = reactor_factory

    def __call__(self):
        self.reactor = self.reactor_factory()

        def start():
            logger.info("Starting Twisted reactor...")
            self.reactor.run(installSignalHandlers=0)

        self.thread = threading.Thread(target=start)
        self.thread.setDaemon(True)
        self.thread.start()

        self.reactor.callWhenRunning(self.reactorStarted)

    def reactorStarted(self):
        logger.info("Twisted reactor started")
        self.reactor.callLater(2,self.reactorPoll)

    def reactorPoll(self):
        logger.info("Twisted poll")
        self.reactor.callLater(2,self.reactorPoll)


reactor_installer = ReactorInstaller()
