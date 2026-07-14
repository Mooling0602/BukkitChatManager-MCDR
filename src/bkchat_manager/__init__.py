import re

from mcdreforged.api.all import *

import bkchat_manager.runtime as rt
from bkchat_manager.config import get_config
from bkchat_manager.handler import CustomHandler
from bkchat_manager.installer import install_bukkit_plugin
from bkchat_manager.utils import execute_if


def on_load(server: PluginServerInterface, _):
    rt.config = get_config(server)
    server.logger.warning(
        "0.3.1以后的版本不再内置Bukkit服务端插件，你需要在新的自动安装器实现之前（即0.4.0以前的版本）手动下载安装到服务端中。"
    )
    install_bukkit_plugin(server)
    server.logger.info("内置处理器强制启用，正在尝试进行注册...")
    server.register_server_handler(CustomHandler())
    server.logger.warning(
        "混用多个服务端处理器会导致错误，可以手动卸载或禁用其他服务端处理器插件！"
    )
    server.logger.info("若插件内置的处理器造成异常，请及时前往GitHub Issues进行反馈！")
    if server.is_server_running():
        on_server_startup(server)


def on_server_startup(server: PluginServerInterface):
    if rt.config.compatibility_mode is not True:
        server.execute("chatmsg off")
    else:
        server.execute("chatmsg on")
        server.logger.info(
            "§a兼容模式已开启§r，此MCDR插件的功能将关闭，你可以使用其他可以修改聊天内容格式的服务端插件！"
        )
        server.logger.info(
            "控制台会产生两条内容重复的聊天日志，目前这个体验问题无法解决，但是§a此MCDR插件内置的处理器会正确进行解析，不会有负面影响！§r"
        )


@execute_if(lambda: rt.config.compatibility_mode is False)
def on_user_info(server: PluginServerInterface, info: Info):
    if info.content == "" or not info.content:
        return
    player = info.player
    message = info.content
    if player is not None:
        if not info.content.startswith("!!"):
            chat_format = rt.config.format.chat
            if isinstance(chat_format, str):
                formatted_message = chat_format.replace("%player%", player).replace(
                    "%message%", message
                )
                server.say(formatted_message)
            elif isinstance(chat_format, dict):
                formatted_message = str(chat_format).replace("'", '"')
                server.logger.info(formatted_message)
                server.execute(f"tellraw @a {formatted_message}")
        else:
            src_prefix = "MCDR"
            command_format = rt.config.format.command
            if rt.config.command.feedback and not rt.config.command.broadcast:
                formatted_message = (
                    command_format
                    .replace("%src_prefix%", src_prefix)
                    .replace("%player%", "您")
                    .replace("%message%", message)
                )
                server.tell(player, formatted_message)
            if rt.config.command.broadcast:
                formatted_message = (
                    command_format
                    .replace("%src_prefix%", src_prefix)
                    .replace("%player%", player)
                    .replace("%message%", message)
                )
                server.say(formatted_message)


@execute_if(lambda: rt.config.compatibility_mode is False)
def on_info(server: PluginServerInterface, info: Info):
    if not info.is_from_server or not isinstance(info.content, str):
        return
    match = re.fullmatch(r"(.+) issued server command: (.+)", info.content)
    if match:
        player = match.group(1)
        command = match.group(2)
        src_prefix = "Server"
        command_format = rt.config.format.command
        if rt.config.command.feedback and not rt.config.command.broadcast:
            formatted_message = (
                command_format
                .replace("%src_prefix%", src_prefix)
                .replace("%player%", "您")
                .replace("%message%", command)
            )
            server.tell(player, formatted_message)
        if rt.config.command.broadcast:
            formatted_message = (
                command_format
                .replace("%src_prefix%", src_prefix)
                .replace("%player%", player)
                .replace("%message%", command)
            )
            server.say(formatted_message)


@execute_if(lambda: rt.config.compatibility_mode is False)
def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    joinTip = rt.config.format.join
    formatted_joinTip = joinTip.replace("%player%", player)
    server.say(formatted_joinTip)


@execute_if(lambda: rt.config.compatibility_mode is False)
def on_player_left(server: PluginServerInterface, player: str):
    leftTip = rt.config.format.left
    formatted_leftTip = leftTip.replace("%player%", player)
    server.say(formatted_leftTip)
