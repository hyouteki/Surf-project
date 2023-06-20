import processing.serial.*;

Serial port;
int lf = 10; // similar to endline character

void setup() {
  //printArray(Serial.list());
  port = new Serial(this, Serial.list()[0], 9600);
 
}

void draw() {
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
        print(x);
        //print(inBuffer.substring(0, comma));
        print(" ");
        println(y);
        //println(inBuffer.substring(comma+1, end));
      } catch (Exception e) {}
    }
  }
}
