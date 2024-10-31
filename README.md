# BukkitChatManager-MCDR
---
- [en_US]

Manage chat in game for BukkitAPI servers in MCDR.

## Dependency
- BukkitAPI Plugin: [PlayerLog](https://github.com/Mooling0602/BukkitChatManager-MCDR/blob/main/extra/PlayerLog-1.0-SNAPSHOT.jar)

## Usage
Install need BukkitAPI plugin in **Dependency** first, 
> Install this to disable server sent chat messages to clients by default, then the MCDR plugin can manage these messages after.

then install this MCDR plugin from release.

## Configuration
Located in `config/bkchat_manager/config.json`, default config is written by zh_CN, you can edit it to feat your language.

Among them, `%player%` represents the playername; `%message%` represents the chat content or commands player executed; `%src_prefix%` represents the command source, e.g. `MCDR`, `Server`.

## NOTE
Conflicts with similar BukkitAPI chat management plugins, please do not use these same type of plugins!

---
在MCDR接管BukkitAPI服务端的游戏内聊天。

## 依赖
- BukkitAPI 插件：[PlayerLog](https://github.com/Mooling0602/BukkitChatManager-MCDR/blob/main/extra/PlayerLog-1.0-SNAPSHOT.jar)

## 用法
先安装**依赖**部分中的BukkitAPI插件，
> 以禁止服务端默认地向客户端发送聊天消息，然后此MCDR插件就可以接管这些消息并进行处理。

然后从Release中安装此MCDR插件。

## 配置
配置文件位于`config/bkchat_manager/config.json`，你可以在里面修改聊天消息的格式等。

其中，`%player%`表示玩家名；`%message%`表示聊天消息内容或玩家执行的指令内容；`%src_prefix%`表示指令源。

## 注意事项
和类似的BukkitAPI插件冲突，请不要使用这些同类型的插件。

另外，如果有和依赖中作用相同的替代品插件，此MCDR插件可无缝迁移到其他类型的服务端上。
