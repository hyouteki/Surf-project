import processing.serial.*;

// variables
Serial port;
int lf = 10;


void setup()
{
  // port setup
  //printArray(Serial.list());
  port = new Serial(this, Serial.list()[0], 9600);
  
  size(1050, 720);
  surface.setTitle("Surf project");
  smooth();
  
  rect(100, 100, 520, 520);

}
void draw(){
  int i = 0;
  strokeWeight(16);
  while (port.available() > 0) {
    String inBuffer = port.readStringUntil(lf); 
    if (inBuffer != null) {
      try {
        //println(inBuffer);
        if (inBuffer.length() < 4) continue;
        int comma = inBuffer.indexOf(",", 0);
        int end = inBuffer.indexOf(",", comma+1);
        inBuffer = inBuffer.substring(0, end);
        //println(inBuffer);
        int x = Integer.parseInt(inBuffer.substring(0, comma));
        int y = Integer.parseInt(inBuffer.substring(comma+1, end));
        
        x += 120;
        y += 120;
        //print(x);
        ////print(inBuffer.substring(0, comma));
        //print(" ");
        //println(y);
        //println(inBuffer.substring(comma+1, end));
        point(x+i, y);
        i += 50;
      } catch (Exception e) {}
    }
  }
}
