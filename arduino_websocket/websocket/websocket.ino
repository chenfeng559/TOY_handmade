#include <driver/i2s.h>
#include <WiFi.h>
#include <Arduino.h>
#include <ArduinoWebsockets.h>
//#include <HTTPClient.h>
#include <WiFiUdp.h>

// 管脚配置
#define I2S_WS 5
#define I2S_SD 6
#define I2S_SCK 4

// I2S 配置参数
#define I2S_NUM         I2S_NUM_0
#define I2S_SAMPLE_RATE 44100
#define I2S_SAMPLE_BITS I2S_BITS_PER_SAMPLE_16BIT
#define I2S_CHANNEL_NUM I2S_CHANNEL_FMT_ONLY_LEFT
#define I2S_BUFFER_SIZE 1024

const char* ssid = "Xiaomi_79E1";
const char* password = "8879878Ccf";
const char* websocket_server = "192.168.31.160";
const uint16_t websocket_port = 8765;
const char* websocket_path = "/audio";


// Audio buffer size
const size_t bufferSize = 1024;
uint8_t buffer[bufferSize];


using namespace websockets;
WebsocketsClient client;
void setupI2S();
void connectToWiFi();
void connectToWebSocket();
//void readAndSendSerialInput();
void onMessageCallback(WebsocketsMessage message);
void onEventsCallback(WebsocketsEvent event, String data);
size_t streamAudio(uint8_t* data, size_t size);


void setup() {
    Serial.begin(115200);
    setupI2S();
    connectToWiFi();
    connectToWebSocket();

    client.onMessage(onMessageCallback);
    client.onEvent(onEventsCallback);
}

void loop() {
    client.poll();
    //readAndSendSerialInput();
    size_t bytesRead = streamAudio(buffer, bufferSize);
    //delay(50);
    if (bytesRead > 0) {
      //强制类型转换。sendBinary接受char*类型
        client.sendBinary(reinterpret_cast<const char*>(buffer), bytesRead);
    }
    
}


void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_SAMPLE_BITS,
    .channel_format = I2S_CHANNEL_NUM,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = I2S_BUFFER_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = true,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  // 安装并启动i2s驱动
  i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM, &pin_config);

}

size_t streamAudio(uint8_t* data, size_t size) {
    size_t bytesRead;
    i2s_read(I2S_NUM, data, size, &bytesRead, portMAX_DELAY);
    return bytesRead;
}


void connectToWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);

    unsigned long startAttemptTime = millis();

    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("网络未能连接上");
        return;
    }

    Serial.println("连接上WiFi!");
}

void connectToWebSocket() {
    bool connected = false;
    for (int i = 0; i < 5; i++) {
        if (client.connect("ws://" + String(websocket_server) + ":" + String(websocket_port))) {
            connected = true;
            Serial.println("Connected to server");
            client.send("Hello from ESP32");
            break;
        } else {
            Serial.println("Failed to connect to server, retrying...");
            delay(2000);
        }
    }
    if (!connected) {
        Serial.println("Could not connect to server after multiple attempts.");
    }
}

// void readAndSendSerialInput() {
//     if (Serial.available() > 0) {
//         String input = Serial.readStringUntil('\n');
//         input.trim();
//         if (input.length() > 0) {
//             client.send(input);
//             Serial.println("Sent: " + input);
//         }
//     }
// }

void onMessageCallback(WebsocketsMessage message) {
    Serial.print("Received: ");
    Serial.println(message.data());
}

void onEventsCallback(WebsocketsEvent event, String data) {
    if(event == WebsocketsEvent::ConnectionOpened) {
        Serial.println("Connection Opened");
    } else if(event == WebsocketsEvent::ConnectionClosed) {
        Serial.println("Connection Closed");
    } else if(event == WebsocketsEvent::GotPing) {
        Serial.println("Got a Ping!");
    } else if(event == WebsocketsEvent::GotPong) {
        Serial.println("Got a Pong!");
    }
}