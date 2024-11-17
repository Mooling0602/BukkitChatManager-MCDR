import os
import shutil

from mcdreforged.api.all import *

psi = ServerInterface.psi()

def unpack_dependency():
    plgdir = os.path.dirname(__file__)
    extra_folder = os.path.join(plgdir, 'extra')
    server_folder = psi.get_mcdr_config()["working_directory"]
    target_folder = f'{server_folder}/plugins'
    if os.path.exists(extra_folder):
        for item in os.listdir(extra_folder):
            item_path = os.path.join(extra_folder, item)
            target_path = os.path.join(target_folder, item)
            if not os.path.exists(target_path):
                shutil.copy(item_path, target_path)
                psi.logger.info(f"解压依赖项[BukkitAPI插件: {item}] 到 {target_folder} 中...")
            else:
                psi.logger.warning(f"依赖项[BukkitAPI插件: {item}] 已经存在于目标目录中，请尝试重启服务器以加载插件")