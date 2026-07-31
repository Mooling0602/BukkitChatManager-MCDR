from mcdreforged import (
    CommandContext,
    CommandSource,
    PluginServerInterface,
    RColor,
    RText,
    SimpleCommandBuilder,
    Text,
)

from bkchat_manager.chat import get_player_entity, get_player_rtext

builder = SimpleCommandBuilder()


def command_register(server: PluginServerInterface):
    builder.arg("player", Text)
    builder.register(server)


@builder.command("!!bcm debug player_rtext <player>")
def debug_player_entity(src: CommandSource, ctx: CommandContext):
    server = src.get_server().psi()
    player_name = ctx["player"]
    player = get_player_entity(player_name)
    if src.is_player:
        src.reply("已获取玩家组件，正在返回文本组件结果：")
        src.reply(get_player_rtext(player))
    else:
        src.reply("已获取玩家组件，正在返回文本组件结果：")
        src.reply(RText("你可能需要在游戏内验证实际效果。", RColor.gray))
        server.broadcast(get_player_rtext(player))
