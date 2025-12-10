package com.decloid.deCloidUtils;

import com.velocitypowered.api.command.SimpleCommand;
import com.velocitypowered.api.proxy.ProxyServer;
import com.velocitypowered.api.proxy.server.RegisteredServer;
import com.velocitypowered.api.proxy.server.ServerInfo;
import net.kyori.adventure.text.Component;

import java.net.InetSocketAddress;
import java.util.UUID;

public class GetServerCommand implements SimpleCommand {

    private final ProxyServer proxy;

    public GetServerCommand(ProxyServer proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(Invocation invocation) {

        String[] args = invocation.arguments();
        if (args.length != 1) {
            invocation.source().sendMessage(Component.text("❌ Uso: /getserver <clave>"));
            return;
        }

        String key = args[0];
        UUID artifactUUID = KeyMap.getUUID(key);

        if (artifactUUID == null) {
            invocation.source().sendMessage(Component.text("❌ Clave desconocida: " + key));
            return;
        }

        invocation.source().sendMessage(Component.text("⏳ Buscando servidor para " + key + "..."));

        OrchestratorClient client = new OrchestratorClient("http://192.168.40.48:8080");
        int ownerId = 1; // temporal
        client.requestServer(artifactUUID, ownerId).whenComplete((server, ex) -> {

            System.out.println("CALLBACK ejecutado!");

            if (ex != null) {
                ex.printStackTrace();
                invocation.source().sendMessage(Component.text("❌ Error solicitando servidor."));
                return;
            }

            if (server == null) {
                invocation.source().sendMessage(Component.text("❌ Orquestador no respondió."));
                return;
            }

            System.out.println("Orquestador → " + server.ip_address() + ":" + server.port());

            ServerInfo info = new ServerInfo(
                    "dynamic-" + server.port(),
                    new InetSocketAddress(server.ip_address(), server.port())
            );

            RegisteredServer registered = proxy.registerServer(info);

            invocation.source().sendMessage(Component.text(
                    "🚀 Servidor asignado: dynamic-" + server.port()
            ));
        });
    }
}
