import re

from mcdreforged.api.all import Info, PluginServerInterface

import bkchat_manager.runtime as rt
from bkchat_manager.config import get_config
from bkchat_manager.installer import install_bukkit_plugin


def on_load(server: PluginServerInterface, _):
    rt.psi = server
    rt.config = get_config(server)
    server.logger.warning(
        "0.3.1以后的版本不再内置Bukkit服务端插件，你需要在新的自动安装器实现之前（即0.4.0以前的版本）手动下载安装到服务端中。"
    )
    rt.bukkit_plugin_ready = install_bukkit_plugin()
    if not rt.bukkit_plugin_ready:
        server.logger.error("Bukkit 插件未就绪，BukkitChatManager 功能不会启动。")
        return
    if server.is_server_running():
        on_server_startup(server)


def on_server_startup(server: PluginServerInterface):
    if not rt.bukkit_plugin_ready:
        return
    server.execute("playerlog on")


def on_user_info(server: PluginServerInterface, info: Info):
    if not rt.bukkit_plugin_ready:
        return
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


def on_info(server: PluginServerInterface, info: Info):
    if not rt.bukkit_plugin_ready:
        return
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


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    if not rt.bukkit_plugin_ready:
        return
    joinTip = rt.config.format.join
    formatted_joinTip = joinTip.replace("%player%", player)
    server.say(formatted_joinTip)


def on_player_left(server: PluginServerInterface, player: str):
    if not rt.bukkit_plugin_ready:
        return
    leftTip = rt.config.format.left
    formatted_leftTip = leftTip.replace("%player%", player)
    server.say(formatted_leftTip)
