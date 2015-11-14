"""
Provides lower level datatypes and functionality.
Most of the functionality is wrapped by modules from the parent package.
"""

# low-level datatypes
from . import deck, card

# platform dependent operations
from . import compat

# computer-specific configuration options
from . import config
