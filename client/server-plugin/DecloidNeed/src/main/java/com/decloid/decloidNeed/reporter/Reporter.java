package com.decloid.decloidNeed.reporter;

import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class Reporter {

    private static JavaPlugin plugin;
    private static final String SERVER_KEY = System.getenv("SERVER_KEY");
    // BACKEND_URL debe incluir el UUID: ej: https://mi-backend/api/v1/servers/<uuid>/heartbeat/
    private static final String BACKEND_URL = System.getenv("BACKEND_URL");

    // Inicializar con la instancia del plugin (llamar desde onEnable)
    public static void init(JavaPlugin p) {
        plugin = p;
        if (BACKEND_URL == null || SERVER_KEY == null) {
            Bukkit.getLogger().warning("[DecloidNeed] BACKEND_URL o SERVER_KEY no están definidas en el entorno.");
        }
    }

    public static void reportToBackend(String message, int players, double tps) {

        if (plugin == null) {
            Bukkit.getLogger().warning("[DecloidNeed] Reporter no inicializado. Llama Reporter.init(this) en onEnable.");
            return;
        }

        if (BACKEND_URL == null || SERVER_KEY == null) {
            Bukkit.getLogger().warning("[DecloidNeed] Variables de entorno faltantes. Heartbeat no enviado.");
            return;
        }

        // Ejecutar la petición fuera del hilo del servidor
        Bukkit.getScheduler().runTaskAsynchronously(plugin, () -> {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(BACKEND_URL);
                conn = (HttpURLConnection) url.openConnection();

                conn.setRequestMethod("POST");
                conn.setConnectTimeout(5000);
                conn.setReadTimeout(5000);
                conn.setDoOutput(true);

                conn.setRequestProperty("Content-Type", "application/json");
                conn.setRequestProperty("X-Server-Key", SERVER_KEY);

                // BODY: solo players y tps (formato que espera el backend)
                String json = String.format(
                        "{\"players\": %d, \"tps\": %.2f}",
                        players, tps
                );

                try (OutputStream os = conn.getOutputStream()) {
                    os.write(json.getBytes(StandardCharsets.UTF_8));
                }

                int code = conn.getResponseCode();
                if (code == 200 || code == 204) {
                    // opcional: no loguear cada heartbeat para no llenar logs
                    // Bukkit.getLogger().info("[DecloidNeed] Heartbeat OK");
                } else if (code >= 400 && code < 500) {
                    Bukkit.getLogger().warning("[DecloidNeed] Heartbeat rechazado por backend. Código: " + code);
                } else {
                    Bukkit.getLogger().warning("[DecloidNeed] Error al enviar heartbeat. Código: " + code);
                }

            } catch (Exception e) {
                Bukkit.getLogger().warning("[DecloidNeed] Error enviando heartbeat: " + e.getMessage());
            } finally {
                if (conn != null) {
                    conn.disconnect();
                }
            }
        });
    }
}
