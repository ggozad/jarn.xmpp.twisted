Introduction
============

``plone.messaging.twisted`` provides a basis for building XMPP applications with Plone.

In short, ``plone.messaging.twisted`` includes:

* Extensions to the `wokkel`_ package by implementing parts of the following XMPP extensions:

  * `XEP-0071`_ XHTML-IM.
  * `XEP-0144`_ Roster Item Exchange.
  * `XEP-0060`_ Publish-Subscribe.
  * `XEP-0248`_ PubSub Collection Nodes.
  * `XEP-0133`_ Service Administration.

* A `Twisted`_ reactor that runs side-by-side with the Zope instance.
* Utilities that provide XMPP clients of two sorts, a *deferred* client that initially connects, executes a task and disconnects as soon as it is done, as well as a normal client that remains connected and can respond to XMPP events.

.. _Twisted: http://twistedmatrix.com
.. _wokkel: http://wokkel.ik.nu
.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html