import os

from mcdreforged.api.all import ServerInterface

from bkchat_manager import PluginServerInterface

psi = ServerInterface.psi()
server_folder = psi.get_mcdr_config()["working_directory"]
bukkit_plg_folder = os.path.join(server_folder, "plugins")


# TODO
# 将修改为从 GitHub Release 下载相应的 Bukkit 插件，并放置在 server/plugins 文件夹下
def install_bukkit_plugin(server: PluginServerInterface):
    server.logger.info("Please install PlayerLog v1.4 from GitHub release manually.")
    server.logger.info("https://github.com/Mooling0602/PlayerLog-Bukkit/releases/tag/1.4")