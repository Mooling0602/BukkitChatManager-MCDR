import os

from mcdreforged.api.all import *


psi = ServerInterface.psi()
server_folder = psi.get_mcdr_config()["working_directory"]
bukkit_plg_folder = os.path.join(server_folder, 'plugins')

def extract_file():
    old_plg = os.path.join(bukkit_plg_folder, 'PlayerLog.jar')
    if os.path.isfile(old_plg):
        psi.logger.info("检测到旧版本Bukkit插件依赖，正在尝试删除并替换新版本！")
        os.remove(old_plg)
    dependency_path = os.path.join('extra', 'PlayerLog-1.1.jar')
    target_path = os.path.join(bukkit_plg_folder, os.path.basename(dependency_path))
    with psi.open_bundled_file(dependency_path) as file_handler:
        with open(target_path, 'wb') as target_file:
            target_file.write(file_handler.read())
            psi.logger.info("BukkitAPI插件依赖项解压完成，若出现玩家消息重复等异常情况，重启游戏服务端即可。")