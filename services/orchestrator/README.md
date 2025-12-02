#Orchestrator
#encargado de orquestar los contenedores en los nodos de todos los clientes
#pide al backend crear un servidor antes de crearlo
#decide cuando elimnar contenedores, segun la info que mande el plugin en el server
#un jugador puede solicitar un servidor desde un server usando el proxy-plugin
#si existe un servidor disponible y no lleno se le envia la ip y puerto dle mismo para que el proxy-plugin lo registre
#si no hay servidor disponible hace la solicitud al backend
#le pasa la ip y puerto al proxy-plugin

