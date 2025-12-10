package com.decloid.deCloidUtils;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public class OrchestratorClient {

    private final String baseUrl;

    public OrchestratorClient(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public CompletableFuture<DynamicServerInfo> requestServer(UUID artifactUUID, int ownerId) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String fullUrl = baseUrl + "/get-server?artifact_id=" + artifactUUID + "&owner_id=" + ownerId;
                System.out.println("Llamando: " + fullUrl);

                URL url = new URL(fullUrl);
                HttpURLConnection con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");
                con.setConnectTimeout(3000);
                con.setReadTimeout(3000);

                int status = con.getResponseCode();
                BufferedReader reader;

                if (status >= 200 && status < 300) {
                    reader = new BufferedReader(new InputStreamReader(con.getInputStream()));
                } else {
                    reader = new BufferedReader(new InputStreamReader(con.getErrorStream()));
                    String error = reader.lines().collect(Collectors.joining());
                    throw new RuntimeException("Error del backend: HTTP " + status + " → " + error);
                }

                String json = reader.lines().collect(Collectors.joining());
                System.out.println("Respuesta del orquestador: " + json);

                JSONObject obj = new JSONObject(json);
                return new DynamicServerInfo(obj.getString("ip_address"), obj.getInt("port"));

            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
    }

}
