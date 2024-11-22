package com.Mooling0602.PlayerLog;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.plugin.java.JavaPlugin;

public class LogInterceptor extends JavaPlugin implements Listener {

    @Override
    public void onEnable() {
        // 注册事件监听器
        Bukkit.getPluginManager().registerEvents(this, this);
        getLogger().info(ChatColor.GREEN + "PlayerLog 已启用！" + ChatColor.stripColor(""));
    }

    @Override
    public void onDisable() {
        getLogger().info(ChatColor.RED + "PlayerLog 已禁用！" + ChatColor.stripColor(""));
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        // 阻止玩家上线消息在游戏内显示
        event.setJoinMessage(null);
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        // 阻止玩家下线消息在游戏内显示
        event.setQuitMessage(null);
    }

    @EventHandler
    public void onPlayerChat(AsyncPlayerChatEvent event) {
        event.setCancelled(true);
        getLogger().info(ChatColor.stripColor("<" + event.getPlayer().getName() + "> " + event.getMessage()));
    }
}