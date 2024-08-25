#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include <ESP32Servo.h>

const char* WIFI_SSID = "Ansh";
const char* WIFI_PASS = "*********";

WebServer server(80);
Servo servoX;
Servo servoY;

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleServoControl() {
  if (server.hasArg("x") && server.hasArg("y")) {
    int x = server.arg("x").toInt();
    int y = server.arg("y").toInt();

    Serial.printf("Received command: x=%d, y=%d\n", x, y);

    // Directly map the incoming values to servo positions
    servoX.write(x);
    servoY.write(y);

    server.send(200, "text/plain", "Servos adjusted");
  } else {
    server.send(400, "text/plain", "Missing parameters");
  }
}

void centerServos() {
  servoX.write(90);
  servoY.write(90);
  delay(1000);  // Allow time for servos to move to the center
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  // Initialize servos
  servoX.attach(14);
  servoY.attach(15);

  centerServos();  // Center the servos at the start

  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");

    // Turn on the LED flash
    digitalWrite(4, HIGH); // Assuming GPIO 4 controls the flash LED
  }

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");

  server.on("/cam-lo.jpg", handleJpgLo);    
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/control", HTTP_GET, handleServoControl);

  server.begin();
}

void loop()
{
  server.handleClient();
}
