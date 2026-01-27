#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// WiFi credentials
const char* ssid = "KKS's phone";
const char* password = "kvsandkks";

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
int sm = 400;
const int MAX_SPEED = 1023;
const int MIN_SPEED = 400;

// Timeout safety feature
unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT = 300; // Stop if no command for 300ms

// Last command for change detection
char lastCommand = 'S';

// Function declarations
void forward();
void backward();
void left();
void right();
void stopMotors();
void increaseSpeed();
void decreaseSpeed();
void executeCommand(char cmd);
void ul();
void ur();
void dl();
void dr();

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
  Serial.println(F("\n\nESP8266 RC Car - UDP Controller"));
  Serial.println(F("================================"));
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print(F("Connecting to WiFi"));
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println(F("\n\n✓ WiFi Connected!"));
  Serial.print(F("IP Address: "));
  Serial.println(WiFi.localIP());
  Serial.print(F("Listening on UDP port: "));
  Serial.println(localPort);
  Serial.println(F("================================\n"));
  
  // Start UDP
  udp.begin(localPort);
  lastCommandTime = millis();
}

void loop() {
  // Process ALL pending UDP packets (clear the buffer)
  while (udp.parsePacket()) {
    int len = udp.read(packetBuffer, 2); // Read max 2 bytes (command + potential null)
    if (len > 0) {
      char cmd = packetBuffer[0];
      
      // Execute command immediately (removed debouncing for better responsiveness)
      executeCommand(cmd);
      lastCommand = cmd;
      lastCommandTime = millis();
    }
  }
  
  // Safety timeout - auto-stop if no command received
  if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
    if (lastCommand != 'S') {
      stopMotors();
      lastCommand = 'S';
      Serial.println(F("\n[TIMEOUT - STOPPED]"));
    }
  }
  
  // Yield to prevent watchdog reset
  yield();
}

void executeCommand(char cmd) {
  // Minimal serial output for speed
  Serial.print(cmd);
  Serial.print(' ');
  
  switch(cmd) {

    case 'R':
      ul();
      break;
    case 'Y':
      ur();
      break;
    case 'C':
      dl();
      break;
    case 'B':
      dr();
      break;
    case 'F':
      forward();
      break;
    case 'K':
      backward();
      break;
    case 'L':
      left();
      break;
    case 'E':
      right();
      break;
    case 'S':
      stopMotors();
      break;
    case '+':
      increaseSpeed();
      break;
    case '-':
      decreaseSpeed();
      break;
    default:
      // Ignore unknown commands
      break;
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

void right() {
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
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

void ul(){
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, currentSpeed - sm);
  analogWrite(MOTOR_RIGHT_EN,currentSpeed + sm);
}
void ur(){
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, currentSpeed + sm);
  analogWrite(MOTOR_RIGHT_EN,currentSpeed - sm);
}
void dl(){
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, HIGH);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, HIGH);
  analogWrite(MOTOR_LEFT_EN, currentSpeed - sm);
  analogWrite(MOTOR_RIGHT_EN, currentSpeed + sm);
}
void dr(){
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, HIGH);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, HIGH);
  analogWrite(MOTOR_LEFT_EN, currentSpeed + sm);
  analogWrite(MOTOR_RIGHT_EN, currentSpeed - sm);
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
  Serial.print(F("[SPD+: "));
  Serial.print(currentSpeed);
  Serial.println(F("]"));
}

void decreaseSpeed() {
  currentSpeed -= 100;
  if (currentSpeed < MIN_SPEED) currentSpeed = MIN_SPEED;
  Serial.print(F("[SPD-: "));
  Serial.print(currentSpeed);
  Serial.println(F("]"));
}