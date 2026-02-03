# SaaS-DeCloid ☁️

**DeCloid** es un **Software as a Service (SaaS)** orientado a la **orquestación de instancias de servidores de Minecraft bajo demanda**. El proyecto está diseñado con una **arquitectura moderna de microservicios**, enfocada en eficiencia, escalabilidad y reducción de costos operativos.

Su objetivo es abandonar el modelo tradicional de networks monolíticas siempre encendidas y permitir que los servidores se creen, utilicen y destruyan dinámicamente según la demanda real.

---

## 🧱 Stack tecnológico

El sistema está compuesto por múltiples servicios desacoplados:

* **Arquitectura:** Microservicios
* **Cola de tareas:** Redis
* **Base de datos:** PostgreSQL
* **Contenerización:** Docker
* **Almacenamiento de imágenes:** Docker Registry

### Backend

* **Backend principal:** Django
* **Backends secundarios:** FastAPI
* **Orquestador y workers:** Python

### Frontend

* **Frontend:** Vue.js

### Integración con Minecraft

* **Plugin Proxy (Velocity):**

  * Solicitud de instancias
  * Registro y descubrimiento de servidores

* **Plugin Backend (Paper / Spigot):**

  * Control del ciclo de vida de servidores individuales
  * Comunicación con el backend central

---

## 🎯 Problema que resuelve

Actualmente, en la comunidad de desarrollo de servidores de Minecraft:

* **No existe una solución estándar para la orquestación de servidores efímeros**
* Prácticamente **todas las networks (2026)** utilizan arquitecturas monolíticas
* Muchos servidores backend permanecen activos **24/7 sin jugadores**, consumiendo recursos innecesariamente

Este enfoque tradicional genera:

* Costos elevados
* Escalado ineficiente
* Complejidad operativa

---

## 💡 Propuesta de DeCloid

Con DeCloid:

* Las instancias de servidores se **levantan únicamente cuando son requeridas**
* Cada modalidad o partida puede ejecutarse en un servidor efímero
* Los recursos se utilizan de forma eficiente y controlada

El resultado es una infraestructura más limpia, escalable y alineada con prácticas modernas de ingeniería.

---

## ⏸️ Estado del proyecto

El desarrollo de este **SaaS se encuentra actualmente pausado**.

El enfoque actual está en lanzar esta misma tecnología como un **software `.jar` open source**, gratuito y accesible para toda la comunidad de Minecraft.

👉 Puedes seguir el desarrollo de la versión open source en: **( https://github.com/S4LPICON/DeCloid-MC )**

