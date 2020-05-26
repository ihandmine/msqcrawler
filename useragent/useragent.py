
class BaseUserAgent:
    _INSTANCE = None
    WIN_SYSTEM = [
        'Windows NT 5.0',
        'Windows NT 5.1',
        'Windows NT 6.0',
        'Windows NT 6.1',
        'Windows NT 6.2',
        'Windows NT 6.3',
        'Windows NT 10.0',
    ]
    WIN_SYSTEM_BIT = [
        'Win64; x64',
        'WOW64',
    ]
    MAC_SYSTEM = [
        'Macintosh',
    ]
    MAC_SYSTEM_BIT = [
        'PPC Mac OS X',
        'Intel Mac OS X'
    ]
    LINUX_SYSTEM = [
        'X11'
    ]
    LINUX_SYSTEM_BIT = [
        'Linux ppc',
        'Linux ppc64',
        'Linux i686',
        'Linux x86_64',
    ]

    BASE_USER_AGENT_CHROME = 'Mozilla/5.0 (%(system_info)s; %(system_bit)s) ' \
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome' \
                      '/%(big_version)d.%(mid_version)d.%(small_version)d.%(beta_version)d'

    def __new__(cls, *args, **kwargs):
        if not cls._INSTANCE:
            cls._INSTANCE = super().__new__(cls)
        return cls._INSTANCE


class UserAgent(BaseUserAgent):

    def __init__(self, *args, **kwargs):
        pass

