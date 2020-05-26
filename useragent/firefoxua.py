from random import randint, choice as r_choice
from useragent.useragent import UserAgent


class FirefoxUA(UserAgent):
    """
    Mozilla/5.0 是一个通用标记符号，用来表示与 Mozilla 兼容，这几乎是现代浏览器的标配。
    platform 用来说明浏览器所运行的原生系统平台（例如 Windows、Mac、Linux 或 Android），以及是否运行在手机上。搭载 Firefox OS 的手机仅简单地使用了 "Mobile" 这个字符串；因为 web 本身就是平台。注意 platform 可能会包含多个使用 "; " 隔开的标记符号。参见下文获取更多的细节信息及示例。
    rv:geckoversion 表示 Gecko 的发布版本号（例如  "17.0"）。在近期发布的版本中，geckoversion 表示的值与 firefoxversion 相同。
    Gecko/geckotrail 表示该浏览器基于 Gecko 渲染引擎。
    在桌面浏览器中， geckotrail  是固定的字符串 "20100101" 。
    Firefox/firefoxversion 表示该浏览器是 Firefox，并且提供了版本号信息（例如  "17.0"）。

    eg: Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion

    example:
        Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0
        Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0

    platform:
        windows
        mac
        linux
    """
    BASE_USER_AGENT_FIREFOX = 'Mozilla/5.0 (%(system_info)s; %(system_bit)s; rv:%(r_version)s) Gecko/20100101 Firefox/%(version)s'

    def __init__(self, platform='windows', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if platform == 'windows':
            self.s_info, self.s_bit = self.WIN_SYSTEM, self.WIN_SYSTEM_BIT
        elif platform == 'linux':
            self.s_info, self.s_bit = self.LINUX_SYSTEM, self.LINUX_SYSTEM_BIT
        elif platform == 'mac':
            self.s_info, self.s_bit = self.MAC_SYSTEM, self.MAC_SYSTEM_BIT
        else:
            raise TypeError('Unknown platform type: %s' % platform)
        self.version, self.info, self.bit, self.r_version = float(randint(10, 50)), r_choice(self.s_info), r_choice(self.s_bit), float(randint(10, 50))

    @property
    def ua(self):
        _ua = self.BASE_USER_AGENT_FIREFOX % {
            'system_info': self.info,
            'system_bit': self.bit,
            'r_version': self.r_version,
            'version': self.version
        }
        return _ua

    def __repr__(self):
        return self.ua



