from __future__ import absolute_import, unicode_literals

import logging

try:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
except ImportError:
    from pkg_resources import declare_namespace
    declare_namespace(__name__)

from sdk.wechatpy.parser import parse_message  # NOQA

__version__ = '1.3.1'
__author__ = 'messense'

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
