package com.decloid.decloidNeed;

import com.decloid.decloidNeed.extractor.Extrator;
import com.decloid.decloidNeed.reporter.Reporter;
import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;

public final class DecloidNeed extends JavaPlugin {

    private final Extrator extractor = new Extrator();

    // Configuración
    private final int intervalSeconds = 5;        // cada X segundos se envía heartbeat
    private final int minPlayersThreshold = 2;
    private final int inactiveThresholdMinutes = 1;
    private int inactiveSecondsCounter = 0;

    @Override
    public void onEnable() {
        Bukkit.getLogger().info("[DecloidNeed] Iniciado correctamente.");

        // Inicializar Reporter con la instancia del plugin
        Reporter.init(this);

        new BukkitRunnable() {
            @Override
            public void run() {

                extractor.updateStats();
                int players = extractor.getPlayers();
                double tps = extractor.getTps();

                //------ LÓGICA DE INACTIVIDAD ------
                if (players <= minPlayersThreshold) {
                    inactiveSecondsCounter += intervalSeconds;
                } else {
                    inactiveSecondsCounter = 0;
                }

                if (inactiveSecondsCounter >= inactiveThresholdMinutes * 60) {

                    String warn = "⚠ Servidor inactivo por " + inactiveThresholdMinutes +
                            " minuto(s). Jugadores: " + players;

                    Reporter.reportToBackend(warn, players, tps);

                    inactiveSecondsCounter = 0;
                    return;
                }
                //-----------------------------------

                String msg = "HB → players=" + players + " | tps=" + String.format("%.2f", tps);

                Reporter.reportToBackend(msg, players, tps);
            }
        }.runTaskTimer(this, 0L, intervalSeconds * 20L);
    }

    @Override
    public void onDisable() {
        Bukkit.getLogger().info("[DecloidNeed] Detenido.");
    }
}
