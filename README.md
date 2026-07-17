# BukkitChatManager-MCDR

在 MCDR 接管服务端内的游戏聊天。

> 目前支持 BukkitAPI，但你也可以接入到其他服务端中。
>
> 由于历史遗留原因，插件名称将继续保留“bukkit”字样。

## 依赖
- BukkitAPI 插件：[PlayerLog](https://github.com/Mooling0602/PlayerLog-Bukkit)

> 此 MCDR 插件会自动管理安装，你可能需要重启服务器以完成重载。

## 用法

从 Release 中安装此MCDR插件，如果出现问题，请确认依赖是否已经正常加载，有报错请反馈到 Issues！

## 配置

配置文件位于 `config/bkchat_manager/config.json`，你可以在里面修改聊天消息的格式等。

其中，`%player%` 表示玩家名；`%message%` 表示聊天消息内容或玩家执行的指令内容；`%src_prefix%` 表示指令源。

## 注意事项

和类似的 BukkitAPI 插件冲突，请不要使用这些同类型的插件。

> 其他服务端同理，不再赘述。

另外，如果有和依赖中作用相同的替代品插件，此 MCDR 插件可无缝迁移到其他类型的服务端上；Mohist等支持 BukkitAPI 的混合端也可以使用。

> 自 v0.4.0 版本起，需要修改配置文件才能使用未经验证的服务端插件。

插件自 v0.4.0 版本起不再需要定制的服务端处理器，你可以根据需要来自行配置。

经过测试的服务端：Mohist、Paper、Leaves、Folia、Luminol（已停止维护）

> 极低版本的服务端尚未测试，理论上支持 1.13 及以上的所有 Bukkit 服务端。
