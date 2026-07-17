from __future__ import annotations

from mcdreforged.api.all import PluginServerInterface, Serializable


class formatConfig(Serializable):
    chat: str | dict = r"§7[服内聊天] §a%player% §6>>§r %message%"
    command: str = r"§7[%src_prefix%] §a%player%提交了指令§6：§r %message%"
    join: str = r"§a[+]§r %player%"
    left: str = r"§c[-]§r %player%"


class commandConfig(Serializable):
    feedback: bool = True
    broadcast: bool = False


class downloadConfig(Serializable):
    file_name_regex: str = r"PlayerLog-(\d+(?:\.\d+)*)\.jar"
    file_sha256: str = (
        "6612167f528ed970d4feaa01de5320bfb111a32ac2f594e2e013f1cf904b272b"
    )
    force_hash_check: bool = True


class mainConfig(Serializable):
    format: formatConfig = formatConfig()
    command: commandConfig = commandConfig()
    bukkit_plugin_version_limit: str = ">=2.0"  # empty to disable check
    bukkit_plugin_management: downloadConfig = downloadConfig()


def get_config(server: PluginServerInterface) -> mainConfig:
    config: mainConfig = server.load_config_simple(target_class=mainConfig)  # ty:ignore[invalid-assignment]
    return config
