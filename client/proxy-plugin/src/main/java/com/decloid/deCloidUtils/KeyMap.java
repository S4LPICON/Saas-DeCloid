package com.decloid.deCloidUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class KeyMap {

    private static final Map<String, UUID> keyToUUID = new HashMap<>();

    static {
        // 🔥 Aquí defines tus claves
        keyToUUID.put("skywars", UUID.fromString("f4074b11-2de1-4005-b179-e7b7564364cb"));
        keyToUUID.put("bedwars", UUID.fromString("dd4671c4-f404-4626-93a8-3ba226cea4a9"));
        keyToUUID.put("prueba3", UUID.fromString("a8dacc48-bf53-4df5-b3d7-1be6a1c34b90"));
    }

    public static UUID getUUID(String key) {
        return keyToUUID.get(key.toLowerCase());
    }
}
