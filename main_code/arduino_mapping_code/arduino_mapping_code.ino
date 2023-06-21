#include "Ultrasonic.h"

/*
units
    length - mm
    angle - degree
    delay - millisecond
*/

// pin initialization
Ultrasonic ultrasonic_l(7);
Ultrasonic ultrasonic_b(8);

// mathematical constants
double pi = 3.141592653589;

// constraints (ultrasonic)
#define theta_m 15
#define min_dis 20
#define max_dis 3500

// model parameters
#define l 100
#define b 100
#define theta_l theta_m
#define theta_b theta_m
#define scale_l 1
#define scale_b 1
#define no_readings 3
#define delay_in_reading 70

// helper methods
double degree_to_radian(int degree)
{
    return degree * pi / 180;
}

// derived model parameters
int c_l = l / (2 * sin(degree_to_radian(theta_l)));
int c_b = b / (2 * sin(degree_to_radian(theta_b)));

// model methods
void get_readings(int *d_l, int *d_b)
{
    // for now it is hardcoded
    // *d_l = c_l + b;
    // *d_b = sqrt(sq((long)(c_b+l/2)) + sq((long)(b / 2)));
    *d_l = ultrasonic_l.MeasureInMillimeters();
    *d_b = ultrasonic_b.MeasureInMillimeters();
}

void average_readings(int *d_l, int *d_b)
{
    int reading_l, reading_b;
    *d_l = 0;
    *d_b = 0;
    for (int i = 0; i < no_readings; ++i)
    {
        get_readings(&reading_l, &reading_b);
        *d_l += reading_l;
        *d_b += reading_b;
        delay(delay_in_reading);
    }
    *d_l = *d_l / no_readings;
    *d_b = *d_b / no_readings;
}

bool is_reading_valid(int d_l, int d_b)
{
    int d_l_min = c_l;
    int d_l_max = sqrt(sq((long)(c_l + b)) + sq((long)(l / 2)));
    int d_b_min = c_b;
    int d_b_max = sqrt(sq((long)(c_b + l)) + sq((long)(b / 2)));
    // printf("d_l_max = %d\n", d_l_max);
    // printf("d_b_max = %d\n", d_b_max);
    return d_l >= d_l_min && d_l <= d_l_max && d_b >= d_b_min && d_b <= d_b_max;
}

void map_to_coords(int d_l, int d_b, int *alpha, int *beta)
{
    double p = d_l;
    double q = l / 2;
    double r = b + c_l;
    double u = d_b;
    double v = l + c_b;
    double w = b / 2;
    double e = sqrt(sq(q - v) + sq(r - w));
    double f = (sq(p) - sq(u) + sq(e)) / (2 * e);
    double g = sqrt(sq(p) - sq(f));

    *alpha = (int)((f / e) * (v - q) + (g / e) * (w - r) + q) % l;
    *beta = (int)((f / e) * (w - r) - (g / e) * (v - q) + r) % b;
}


void setup() {
  Serial.begin(9600);
}

void print_coords(int alpha, int beta) {
  String code = String(alpha)+","+String(beta)+",";
  Serial.println(code);
}

void loop() {
    int d_l, d_b;
    average_readings(&d_l, &d_b);
    // Serial.println("c_l = " + String(c_l)+"mm");
    // Serial.println("c_b = " + String(c_b)+"mm");
    // Serial.println("d_l = " + String(d_l)+"mm");
    // Serial.println("d_b = " + String(d_b)+"mm");
    int valid = is_reading_valid(d_l, d_b);
    // Serial.println("valid_reading = " + String(valid));
    if (valid)
    {
        int alpha, beta;
        map_to_coords(d_l, d_b, &alpha, &beta);
        // printf("mapped coordinate = (%d, %d)\n", alpha, beta);
        print_coords(alpha, beta);
    }
    return 0;
}