import re
from mcdreforged.api.all import *

class formatConfig(Serializable):
    chat: str = r'§7[服内聊天] §a%player% §6>>§r %message%'
    command: str = r'§7[%src_prefix%] §a%player%提交了指令§6：§r %message%'

class commandConfig(Serializable):
    feedback: bool = True
    broadcast: bool = False

class mainConfig(Serializable):
    format: formatConfig = formatConfig()
    command: commandConfig = commandConfig()

config: mainConfig

def load_config(server: PluginServerInterface):
    global config
    config = server.load_config_simple(target_class=mainConfig)

def on_load(server: PluginServerInterface, prev_module):
    load_config(server)

def on_user_info(server: PluginServerInterface, info: Info):
    player = info.player
    message = info.content
    if player is not None:
        if not info.content.startswith("!!"):
            chat_format = config.format.chat
            formatted_message = chat_format.replace('%player%', player).replace('%message%', message)
            server.say(formatted_message)
        else:
            src_prefix = "MCDR"
            command_format = config.format.command
            if config.command.feedback:
                if not config.command.broadcast:
                    formatted_message = command_format.replace('%src_prefix%', src_prefix).replace('%player%', "您").replace('%message%', message)
                    server.tell(player, formatted_message)
            if config.command.broadcast:
                formatted_message = command_format.replace('%src_prefix%', src_prefix).replace('%player%', player).replace('%message%', message)
                server.broadcast(formatted_message)


def on_info(server: PluginServerInterface, info: Info):
    if info.is_from_server and re.fullmatch(r'(.+) issued server command: (.+)', info.content):
        match = re.fullmatch(r'(.+) issued server command: (.+)', info.content)
        if match:
            player = match.group(1)
            command = match.group(2)
            src_prefix = "Server"
            command_format = config.format.command
            if config.command.feedback:
                if not config.command.broadcast:
                    formatted_message = command_format.replace('%src_prefix%', src_prefix).replace('%player%', "您").replace('%message%', command)
                    server.tell(player, formatted_message)
            if config.command.broadcast:
                formatted_message = command_format.replace('%src_prefix%', src_prefix).replace('%player%', player).replace('%message%', command)
                server.broadcast(formatted_message)
