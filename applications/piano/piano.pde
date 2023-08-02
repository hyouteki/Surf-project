import processing.serial.*;
import ddf.minim.analysis.*;
import ddf.minim.*;
import ddf.minim.signals.*;
 
Minim minim;
AudioOutput out;
color light = color(196, 196, 196);
color dark = color(62, 54, 63);
String logoLink = "https://img.icons8.com/clouds/256/piano.png";
PImage logo;
Serial port; 
String val = "";

void setup()
{
    port = new Serial(this, "COM5", 115200);
    size(1050, 720);
    minim = new Minim(this);
    out = minim.getLineOut(Minim.STEREO);
    surface.setTitle("Piano");
    background(dark);
    smooth();
    //logo = loadImage(logoLink);
    //surface.setIcon(logo);
    //image(logo,width-100,0,100,100); 
    background(0);
    stroke(255);
    for(int i = 0; i < out.bufferSize() - 1; i++)
    {
      float x1 = map(i, 0, out.bufferSize(), 0, width);
      float x2 = map(i+1, 0, out.bufferSize(), 0, width);
      line(x1, 50 + out.left.get(i)*50, x2, 50 + out.left.get(i+1)*50);
      line(x1, 150 + out.right.get(i)*50, x2, 150 + out.right.get(i+1)*50);
    }
    
    color[] colors = {light, dark, light, dark, light, light, dark, light, dark, light, dark, light};
    int[] xCoods = {0, 100, 150, 250, 300, 450, 550, 600, 700, 750, 850, 900};
    char[] keys = {'z', 's', 'x', 'd', 'c', 'v', 'g', 'b', 'h', 'n', 'j', 'm'};
    int[] rows = {1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3};
    int[] cols = {1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4};
    
    for (int i = 0; i < 12; i++) {
        if (colors[i] == light) {
              fill(colors[i]);
              stroke(dark);
              strokeWeight(2);
              rect(xCoods[i],0,150,height);
              fill(dark);
              textSize(36);
              text("Key: "+str(keys[i]), xCoods[i]+30, height-54);
              text("["+str(rows[i])+", "+str(cols[i])+"]", xCoods[i]+36, height-20);
        }
    }
    for (int i = 0; i < 12; i++) {
        if (colors[i] == dark) {
              fill(colors[i]);
              stroke(dark);
              strokeWeight(2);
              rect(xCoods[i],0,100,height*0.6, 0, 0, 24, 24);
              fill(light);
              textSize(24);
              text("Key: "+str(keys[i]), xCoods[i]+22, height*0.6-48);
              text("["+str(rows[i])+", "+str(cols[i])+"]", xCoods[i]+28, height*0.6-20);
        }
    }
}
 
void draw()
{
  if ( port.available() > 0)
  { // If data is available,
    val = port.readStringUntil('\n'); 
    keyPressAction(val.charAt(0)); // read it and store it in val
    println(val);
  }
}

void keyPressAction(char ch) {
  SineWave mySine;
  MyNote newNote;

  float pitch = 0;
  switch(ch) {
    case 'z': pitch = 262; break;
    case 's': pitch = 277; break;
    case 'x': pitch = 294; break;
    case 'd': pitch = 311; break;
    case 'c': pitch = 330; break;
    case 'v': pitch = 349; break;
    case 'g': pitch = 370; break;
    case 'b': pitch = 392; break;
    case 'h': pitch = 415; break;
    case 'n': pitch = 440; break;
    case 'j': pitch = 466; break;
    case 'm': pitch = 494; break;
    case ',': pitch = 523; break;
    case 'l': pitch = 554; break;
    case '.': pitch = 587; break;
    case ';': pitch = 622; break;
    case '/': pitch = 659; break;
  }
  
   if (pitch > 0) {
      newNote = new MyNote(pitch, 0.2);
   }
}
 
void keyPressed()
{
  keyPressAction(key);
}

void stop()
{
  out.close();
  minim.stop();
 
  super.stop();
}

class MyNote implements AudioSignal
{
     private float freq;
     private float level;
     private float alph;
     private SineWave sine;
     
     MyNote(float pitch, float amplitude)
     {
         freq = pitch;
         level = amplitude;
         sine = new SineWave(freq, level, out.sampleRate());
         alph = 0.9;
         out.addSignal(this);
     }

     void updateLevel()
     {
         level = level * alph;
         sine.setAmp(level);
         
         if (level < 0.01) {
             out.removeSignal(this);
         }
     }
     
     void generate(float [] samp)
     {
         sine.generate(samp);
         updateLevel();
     }
     
    void generate(float [] sampL, float [] sampR)
    {
        sine.generate(sampL, sampR);
        updateLevel();
    }

}
