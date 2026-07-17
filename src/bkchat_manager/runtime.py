from mcdreforged.api.all import PluginServerInterface, ServerInterface

from .config import mainConfig

psi: PluginServerInterface = ServerInterface.psi()
config: mainConfig = mainConfig()
bukkit_plugin_ready: bool = False
