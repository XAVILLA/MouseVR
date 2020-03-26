// Encoder2RDS
//
//  Read the encoder and translate to USB output that mimics the camera treadmill system
//  Teensy 3.2 Arduino 1.8.3 with Teensy Extensions
//
//  Encoder A - pin 0
//  Encoder B - pin 1
//  Encoder VCC - Vin
//  Encoder ground - GND
//
//  The data packet we need to put out consists of:
//  0           : marks start of data pack - no other data can be = 0
//  sampleCount : A counter that counts from 1 to 255 and then loops back to 1
//  x[0]        : counts since last report, 0x80 to 0x7f, offset by adding 0x80
//  y[0]         
//  x[1]        
//  y[1]        
//  squal[0]    : surface quality, 0 = no surface, max = 169, typically ~80 on white paper
//  squal[1]       - squal is always incremented by 1
//  shut_high[0]: shutter high and low are 16 bit number - adjusts shutter, typically ~120 on white paper  
//  shut_low[0]    - if shutter low = 0, force it to 1
//  shut_high[1]   - shutter high is always incremented by 1 
//  shut_low[1]

//
// Steve Sawtelle
// 20180420
// jET Janelia HHMI 
//

#include <EEPROM.h>

#define VERSION "20180518"
// ===== VERSIONS ======
// 20180518 sws
// - add in EEPROM cal values
// - add in analog out and direction
// - add help and debug commands

// 201804254 sws 
//  - started


#define FRAMECLK 250     // usec per frame

// Create an IntervalTimer object 
#ifdef MEGA
#include "TimerOne.h"
#else
IntervalTimer frameTimer;
#endif

#define DATA_RETURN 246     // 0 = return rotation coordinates, 1 return raw camera x/y  RDS uses 1 
#define VIDEO_OFF   250     // Turn off video - not used here
#define VIDEO_INIT  251     // Read out a frame of pixels from the camera and send it to the user - not used here
#define DUMP_REGISTERS  252 // Dump Internal Registers - not used here
#define MOTION_STOP  254    // Stop Data Acquisition
#define MOTION START 255    // Start Data Acquisition

#define encAPin 0
#define encBPin 1
#define dirPin 2

struct 
{
    int flag;         // set to 0x55 to show we have actually saved data 
    float voltsPerMmPerSecond; // convert count to speed
    float mmPerCount;   // convert counts to distance
    boolean reverseDirection;  // true to reverse direction sense
    boolean showBackwards; // true to show backwards speed       
} setups;


#define SPEED_TIMEOUT 50000  // if we don't move in this many microseconds assume we are stopped
#define MAXSPEED    1000.0f  // maximum speed for dac out (mm/sec)
#define MAXDACVOLTS 2.5f    // DAC ouput voltage at maximum speed
#define MAXDACCNTS  4095.0f // maximum dac value
#define DAC_CNTS_PER_VOLT 1240.9f
#define FW 1
#define BW -1

float maxDACval = MAXDACVOLTS * MAXDACCNTS / 3.3; // limit dac output to max allowed
static float runSpeed = 0;
static float lastSpeed = 0;
volatile uint32_t lastUsecs;
volatile uint32_t thisUsecs;
volatile uint32_t encoderUsecs;
volatile float distance = 0;
volatile int direction = FW; 

boolean debug = false;
boolean showSpeed = false;
int32_t counts = 0;

volatile boolean sampling = false;
volatile uint8_t xcounts = 0;
volatile uint8_t ycounts = 128;
volatile uint8_t samples = 1;
uint8_t outStream[] = {0, 1, 128, 128, 128, 128, 80, 80, 1, 120, 1, 120 };

// ------------------------------------------
// interrupt routine for ENCODER_A rising edge
// ---------------------------------------------
void encoderInt()
{    
    int ENCA = digitalReadFast(encAPin);  
    int ENCB = digitalReadFast(encBPin);   
    // figure out the direction  
    if (ENCA != ENCB )
    {   
       if( sampling ){ if( ycounts < 250) ycounts++; }  // forwards 
       direction = FW;
       counts++;
       thisUsecs = micros();
       encoderUsecs = thisUsecs - lastUsecs;
       lastUsecs = thisUsecs;
       runSpeed = setups.mmPerCount * 1e6 / (float)(encoderUsecs);
       distance += setups.mmPerCount;      
    }  
    else
    {
       if( sampling ){ if( ycounts > 1 ) ycounts--; }   // backwards
       if( setups.showBackwards) 
       {
          counts--;
          thisUsecs = micros();
          encoderUsecs = thisUsecs - lastUsecs;
          lastUsecs = thisUsecs;
          runSpeed = setups.mmPerCount * 1e6 / (float)(encoderUsecs);
          distance += setups.mmPerCount;  
          direction = BW;
       }       
    }  
}

void frameSend()
{ 
//   digitalWrite(3, HIGH);
   noInterrupts();
   uint8_t yval = ycounts;
   ycounts = 128;
   if(samples == 0) samples++; 
   outStream[1] = samples++; 
   interrupts();  
   outStream[3] = yval;
   outStream[5] = yval;
   Serial.write(outStream, 12);  
//   digitalWrite(3, LOW);
}


void setup()
{

  Serial.begin(192000);
  while( !Serial);
  
  pinMode(encAPin, INPUT_PULLUP); // sets the digital pin as input
  pinMode(encBPin, INPUT_PULLUP); // sets the digital pin as input
  pinMode(dirPin,  OUTPUT);
  
  pinMode(3, OUTPUT);             // testing
  digitalWrite(3, HIGH);
  digitalWrite(dirPin, LOW);
//  Serial.print("Treadmill Interface V: ");
//  Serial.println(VERSION);

   analogWriteResolution(12);

   EEPROM.get(0, setups );
   if( setups.flag != 0x55 )  // not inited yet
   {
      setups.flag = 0x55;
      setups.voltsPerMmPerSecond = .0025; // 2.5V for 1000 mm/sec
      setups.mmPerCount = 0.412;        // for small treadmill
      setups.reverseDirection = false;
      setups.showBackwards = true;       
      EEPROM.put(0, setups);
   }

   sampling = false;
   attachInterrupt(encAPin, encoderInt, RISING); // check encoder every A pin rising edge

   lastUsecs = micros();
   runSpeed = 0;

}

