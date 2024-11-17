import os
import shutil

from mcdreforged.api.all import *

psi = ServerInterface.psi()

def unpack_dependency():
    psi.logger.info("开始解压依赖...")
    plgdir = os.path.dirname(__file__)
    extra_folder = os.path.join(plgdir, 'extra')
    server_folder = psi.get_mcdr_config().get("working_directory", None)
    if server_folder is None:
        server_folder = "server"
    target_folder = f'{server_folder}/plugins'
    psi.logger.info("内置依赖项路径: " + extra_folder)
    if os.access(extra_folder, os.R_OK):
        psi.logger.info("路径可读")
    else:
        psi.logger.error("没有读取权限，无法访问依赖项路径")
    if os.path.exists(extra_folder):
        psi.logger.info("内置依赖项存在")
        for item in os.listdir(extra_folder):
            item_path = os.path.join(extra_folder, item)
            target_path = os.path.join(target_folder, item)
            if not os.path.exists(target_path):
                psi.logger.info(f"解压依赖项[BukkitAPI插件: {item}] 到 {target_folder} 中...")
                shutil.copy(item_path, target_path)
            else:
                psi.logger.warning(f"依赖项[BukkitAPI插件: {item}] 已经存在于目标目录中，请尝试重启服务器以加载插件")
    else:
        psi.logger.info("内置依赖项不存在！！！")