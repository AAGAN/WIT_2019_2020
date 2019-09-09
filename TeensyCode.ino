#include <SPI.h>
#include <Adafruit_GFX.h>
#include "Adafruit_HX8357.h"
#include <SD.h>
File myFile;

const int chipSelect = BUILTIN_SDCARD; //for the SD card
const int LED = 13;

const int TFT_CS = 10;
const int TFT_DC = 9;
const int TFT_RST = 8;

int type;
int numCycles;
int holdTime;
int minPressure;
int counter = 1;
const int NumPoints = 390;
#define BLUE      0x001F
#define GREEN     0x07E0
#define RED       0xF800
#define YELLOW    0xFFE0
#define ORANGE    0xFC00
#define WHITE     0xFFFF
#define BLACK     0x0000
#define DKBLUE    0x000D
#define ADJ_PIN A0

double vo;

Adafruit_HX8357 tft = Adafruit_HX8357(TFT_CS, TFT_DC);

boolean display7 = true;
int leng = NumPoints - 1;
double xox[NumPoints] , xoy[NumPoints] ;
double ox,oy;
void setup()
{
  
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
  //Serial.print("Initializing SD card...");

  if (!SD.begin(chipSelect)) {
    Serial.println("initialization failed!");
    return;
  }

  pinMode(ADJ_PIN, INPUT);
  tft.begin(HX8357D);
  tft.fillScreen(BLACK);
  //Serial.println("initialization done.");
  
  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  //myFile = SD.open("inputs.txt", FILE_READ);
  
  // if the file opened okay, write to it:
  //if (myFile) {
    //Serial.print("Writing to test.txt...");
    //myFile.println("testing 1, 2, 3.");
	// close the file:
    //myFile.close();
    //Serial.println("done.");
  //} else {
    // if the file didn't open, print an error:
  //  Serial.println("error opening test.txt");
  //}
  
  // re-open the file for reading:
  myFile = SD.open("inputs.txt");
  if (myFile) {
    //Serial.println("inputs.txt:");
    
    // read from the file until there's nothing else in it:
    while (myFile.available()) {
      char c = myFile.read();
      //Serial.write(c);
      //Serial.println("*");
      if (c == '/')
      {
        while (c != '\n'  && myFile.available())
        {
          c = myFile.read();
        }
        //c = myFile.read();
        continue;
      }
      
    	
      if (c == 't')
      {
        type = 1;
        while (c != '\n'  && myFile.available())
        {
          c = myFile.read();
        }
        //c = myFile.read();
        continue;
      }
      else if (c == 'i')
      {
        type = 2;
        while (c != '\n'  && myFile.available())
        {
          c = myFile.read();
        }
        //c = myFile.read();
        continue;
      }
      else
      {
        char input [20];
        int p = 0;
        while(c!='\n' && myFile.available())
        {
          input[p] = c;
          c = myFile.read();
          p++;
        }
        input[p]='\0';
        if (counter ==1)
        {
          numCycles = atoi(input);
          counter++;
        }
        else if(counter == 2)
        {
          holdTime = atoi(input);
          counter++;
        }
        else if(counter == 3)
        {
          minPressure = atoi(input);
          counter++;
        }
      }
      //Serial.write(c);
    }
    // close the file:
    
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
  
    Serial.print("type = ");
    Serial.println(type);
    Serial.print("numCycles = ");
    Serial.println(numCycles);
    Serial.print("holdTime = ");
    Serial.println(holdTime);
    Serial.print("minPressure = ");
    Serial.println(minPressure);
  digitalWrite(LED,LOW);

    double x, y;


  tft.setRotation(3);


x=0;
  while(1) {
x++;
vo = analogRead(ADJ_PIN)/1023.0;
      Graph(tft, x, vo, 50, 290, 390, 260, 0, NumPoints, int(NumPoints/6), 0, 1.01, 0.1, "Normalized P-T", " Cycle ", "", DKBLUE, RED, GREEN, WHITE, BLACK, display7,x);
    delay(10);
    if(x==leng)x=0;
  }
}
/*

  function to draw a cartesian coordinate system and plot whatever data you want
  just pass x and y and the graph will be drawn

  huge arguement list
  &d name of your display object
  x = x data point
  y = y datapont
  gx = x graph location (lower left)
  gy = y graph location (lower left)
  w = width of graph
  h = height of graph
  xlo = lower bound of x axis
  xhi = upper bound of x asis
  xinc = division of x axis (distance not count)
  ylo = lower bound of y axis
  yhi = upper bound of y asis
  yinc = division of y axis (distance not count)
  title = title of graph
  xlabel = x asis label
  ylabel = y asis label
  gcolor = graph line colors
  acolor = axi ine colors
  pcolor = color of your plotted data
  tcolor = text color
  bcolor = background color
  &redraw = flag to redraw graph on fist call only
*/
void loop()
{
	// nothing happens after setup
}

void Graph(Adafruit_HX8357 &d, double x, double y, double gx, double gy, double w, double h, double xlo, double xhi, double xinc, double ylo, double yhi, double yinc, String title, String xlabel, String ylabel, unsigned int gcolor, unsigned int acolor, unsigned int pcolor, unsigned int tcolor, unsigned int bcolor, boolean &redraw, int jj) {

  //double ydiv, xdiv;
  // initialize old x and old y in order to draw the first point of the graph
  // but save the transformed value
  // note my transform funcition is the same as the map function, except the map uses long and we need doubles
  //static double ox = (x - xlo) * ( w) / (xhi - xlo) + gx;
  //static double oy = (y - ylo) * (gy - h - gy) / (yhi - ylo) + gy;
  double i;
  double temp;
  //int rot, newrot;

  if (redraw == true) {

    redraw = false;
    ox = (x - xlo) * ( w) / (xhi - xlo) + gx;
    oy = (y - ylo) * (gy - h - gy) / (yhi - ylo) + gy;
    // draw y scale
    for ( i = ylo; i <= yhi; i += yinc) {
      // compute the transform
      temp =  (i - ylo) * (gy - h - gy) / (yhi - ylo) + gy;

      if (i == 0) {
        d.drawLine(gx, temp, gx + w, temp, acolor);
      }
      else {
        d.drawLine(gx, temp, gx + w, temp, gcolor);
      }

      d.setTextSize(1);
      d.setTextColor(tcolor, bcolor);
      d.setCursor(gx - 40, temp);
      // precision is default Arduino--this could really use some format control
      d.println(i);
    }
    // draw x scale
    for (i = xlo; i <= xhi; i += xinc) {

      // compute the transform

      temp =  (i - xlo) * ( w) / (xhi - xlo) + gx;
      if (i == 0) {
        d.drawLine(temp, gy, temp, gy - h, acolor);
      }
      else {
        d.drawLine(temp, gy, temp, gy - h, gcolor);
      }

      d.setTextSize(1);
      d.setTextColor(tcolor, bcolor);
      d.setCursor(temp, gy + 10);
      // precision is default Arduino--this could really use some format control
      d.println(i);
    }

    //now draw the labels
    d.setTextSize(2);
    d.setTextColor(tcolor, bcolor);
    d.setCursor(gx , gy - h - 30);
    d.println(title);

    d.setTextSize(1);
    d.setTextColor(acolor, bcolor);
    d.setCursor(gx , gy + 20);
    d.println(xlabel);

    d.setTextSize(1);
    d.setTextColor(acolor, bcolor);
    d.setCursor(gx - 30, gy - h - 10);
    d.println(ylabel);


  }

  //graph drawn now plot the data
  // the entire plotting code are these few lines...
  // recall that ox and oy are initialized as static above
  x =  (x - xlo) * ( w) / (xhi - xlo) + gx;
  y =  (y - ylo) * (gy - h - gy) / (yhi - ylo) + gy;
//  d.drawLine(ox, oy, x, y, pcolor);
//  d.drawLine(ox, oy + 1, x, y + 1, pcolor);
//  d.drawLine(ox, oy - 1, x, y - 1, pcolor);
  d.drawPixel(xox[jj],xoy[jj],bcolor);
  d.drawPixel(x,y,pcolor);
  xox[jj] = x;
  xoy[jj] = y;

}
