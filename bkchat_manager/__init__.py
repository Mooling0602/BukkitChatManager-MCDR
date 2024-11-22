import re
import bkchat_manager.config
from mcdreforged.api.all import *
from bkchat_manager.config import load_config
from bkchat_manager.installer import extract_file
from bkchat_manager.handler import CustomHandler

def on_load(server: PluginServerInterface, prev_module):
    global config
    load_config(server)
    config = bkchat_manager.config.config
    if config.builtin_handler:
        server.logger.info("内置处理器已启用，正在尝试进行注册...")
        server.register_server_handler(CustomHandler())
        server.logger.warning("混用多个服务端处理器会导致错误，可以手动卸载或禁用其他服务端处理器插件！")
        server.logger.info("如果你有适用的服务端处理器，你可以在配置文件内禁用此插件的builtin_handler，以使用该处理器")
    extract_file()

def on_user_info(server: PluginServerInterface, info: Info):
    global config
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
    global config
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
    global config
    joinTip = config.format.join
    formatted_joinTip = joinTip.replace('%player%', player)
    server.say(formatted_joinTip)

def on_player_left(server: PluginServerInterface, player: str):
    global config
    leftTip = config.format.left
    formatted_leftTip = leftTip.replace('%player%', player)
    server.say(formatted_leftTip)