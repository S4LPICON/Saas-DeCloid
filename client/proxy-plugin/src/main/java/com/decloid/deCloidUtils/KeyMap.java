package com.decloid.deCloidUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class KeyMap {

    private static final Map<String, UUID> keyToUUID = new HashMap<>();

    static {
        // 🔥 Aquí defines tus claves
        keyToUUID.put("skywars", UUID.fromString("c8a78d2d-db48-4799-96b4-f83a3e09e0ba"));
        keyToUUID.put("prueba2", UUID.fromString("3fe4f0e0-45a8-4d0a-bfc9-1abcdaec2f88"));
        keyToUUID.put("prueba3", UUID.fromString("a8dacc48-bf53-4df5-b3d7-1be6a1c34b90"));
    }

    public static UUID getUUID(String key) {
        return keyToUUID.get(key.toLowerCase());
    }
}
