package com.decloid.decloidNeed.extractor;

import org.bukkit.Bukkit;

public class Extrator {

    private int players;
    private double tps;

    public void updateStats() {
        this.players = Bukkit.getOnlinePlayers().size();
        this.tps = Bukkit.getServer().getTPS()[0];
    }

    public int getPlayers() {
        return players;
    }

    public double getTps() {
        return tps;
    }
}
