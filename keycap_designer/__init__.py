try:
    from ._version import version
    __version_info__ = version
except ImportError:
    __version_info__ = version = '0.0.dev1'

__version__ = '.'.join(map(str, __version_info__))
