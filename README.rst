Introduction
============

``jarn.xmpp.twisted`` provides a basis for building XMPP applications with Plone.

In short, ``jarn.xmpp.twisted`` includes:

* Extensions to the `wokkel`_ package by implementing parts of the following XMPP extensions:

  * `XEP-0071`_ XHTML-IM.
  * `XEP-0144`_ Roster Item Exchange.
  * `XEP-0060`_ Publish-Subscribe.
  * `XEP-0248`_ PubSub Collection Nodes.
  * `XEP-0133`_ Service Administration.

* A `Twisted`_ reactor that runs side-by-side with the Zope instance.
* Utilities that provide XMPP clients of two sorts, a *deferred* client that initially connects, executes a task and disconnects as soon as it is done, as well as a normal client that remains connected and can respond to XMPP events.
* An XMPP component base class for writing custom components.

``jarn.xmpp.twisted`` is part of a suite, with the other packages being:

* `jarn.xmpp.core`_, provides facilities for presence, messaging, chatting and microblogging.
* `jarn.xmpp.collaboration`_ provides an XMPP protocol to do real-time collaborative editing as well as a Plone-targeted implementation.


Installation
============

``jarn.xmpp.twisted`` requires a working XMPP server installation. Please refer to the `jarn.xmpp.core`_ documentation on how to set it up.

Testing
=======

Some of the included tests are functional tests that require a XMPP server running on ``localhost`` as well as an administrator account setup up on this server with JID ``admin@localhost`` and password ``admin``. If you wish to run those you have to specify a *level* 2 on your testrunner, i.e.

    ::

    ./bin/test -a 2 -s jarn.xmpp.twisted

Credits
=======

* Most of this work was done using the 10% time available to `Jarn AS`_ employees for the development of open-source projects.

.. _Twisted: http://twistedmatrix.com
.. _wokkel: http://wokkel.ik.nu
.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html
.. _Jarn AS: http://jarn.com
.. _jarn.xmpp.core: http://pypi.python.org/pypi/jarn.xmpp.core
.. _jarn.xmpp.collaboration: http://pypi.python.org/pypi/jarn.xmpp.collaboration
