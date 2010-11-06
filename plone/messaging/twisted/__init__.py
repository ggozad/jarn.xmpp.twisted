from plone.messaging.twisted.subscribers import reactor_installer

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    reactor_installer()
