// pin initialization
#define trig_pin_l 8
#define echo_pin_l 9
#define trig_pin_b 10
#define echo_pin_b 11

void get_readings(int *d_l, int *d_b)
{
  long time;
  digitalWrite(trig_pin_l, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_pin_l, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin_l, LOW);
  time = pulseIn(echo_pin_l, HIGH);
  *d_l = (time * 0.344) / 2;
  delay(delay_in_reading);

  digitalWrite(trig_pin_b, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_pin_b, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin_b, LOW);
  time = pulseIn(echo_pin_b, HIGH);
  *d_b = (time * 0.344) / 2;
  delay(delay_in_reading);
}

void setup()
{
  Serial.begin(9600);
  pinMode(trig_pin_l, OUTPUT);
  pinMode(echo_pin_l, INPUT);
  pinMode(trig_pin_b, OUTPUT);
  pinMode(echo_pin_b, INPUT);
}

void print_coords(int d_l, int d_b)
{
  String code = String(d_l) + "," + String(d_b) + ",";
  Serial.println(code);
}

void loop()
{
  int d_l, d_b;
  get_readings(&d_l, &d_b);
  print_coords(d_l, d_b);
  delay(200);
  return 0;
}