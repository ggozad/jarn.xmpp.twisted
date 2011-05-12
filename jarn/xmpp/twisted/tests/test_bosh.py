import random
import unittest2 as unittest

from twisted.words.protocols.jabber.jid import JID

from jarn.xmpp.twisted.httpb import BOSHClient
from jarn.xmpp.twisted.testing import REACTOR_INTEGRATION_TESTING


class ClientNetworkTest(unittest.TestCase):

    layer = REACTOR_INTEGRATION_TESTING
    level = 2

    def test_bosh_authentication(self):
        jid = JID('admin@localhost')
        jid.resource = str(random.randint(0, 1000))
        client = BOSHClient(jid, 'admin', 'http://localhost:5280/http-bind/')
        self.assertTrue(client.startSession())
        rid = client.rid
        sid = client.sid
        self.assertTrue(rid is not None)
        self.assertTrue(sid is not None)
