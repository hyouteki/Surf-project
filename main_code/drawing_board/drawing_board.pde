import processing.serial.*;

// variables
Serial port;
int lf = 10;
// model parameters;
int l = 100;
int b = 100;
int scale_l = 5;
int scale_b = 5;
int width = l*scale_l;
int height = b*scale_b;
// design parameters;
int stroke_weight = 12;

void setup()
{
  // port setup
  port = new Serial(this, Serial.list()[0], 9600);
  //size(width, height);
  size(500, 500);
  surface.setTitle("Surf project");
  smooth();
}
void draw(){
  strokeWeight(stroke_weight);
  while (port.available() > 0) {
    String buffer = port.readStringUntil(lf); 
    if (buffer != null) {
      try {
        if (buffer.length() < 4) continue;
        int comma = buffer.indexOf(",", 0);
        int end = buffer.indexOf(",", comma+1);
        buffer = buffer.substring(0, end);
        int x = Integer.parseInt(buffer.substring(0, comma));
        int y = Integer.parseInt(buffer.substring(comma+1, end));
        // scaling x & y
        x *= scale_l;
        y *= scale_b;
        // cause coordinates in processing.org are horizontally mirrored
        y = abs(500-y);
        point(x, y);
      } catch (Exception e) {}
    }
  }
}
