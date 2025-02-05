package com.Mooling0602.PlayerLog;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.ArrayList;
import java.util.List;

public class LogInterceptor extends JavaPlugin implements Listener {

    private boolean chatInterceptEnabled = false; // 默认拦截聊天消息

    @Override
    public void onEnable() {
        Bukkit.getPluginManager().registerEvents(this, this);
        getCommand("chatmsg").setExecutor(this);
        getLogger().info(ChatColor.GREEN + "PlayerLog 已启用！");
    }

    @Override
    public void onDisable() {
        getLogger().info(ChatColor.RED + "PlayerLog 已禁用！");
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        event.setJoinMessage(null);
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        event.setQuitMessage(null);
    }

    @EventHandler
    public void onPlayerChat(AsyncPlayerChatEvent event) {
        if (chatInterceptEnabled) {
            event.setCancelled(true);
            getLogger().info("<" + event.getPlayer().getName() + "> " + event.getMessage());
        }
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (command.getName().equalsIgnoreCase("chatmsg")) {
            if (args.length != 1) {
                sender.sendMessage(ChatColor.YELLOW + "用法: /chatmsg <on/off>");
                return true;
            }
            if (args[0].equalsIgnoreCase("on")) {
                chatInterceptEnabled = false;
                sender.sendMessage(ChatColor.YELLOW + "客户端聊天拦截功能已关闭，若MCDR插件功能未关闭会出现聊天消息重复等异常情况！");
            }
            else if (args[0].equalsIgnoreCase("off")) {
                chatInterceptEnabled = true;
                sender.sendMessage(ChatColor.YELLOW + "客户端聊天拦截功能已开启，MCDR插件可开始接管聊天内容！");
            }
            else {
                sender.sendMessage(ChatColor.YELLOW + "用法: /chatmsg <on/off>");
            }
            return true;
        }
        return false;
    }


    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        List<String> completions = new ArrayList<>();
        if (command.getName().equalsIgnoreCase("chatmsg")) {
            completions.add("on");
            completions.add("off");
        }
        return completions;
    }
}