import re

from strip_ansi import strip_ansi
from typing import List
from typing_extensions import override
from mcdreforged.utils import string_utils
from mcdreforged.info_reactor.info import InfoSource, Info
from mcdreforged.handler.impl import BukkitHandler

class CustomHandler(BukkitHandler):
    def get_name(self) -> str:
        return 'bkchat_manager_handler'

    # 从服务器标准输出中解析不含ANSI转义序列的文本日志结果
    @classmethod
    def get_server_stdout_raw_result(cls, text: str) -> Info:
        if type(text) is not str:
            raise TypeError('The text to parse should be a string')
        result = Info(InfoSource.SERVER, text)
        result.content = strip_ansi(string_utils.clean_console_color_code(text))
        return result

    __player_name_regex = re.compile(r'^[.\w]{3,16}$')

    @classmethod
    def _verify_player_name(cls, name: str):
        return cls.__player_name_regex.fullmatch(name) is not None

    # 获取玩家消息解析的正则表达式模式列表
    @classmethod
    @override
    def get_player_message_parsing_formatter(cls) -> List[re.Pattern]:
        regex = r'(\[PlayerLog] )?<(?P<name>[^>]+)> (?P<message>.*)'
        return [re.compile(regex)]

    # 准确的玩家下线识别
    __player_left_regex = re.compile(r'(?P<name>[^ ]+) lost connection: (.+)')

    @override
    def parse_player_left(self, info: Info):
        if not info.is_user:
            if (m := self.__player_left_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return m['name']
        return None