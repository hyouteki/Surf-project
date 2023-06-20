void setup() {
  Serial.begin(9600);
}

void loop() {
  int x = random(0, 500);
  int y = random(0, 500);
  String code = String(x)+","+String(y)+",";
  // Serial.println(code);
  // Serial.write("122,12,");
  // Serial.write(code, sizeof(code)/sizeof(char));
  Serial.println(code);
  // Serial.println(Serial.read());
  delay(500);
}
