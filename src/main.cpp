#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// WiFi credentials
const char* ssid = "YourWiFiName";
const char* password = "YourPassword";

// UDP setup
WiFiUDP udp;
const unsigned int localPort = 4210;
char packetBuffer[255];

// Motor pins (NodeMCU v2 / D1 Mini)
#define MOTOR_LEFT_FWD D1    // GPIO5
#define MOTOR_LEFT_BWD D2    // GPIO4
#define MOTOR_RIGHT_FWD D3   // GPIO0
#define MOTOR_RIGHT_BWD D4   // GPIO2
#define MOTOR_LEFT_EN D5     // GPIO14 - PWM for left motor speed
#define MOTOR_RIGHT_EN D6    // GPIO12 - PWM for right motor speed

// Speed settings
int currentSpeed = 512;      // Default speed (0-1023 for ESP8266)
const int MAX_SPEED = 1023;
const int MIN_SPEED = 400;

//function  declarations:
void forward();
void backward();
void left();
void right();
void stopMotors();
void increaseSpeed();
void decreaseSpeed();
void executeCommand(String cmd);


void setup() {
  Serial.begin(115200);
  delay(100);
  
  // Setup motor pins
  pinMode(MOTOR_LEFT_FWD, OUTPUT);
  pinMode(MOTOR_LEFT_BWD, OUTPUT);
  pinMode(MOTOR_RIGHT_FWD, OUTPUT);
  pinMode(MOTOR_RIGHT_BWD, OUTPUT);
  pinMode(MOTOR_LEFT_EN, OUTPUT);
  pinMode(MOTOR_RIGHT_EN, OUTPUT);
  
  // Initial state - motors off
  stopMotors();
  
  // Connect to WiFi
  Serial.println("\n\nESP8266 RC Car - UDP Controller");
  Serial.println("================================");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n\n✓ WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Listening on UDP port:  ");
  Serial.println(localPort);
  Serial.println("================================\n");
  
  // Start UDP
  udp.begin(localPort);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;  // Null terminate
    }
    
    String command = String(packetBuffer);
    command.trim();  // Remove whitespace
    executeCommand(command);
  }
}

void executeCommand(String cmd) {
  Serial.print("Command:  ");
  Serial.print(cmd);
  Serial.print(" | Speed: ");
  Serial.println(currentSpeed);
  
  if (cmd == "F") {          // Forward
    forward();
  } else if (cmd == "B") {   // Backward
    backward();
  } else if (cmd == "L") {   // Left
    left();
  } else if (cmd == "R") {   // Right
    right();
  } else if (cmd == "S") {   // Stop
    stopMotors();
  } else if (cmd == "+") {   // Increase speed
    increaseSpeed();
  } else if (cmd == "-") {   // Decrease speed
    decreaseSpeed();
  }
}

void forward() {
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, currentSpeed);
  analogWrite(MOTOR_RIGHT_EN, currentSpeed);
}

void backward() {
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, HIGH);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, HIGH);
  analogWrite(MOTOR_LEFT_EN, currentSpeed);
  analogWrite(MOTOR_RIGHT_EN, currentSpeed);
}

void left() {
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, HIGH);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, currentSpeed);
  analogWrite(MOTOR_RIGHT_EN, currentSpeed);
}

void right() {
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, HIGH);
  analogWrite(MOTOR_LEFT_EN, currentSpeed);
  analogWrite(MOTOR_RIGHT_EN, currentSpeed);
}

void stopMotors() {
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, 0);
  analogWrite(MOTOR_RIGHT_EN, 0);
}

void increaseSpeed() {
  currentSpeed += 100;
  if (currentSpeed > MAX_SPEED) currentSpeed = MAX_SPEED;
  Serial.print("Speed increased to: ");
  Serial.println(currentSpeed);
}

void decreaseSpeed() {
  currentSpeed -= 100;
  if (currentSpeed < MIN_SPEED) currentSpeed = MIN_SPEED;
  Serial.print("Speed decreased to: ");
  Serial.println(currentSpeed);
}