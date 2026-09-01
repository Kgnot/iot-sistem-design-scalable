# Arquitectura IoT

Este proyecto implementa una plataforma de monitoreo de sensores conectados a dispositivos IoT. La arquitectura combina dispositivos MQTT, un broker central de eventos, almacenamiento de series temporales, procesamiento por workers y un servidor web que expone datos al usuario final mediante SSE (Server-Sent Events).

## Visión general

El flujo principal es el siguiente:

1. Un dispositivo IoT publica datos por MQTT.
2. El servicio bridge-consumer recibe esos mensajes.
3. Los eventos se normalizan y se publican en RabbitMQ.
4. Los workers escuchan eventos específicos y procesan alertas o lotes por sector.
5. El backend principal expone la información al usuario a través de SSE para actualizar la interfaz en tiempo real.

## Componentes principales

### 1. bridge-consumer

Es la capa de entrada del sistema. Recibe mensajes desde MQTT, convierte los payloads en eventos de dominio y los publica en RabbitMQ.

Responsabilidades:

- Conexión con Mosquitto (MQTT)
- Validación del payload recibido
- Creación del evento de telemetría
- Persistencia en InfluxDB
- Publicación del evento en RabbitMQ

Se encuentra en la carpeta `bridge-consumer`.

### 2. RabbitMQ

Es el bus de eventos del sistema. Los mensajes se publican con routing keys que permiten diferenciar eventos por tipo, dispositivo o sensor.

Ejemplo de routing key:

- `telemetry.esp32-c6-001.esp32-c6-mini.temperature`

Esto facilita que los workers se suscriban solamente a los eventos que les interesan.

### 3. Workers

Los workers reaccionan a eventos de RabbitMQ y realizan tareas de negocio.

En este repositorio existe un worker de temperatura que:

- escucha eventos de telemetría
- agrupa eventos por sector
- acumula una ventana de mensajes
- publica un batch para que el servidor principal lo difunda al cliente

La carpeta `workers/data-temperature-alert-worker` contiene esta lógica.

### 4. main-server

Este servidor es el que expone la información al cliente final. No se encarga de recibir sensores directamente; su función es consumir datos agregados y enviarlos a la interfaz del usuario en tiempo real.

En este caso se usa SSE, es decir, un canal unidireccional desde el servidor al navegador.

#### Endpoint SSE

El servidor expone un endpoint tipo:

- `/api/sectors/stream`

Esto permite abrir una conexión persistente desde el frontend y recibir eventos del backend sin necesidad de polling continuo.

La implementación usa `SseEmitter`, que es la interfaz de Spring para emitir eventos del servidor al cliente.

#### Flujo SSE

- El cliente se conecta a `/api/sectors/stream`
- El servidor guarda el emitter activo
- Cuando llega un batch por sector, el backend hace broadcast a todos los clientes conectados
- El navegador recibe el evento y lo procesa para actualiza la UI

## Flujo de datos completo

### Desde el dispositivo hasta la interfaz

1. El sensor publica un valor por MQTT.
2. El bridge-consumer recibe el mensaje desde el tópico `devices/.../telemetry`.
3. Se construye un `TelemetryEvent` con datos como:
   - dispositivo
   - tipo de sensor
   - valor
   - localidad
   - sector
4. Se guarda en InfluxDB.
5. Se publica en RabbitMQ con su routing key correspondiente.
6. El worker de temperatura escucha eventos de telemetría.
7. El worker arma un batch por sector.
8. El servidor principal recibe ese batch y lo difunde al cliente con SSE.
9. El frontend actualiza la vista de alertas o datos en vivo.

## Persistencia

### InfluxDB

Se usa para almacenar series temporales de mediciones.

Esto permite consultar históricos, promedios, tendencias y alertas sobre los valores de sensores.

### MinIO

Se usa para almacenamiento de archivos o blobs asociados al sistema, como artefactos o media.

## Observabilidad y debugging

La aplicación tiene varios puntos de logging que permiten seguir el flujo de mensajes:

- conexión a InfluxDB
- conexión a RabbitMQ
- conexión a MQTT
- recepción de mensajes MQTT
- creación de eventos
- persistencia del evento
- publicación en RabbitMQ
- recepción de mensajes por worker
- armado de batches
- broadcast por SSE

Estos logs son clave para verificar que el flujo funciona correctamente y para localizar el punto exacto donde se corta la transmisión.

## Infraestructura

La aplicación se levanta con Docker Compose y usa los siguientes servicios:

- `api` -> bridge-consumer
- `temperature-alert-worker` -> worker de alertas por temperatura
- `main-server` -> backend con SSE
- `mosquitto` -> broker MQTT
- `rabbitmq` -> broker de eventos
- `influxdb` -> base de series temporales
- `minio` -> almacenamiento de archivos

## Consideraciones de diseño

- MQTT se usa para la ingestión de datos desde dispositivos.
- RabbitMQ se usa para desacoplar procesos y permitir escala horizontal de workers.
- InfluxDB se usa para datos temporales.
- SSE se usa para entrega en tiempo real a clientes web.
- El sistema está pensado para que cada componente sea responsable de una parte del flujo y pueda evolucionar por separado.

## Resultado esperado

Cuando todo está funcionando correctamente, el sistema debe permitir:

- recibir mediciones desde dispositivos IoT
- guardar métricas en InfluxDB
- procesar alertas en workers
- transmitir cambios a la interfaz en tiempo real con SSE
- mantener el cliente actualizado sin recargar la página

## Conclusión

La solución combina protocolos y tecnologías adecuadas para cada capa del sistema: MQTT para dispositivos, RabbitMQ para eventos, InfluxDB para series temporales, workers para procesamiento y SSE para la experiencia en tiempo real del usuario final.
