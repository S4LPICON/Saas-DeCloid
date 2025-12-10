package com.decloid.deCloidUtils;

import com.google.inject.Inject;
import com.velocitypowered.api.event.Subscribe;
import com.velocitypowered.api.event.proxy.ProxyInitializeEvent;
import com.velocitypowered.api.plugin.Plugin;
import com.velocitypowered.api.proxy.ProxyServer;
import org.slf4j.Logger;

@Plugin(
        id = "decloidutils",
        name = "DeCloidUtils",
        version = BuildConstants.VERSION
)
public class DeCloidUtils {

    private final ProxyServer server;
    private final Logger logger;


    @Inject
    public DeCloidUtils(ProxyServer server, Logger logger) {
        this.server = server;
        this.logger = logger;
    }

    @Subscribe
    public void onInit(ProxyInitializeEvent e) {
        logger.info("DeCloidUtils iniciado.");

        server.getCommandManager().register(
                server.getCommandManager().metaBuilder("getserver").build(),
                new GetServerCommand(server)
        );
        server.getCommandManager().register(
                server.getCommandManager().metaBuilder("unregisterserver").build(),
                new StopServerCommand(server)
        );
    }
}
