import re
from mcdreforged.api.all import *
from bkchat_manager.config import load_config, config
from bkchat_manager.installer import unpack_dependency

def on_load(server: PluginServerInterface, prev_module):
    load_config(server)
    unpack_dependency()

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
                server.say(formatted_message)

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
                server.say(formatted_message)

def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    joinTip = config.format.join
    formatted_joinTip = joinTip.replace('%player%', player)
    server.say(formatted_joinTip)

def on_player_left(server: PluginServerInterface, player: str):
    leftTip = config.format.left
    formatted_leftTip = leftTip.replace('%player%', player)
    server.say(formatted_leftTip)