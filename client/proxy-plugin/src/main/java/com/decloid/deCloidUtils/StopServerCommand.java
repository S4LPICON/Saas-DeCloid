package com.decloid.deCloidUtils;

import com.velocitypowered.api.command.SimpleCommand;
import com.velocitypowered.api.proxy.ProxyServer;
import com.velocitypowered.api.proxy.server.RegisteredServer;
import com.velocitypowered.api.proxy.server.ServerInfo;
import net.kyori.adventure.text.Component;

import java.util.Optional;

public class StopServerCommand implements SimpleCommand {

    private final ProxyServer proxy;

    public StopServerCommand(ProxyServer proxy) {
        this.proxy = proxy;
    }

    @Override
    public void execute(Invocation invocation) {
        String name = "dynamic-25567"; // cambia esto a tu server dinámico

        Optional<RegisteredServer> serverOpt = proxy.getServer(name);

        if (serverOpt.isEmpty()) {
            invocation.source().sendMessage(
                    Component.text("❌ No existe el servidor: " + name)
            );
            return;
        }

        RegisteredServer registered = serverOpt.get();

        proxy.unregisterServer(registered.getServerInfo());

        invocation.source().sendMessage(
                Component.text("🛑 Servidor " + name + " desregistrado.")
        );
    }
}
