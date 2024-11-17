import os
import shutil

from mcdreforged.api.all import *

psi = ServerInterface.psi()

def extract_file():
    server_folder = psi.get_mcdr_config()["working_directory"]
    bukkit_plg_folder = f"{server_folder}/plugins"
    dependency_path = 'extra/PlayerLog.jar'
    target_path = os.path.join(bukkit_plg_folder, os.path.basename(dependency_path))
    with psi.open_bundled_file('extra/PlayerLog.jar') as file_handler:
        with open(target_path, 'wb') as target_file:
            target_file.write(file_handler.read())
            psi.logger.info("BukkitAPI插件依赖项解压完成，请重启服务器以加载插件。")