void loop() 
{
  noInterrupts();
  uint32_t now = micros();
  uint32_t lastU = lastUsecs;
  if( (now > lastU) && ((now - lastU) > SPEED_TIMEOUT)  )
  {   // now should never be < lastUsecs, but sometiems it is
      // I question if noInterupts works
     runSpeed = 0;
  }        
  if( abs( runSpeed - lastSpeed) > 0.001 )
  {   
      lastSpeed = runSpeed;   
      float dacval = DAC_CNTS_PER_VOLT * runSpeed * setups.voltsPerMmPerSecond; 
      if( dacval < 0 ) dacval = 0;
      if( dacval > maxDACval) dacval = maxDACval;
      if( runSpeed < 0.001 ) direction = FW;    // if zero - call it forward direction
      analogWrite(A14,(uint16_t) dacval);
      if( direction == FW )
          digitalWriteFast(dirPin, LOW);
      else
          digitalWriteFast(dirPin, HIGH);    
      if( showSpeed ) 
      {
          Serial.print( direction * runSpeed); 
          Serial.print(" ");
          Serial.println(dacval);
      } 
  }
  interrupts();  

    
  if (Serial.available())
  {
    uint8_t cmdin = Serial.read();
    // we will just process everything - only 254 and 255 matter, parameters (0,1) will be processed as commands and ignored
    switch(cmdin)
    {
//     case 0:
//        break;
//     case 1: 
//        break;
//     case 246: //Data return state.  0 = rotation coordinates, 1 = raw camera x/y
//        break;
     case '?':
         Serial.print("RDS interface with Speed and Direction Outputs V:");
         Serial.println(VERSION);
         Serial.println(" 'D' to start counting distance");
         Serial.println(" 'd' to stop and report distance");
         Serial.println(" 'S' to show speed and volts");
         Serial.println(" 's' to stop showing speed and volts");
         Serial.println(" 'C' to edit setup values");
         Serial.println(" 'c' to show setup values"); 
         break;
     case 'D':
         debug = true;
         counts = 0;
         break;
     case 'd':
         debug = false;
         Serial.print("Cnts:" );
         Serial.print(counts);
         Serial.print(", mm:");
         Serial.println((float)counts * setups.mmPerCount);
         break;    
     case 'S':
         showSpeed = true;
         break;
     case 's':
         showSpeed = false;    
         break; 
     case 'c':
        // Serial.println(setups.flag, HEX);
         Serial.print( "Volts/mm/sec: ");
         Serial.println(setups.voltsPerMmPerSecond,5);
         Serial.print( "mm/encoder count: ");
         Serial.println(setups.mmPerCount,5); 
         if( setups.reverseDirection ) 
            Serial.println("Direction sense reversed");
         else   
            Serial.println("Direction sense normal");
         if( setups.showBackwards ) 
            Serial.println("Backwards speed enabled");
         else   
            Serial.println("Backwards speed disabled");         
         break;
     case 'C':
         Serial.println("Enter new calibration values - NOTE:");
         Serial.println(" - a number is needed before '.'");
         Serial.println(" - all values must be entered, even if unchanged\r\n");
         Serial.print( "Volts/mm/sec (");
         Serial.print(setups.voltsPerMmPerSecond,5);
         Serial.print(") :");
         while( Serial.available()) Serial.read();
         while( Serial.available() == 0);
         setups.voltsPerMmPerSecond = Serial.parseFloat();
         Serial.println(setups.voltsPerMmPerSecond,5);
         
         Serial.print( "mm/encoder count (");
         Serial.print(setups.mmPerCount,5);
         Serial.print(") :");
         while( Serial.available()) Serial.read();
         while( Serial.available() == 0);
         setups.mmPerCount = Serial.parseFloat();   
         Serial.println(setups.mmPerCount,5);
         
         Serial.print( "Reverse Forward direction('y' or 'n')");
         if( setups.reverseDirection ) 
            Serial.print("y:");
         else   
            Serial.print("n:");
         while( Serial.available()) Serial.read();
         while( Serial.available() == 0);
         if( Serial.read() == 'y')
            setups.reverseDirection = true;       
         else
            setups.reverseDirection = false;
          if( setups.reverseDirection ) 
            Serial.println("y");
         else   
            Serial.println("n");
                       
         Serial.print( "Show Backwards on outputs ('y' or 'n')");
         if( setups.showBackwards ) 
            Serial.print("y:");
         else   
            Serial.print("n:");
         while( Serial.available()) Serial.read();
         while( Serial.available() == 0);
         if( Serial.read() == 'y')
            setups.showBackwards = true;       
         else
            setups.showBackwards = false;   
         if( setups.showBackwards ) 
            Serial.println("y");
         else   
            Serial.println("n");   

         EEPROM.put(0, setups);
         Serial.println( "saved");
         break;
     case 254: //'e': // //Stop Data Acquisition
        frameTimer.end();       
        sampling = false;
        ycounts = 128;
        samples = 1;
        break;
     case 255: // 'b': // //Start Data Acquisition        
        frameTimer.begin( frameSend, FRAMECLK);         
        sampling = true;      
        break;
     default:
        break;   
    } // end command switch 
    
  } // end serial in
  
}
