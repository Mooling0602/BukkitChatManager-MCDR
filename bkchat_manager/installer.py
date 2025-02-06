import os

from mcdreforged.api.all import *


psi = ServerInterface.psi()
server_folder = psi.get_mcdr_config()["working_directory"]
bukkit_plg_folder = os.path.join(server_folder, 'plugins')

def extract_file():
    old_plg_files = ['PlayerLog.jar', 'PlayerLog-1.1.jar']
    old_plg_list = []
    for i in old_plg_files:
        i_new = os.path.join(bukkit_plg_folder, i)
        old_plg_list.append(i_new)
    if old_plg_list is not None:
        for i in old_plg_list:
            if os.path.isfile(i):
                psi.logger.info(f"检测到存在于{i}下的旧版本Bukkit插件依赖，正在尝试删除！")
                os.remove(i)
    dependency_path = os.path.join('extra', 'PlayerLog-1.2.jar')
    target_path = os.path.join(bukkit_plg_folder, os.path.basename(dependency_path))
    with psi.open_bundled_file(dependency_path) as file_handler:
        with open(target_path, 'wb') as target_file:
            target_file.write(file_handler.read())
            psi.logger.info("BukkitAPI插件依赖项（新版本）解压完成，若出现玩家消息重复等异常情况，重启游戏服务端使插件加载即可。")