#include <Servo.h>
#define led0 10
#define led1 11
#define led2 12
#define led3 13
#define ultrasonic1 A1
#define ultrasonic2 A0
#define servoPin 9

Servo servo;
int distance1 = 0;
int distance2 = 0;
int position = 0;

void setup()
{
  Serial.begin(115200);
  pinMode(led0, OUTPUT);  
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  servo.attach(servoPin, 500, 2500);
}

long readUltrasonicDistance(int triggerPin, int echoPin)
{
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  return pulseIn(echoPin, HIGH);
}

void glow(int led0State, int led1State, int led2State, int led3State) {
  digitalWrite(led0, led0State);
  digitalWrite(led1, led1State);
  digitalWrite(led2, led2State);
  digitalWrite(led3, led3State);
  for (int i = 0; i < 90; i++) {
  	servo.write(i);
    delay(10);
  }
  distance1 = 0;
  distance2 = 0;
  digitalWrite(led0, LOW);
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  digitalWrite(led3, LOW);
}

void loop()
{
  distance1 = 0.01723 * readUltrasonicDistance(ultrasonic1, ultrasonic1);
  distance2 = 0.01723 * readUltrasonicDistance(ultrasonic2, ultrasonic2);
  // Serial.print(distance1);
  // Serial.print(", ");
  // Serial.print(distance2);n
  // Serial.println("");
  if (distance1 <= 21 && distance1 >= 19) {
    if (distance2 < 20 && distance1 >= 18) {
      Serial.println("z");
      glow(LOW, LOW, LOW, LOW);
    } else if (distance2 < 22 && distance2 >= 20) {
      Serial.println("s");
      glow(LOW, LOW, LOW, HIGH);
    } else if (distance2 == 22) {
      Serial.println("x");
      glow(LOW, LOW, HIGH, LOW);
    } else if (distance2 >= 23 && distance2 < 26) {
      Serial.println("d");
      glow(LOW, LOW, HIGH, HIGH);
    }	
  } else if (distance1 <= 24) {
    if (distance2 < 20 && distance1 >= 18) {
      Serial.println("c");
      glow(LOW, HIGH, LOW, LOW);
    } else if (distance2 < 22 && distance2 >= 20) {
      Serial.println("v");
      glow(LOW, HIGH, LOW, HIGH);
    } else if (distance2 == 22) {
      Serial.println("g");
      glow(LOW, HIGH, HIGH, LOW);
    } else if (distance2 >= 23 && distance2 < 26) {
      Serial.println("b");
      glow(LOW, HIGH, HIGH, HIGH);
    }	
  } else if (distance1 <= 26) {
    if (distance2 < 20 && distance1 >= 18) {
      Serial.println("h");
      glow(HIGH, LOW, LOW, LOW);
    } else if (distance2 < 22 && distance2 >= 20) {
      Serial.println("n");
      glow(HIGH, LOW, LOW, HIGH);
    } else if (distance2 == 22) {
      Serial.println("j");
      glow(HIGH, LOW, HIGH, LOW);
    } else if (distance2 >= 23 && distance2 < 26) {
      Serial.println("m");
      glow(HIGH, LOW, HIGH, HIGH);
    }	
  } else if (distance1 <= 28 && distance1 <= 31) {
    if (distance2 < 20 && distance1 >= 18) {
      Serial.println(",");
      glow(HIGH, HIGH, LOW, LOW);
    } else if (distance2 < 22 && distance2 >= 20) {
      Serial.println(".");
      glow(HIGH, HIGH, LOW, HIGH);
    } else if (distance2 == 22) {
      Serial.println(";");
      glow(HIGH, HIGH, HIGH, LOW);
    } else if (distance2 >= 23 && distance2 < 26) {
      Serial.println("/");
      glow(HIGH, HIGH, HIGH, HIGH);
    }	
  }
  Serial.println("~");
}