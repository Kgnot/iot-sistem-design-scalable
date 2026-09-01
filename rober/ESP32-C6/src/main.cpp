#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ---------- Configuración de red ----------
const char* WIFI_SSID = "FRICAURTE";
const char* WIFI_PASSWORD = "nijomajobra";

// ---------- Configuración de MQTT (mosquitto expuesto en tu docker-compose) ----------
// Usa la IP local de tu PC en la red (no "localhost", el ESP32 es otro dispositivo físico)
const char* MQTT_HOST = "192.168.1.5";
const int   MQTT_PORT = 1883;
const char* DEVICE_TYPE = "esp32-c6-mini";
const char* DEVICE_ID   = "esp32-c6-001";

// ---------- Configuración de sector (fija por dispositivo) ----------
const char* LOCALITY_ID   = "18";
const char* LOCALITY_NAME = "Rafael Uribe Uribe";
const char* SECTOR        = "marruecos-1";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

char topic[128];

void connectWiFi() {
    Serial.printf("Conectando a WiFi: %s\n", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.printf("WiFi conectado. IP: %s\n", WiFi.localIP().toString().c_str());
}

void connectMQTT() {
    mqttClient.setServer(MQTT_HOST, MQTT_PORT);
    while (!mqttClient.connected()) {
        Serial.println("Conectando a MQTT...");
        String clientId = String(DEVICE_ID) + "-" + String(random(0xffff), HEX);
        if (mqttClient.connect(clientId.c_str())) {
            Serial.println("Conectado a MQTT broker.");
        } else {
            Serial.printf("Fallo, rc=%d. Reintentando en 3s\n", mqttClient.state());
            delay(3000);
        }
    }
}

void publishTelemetry(const char* sensorType, float value, const char* unit) {
    JsonDocument doc;
    doc["sensor_type"] = sensorType;
    doc["value"] = value;
    doc["unit"] = unit;
    doc["locality_id"] = LOCALITY_ID;
    doc["locality_name"] = LOCALITY_NAME;
    doc["sector"] = SECTOR;

    char payload[256];
    size_t len = serializeJson(doc, payload);

    bool ok = mqttClient.publish(topic, payload, len);
    Serial.printf("Publicado en %s -> %s [%s]\n", topic, payload, ok ? "OK" : "FALLO");
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    snprintf(topic, sizeof(topic), "devices/%s/%s/telemetry", DEVICE_TYPE, DEVICE_ID);

    connectWiFi();
    connectMQTT();
}

void loop() {
    if (!mqttClient.connected()) {
        connectMQTT();
    }
    mqttClient.loop();

    float fakeTemp = 20.0 + (random(0, 100) / 10.0);
    publishTelemetry("temperature", fakeTemp, "C");

    delay(5000);
}