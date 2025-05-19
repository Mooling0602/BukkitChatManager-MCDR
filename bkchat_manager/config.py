from mcdreforged.api.all import *


class formatConfig(Serializable):
    chat: str|dict = r'§7[服内聊天] §a%player% §6>>§r %message%'
    command: str = r'§7[%src_prefix%] §a%player%提交了指令§6：§r %message%'
    join: str = r'§a[+]§r %player%'
    left: str = r'§c[-]§r %player%'

class commandConfig(Serializable):
    feedback: bool = True
    broadcast: bool = False

class mainConfig(Serializable):
    compatibility_mode: bool = False
    format: formatConfig = formatConfig()
    command: commandConfig = commandConfig()

config: mainConfig

def load_config(server: PluginServerInterface):
    global config
    config = server.load_config_simple(target_class=mainConfig)