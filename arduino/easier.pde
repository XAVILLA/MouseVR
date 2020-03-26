// MouseoVeR - software for interactive Virtual Reality
// Jeremy Cohen (2010-2014)

// this software can communicate (via serial port, RS-232) with the virtual
// reality game engine "MouseoVeR"

// this software can also communicate (via serial port, usb) with the matlab
// GUI "MouseoVeR_(ver).m"

// pin 13 on the Arduino Mega and chipKit max32 board is connected to a red LED
#define LED_PIN   13
// BCS ver C hookup
#define SOLENOID1 29
#define SOLENOID2 28
#define SOLENOID3 27
#define SOLENOID4 26
#define SOLENOID5 25
#define SOLENOID6 24
#define SOLENOID7 23
#define SOLENOID8 22

#define BEAM1     37
#define BEAM2     36
#define BEAM3     35
#define BEAM4     34
#define BEAM5     33
#define BEAM6     32
#define BEAM7     31
#define BEAM8     30

#define DIGITAL1  4 //69            // DIGITAL1 is the reward (RD) signal
#define DIGITAL2  5 //68            // Frame Flashes (FF) signal to the cameras.
#define DIGITAL3  6 //67            // Protocol Markers (PM) (or SYNC 'S' pulses from Heka)
#define DIGITAL4  8 //66            // Start/Stop video recording signal, HIGH=videoRecON, LOW=videoRecOFF
#define DIGITAL5  20 //6            // Licks (LK)
#define DIGITAL6  21 //6             // TTL to step command gate on Dagan amplifier
#define DIGITAL7  A0 //63
#define DIGITAL8  A1 //62

// Chip select pins used with the SPI interface
#define ADC_PIN   49
#define DAC1_PIN  53
#define DAC2_PIN  48

#define LINE_BUFFER 128
#define VR_BUFFER 128
#define EVENT_STRING 32

#define ENDPOS 533000

// Zaber servomotor command numbers
#define HOME_CMD 1 // for "homepos" string
#define STORE_POS_CMD 16 // not used
#define MOVE_STORED_POS__CMD 18 // not used
#define MOVE_ABSOLUTE_CMD 20 // for "moveto" string
#define MOVE_RELATIVE_CMD 21 // not used
#define STOP_CMD 23 // for "servoStop" string
#define SET_SPEED_CMD 42 // for "setSpeed" string
#define SET_ACC_CMD 43 // for "setAccel" string
#define SET_MAX_POS_CMD 44 // for "setMaxPos" string
#define SET_MICROSTEP_RES_CMD 37 // for "setMicrostepRes" string


// include the spi library code:
#include <SPI.h>
// - and required BCSIII header files -
#include <CS.h>            // !!! Mandatory header for SPI chip select routines
#include <MCP23S17.h>      // !!! Mandatory header for Beam break I/O
#include <BCSIII.h>        // !!! Mandatory header file for BCSII main board functions
#include <DRIVER.h>        // header file for solendoid driver panel functions
#include <ADC_AD7328.h>    // header file for ADC panel functions
#include <DAC_AD57x4.h>    // header file for DAC panel functions
#include <LCD2x16.h>       // header file for LCD panel functions


////////////
// FUNCTIONS
////////////

void parse(char *line, char **argv, uint8_t maxArgs) { // parse script
  uint8_t argCount = 0;
  while (*line != '\0') {       /* if not the end of line ....... */

    while (*line == ',' || *line == ' ' || *line == '\t' || *line == '\n') // if one of these chars detected
      *line++ = '\0';     /* replace commas and white spaces with 0    */
    *argv++ = line;          /* save the argument position     */
    argCount++;
    if (argCount == maxArgs-1)
      break;
    while (*line != '\0' && *line != ',' && *line != ' ' &&
      *line != '\t' && *line != '\n') // if char is not one of these, keep reading
      line++;             /* ie, skip the argument until ...    */
  }
  *argv = line;                 /* mark the end of argument list  */
}

long getValue(char *arg) {
  char input[16];
  char *inp;
  uint8_t cnt;

  inp = input;
  cnt = 0;
  while ((*arg != '\0')&&(cnt < 16)) {
    if (*arg != '.') {
      *inp++ = *arg;
      cnt++;
    }
    *arg++;
  }
  *inp++ ='\0';
  return atol(input);
}

void printTimestamp() {
  uint32_t msec;
  uint16_t usec;
  uint64_t ts;
  // get the time stamp
  ts = getTimestamp();
  msec = (uint32_t)(ts/1000);
  usec = (uint16_t)(ts % 1000);
  printTime(msec, usec);
}

void printRD() {
  digitalWrite(DIGITAL1, HIGH);
  printTimestamp();
  sprintf(stringBuff, "TTT"); // indicate a reward event string
  printlnString0((char*)stringBuff);
  RD_cnt++;
  RD_cnt_curr=RD_cnt_curr+100;
  RD_tag = 1;  //the marker meaning that a reward has already been sent. Used to avoid multiple reward for lick-dependent protocol. This tag is reset to 0 by new location event.
  lk_cnt = 0; //reset lick count
  uart1_put(0x80); // row 0, col 0
  Serial1.print(0x0c, BYTE); // clear the display
  sprintf(stringBuff, "RD delivered"); //
  printString1((char*)stringBuff);
  delay(100);
  digitalWrite(DIGITAL1, LOW);
}

void printEN() {
  digitalWrite(DIGITAL1, HIGH);
  printTimestamp();
  sprintf(stringBuff, "EN");
  printlnString0((char*)stringBuff);
  digitalWrite(DIGITAL1, LOW);
}







void setup() {
  bcs.begin();    // !!! first, initialize the BCS
  // and then the panels

  pinMode(LED_PIN, OUTPUT); // Green LED on the front


  bcs.setIO( 1, DIGITAL1, OUTPUT); // pinMode(DIGITAL1, OUTPUT); // DIGITAL1 is the reward (RD) signal
  bcs.setIO( 5, DIGITAL5, INPUT);// pinMode(DIGITAL5, INPUT);  // Licks (LK)

  // PC communications
  Serial.begin(115200);
  sprintf(stringBuff, "0,FR,MouseoVeR BCS firmware revision 7X4");
  printString0((char*)stringBuff);
  printNewline0();

  // LCD communication
  Serial1.begin(19200);
  Serial1.print(0x0c, BYTE); // clear the display
  delay(100); // im ms
  Serial1.print(0x11, BYTE); // Back-light on
  Serial1.print("* Hello Xinyu *   (Ver. 8)");

  // VR communication
  Serial2.begin(115200);

  // Servo motor communication - multiple Zaber motors, daisy chained
  Serial3.begin(9600);

  idx = 0;
  vr_idx = 0;

  // once per initialization, start the randomSeed for random();
  // use the current usec time for the randomSeed seed (will provide a different seed each time)
  uint64_t ts;
  ts = getTimestamp(); // get the timestamp
  randomSeed(ts); // randomSeed for random();


  // Init done
  digitalWrite(LED_PIN, HIGH);

  delay(2000); // 2000ms delay to view LCD messages

} // END void setup()


/////////////////////////////////////////////////
// THE CLOCK AND DATA PROCESSING LOOP STARTS HERE
/////////////////////////////////////////////////

void loop() {
  uint8_t c, i;

  for (;;) {

    // get the time when starting the loop
    uint64_t ts;
    ts = getTimestamp(); // get the time stamp

/*
    // Test Code for sending a test string every 10 ms to Matlab
    if ((millis() % 50) == 0) {
      if ((millis() > 10000) && (millis() < 20000) && (tflag == 0)) {
        printTimestamp();
        sprintf(stringBuff, "Time,");
        printString0((char*)stringBuff);
        printValue0_U32(millis());
        printNewline0();
        tflag = 1;
      }
    } else {
      tflag = 0;
    }
*/
/*
    // Test Code - for updating the LCD display every second with information
    new_ms = millis();
    if (new_ms - old_ms >= 1000) {
      old_ms = new_ms;
      int count = Serial.txCount();
      int s = 0;
      int m = 0;
      int h = 0;
      while (new_ms > 3600000) {
        h++;
        new_ms -= 3600000;
      }
      while (new_ms > 60000) {
        m++;
        new_ms -= 60000;
      }
      while (new_ms > 1000) {
        s++;
        new_ms -= 1000;
      }
      sprintf(stringBuff, "%c%02d:%02d:%02d  %d", 0x0c,h,m,s,count);
      printString1((char*)stringBuff);
      // also print the count
      printTimestamp();
      sprintf(stringBuff, "txCount,");
      printString0((char*)stringBuff);
      printValue0_U32(count);
      printNewline0();
    }
*/


    if (Serial.available() > 0) { // PC communication via usb (Online matlab GUI)
      c = Serial.read(); // read port
      //Serial.print(c); echo back, test code
      if (c == '\r') { // end of line
        buffer[idx] = 0; // reset buffer counter
        parse((char*)buffer, argv, sizeof(argv)); // parse buffer into args,see void parse()
        // process buffer. (read usb inputs from Matlab gui)

        if (strcmp(argv[0], "lick_RD") == 0) {

          lick_RD = atoi(argv[1]);
          if (lick_RD) {
            uart1_put(0x80); // row 0, col 0
            Serial1.print(0x0c, BYTE); // clear the display
            Serial1.print(0x80, BYTE); // move the cursor to the start
            sprintf(stringBuff, "Lick ON!");
            printString1((char*)stringBuff);
          }
          else {
            uart1_put(0x80); // row 0, col 0
            Serial1.print(0x0c, BYTE); // clear the display
            Serial1.print(0x80, BYTE); // move the cursor to the start
            sprintf(stringBuff, "Lick OFF!");
            printString1((char*)stringBuff);
          }

        }

        else if (strcmp(argv[0], "rdson") == 0) {
          RDS_AD = 1;
        }
        else if (strcmp(argv[0], "rdsoff") == 0) {
          RDS_AD = 0;
        }
        else if (strcmp(argv[0], "drips") == 0) {
          num_drips = atoi(argv[1]);
        }
        else if (strcmp(argv[0], "rewardend") == 0) {
          reward_area_num = 1;
        } 
        else if (strcmp(argv[0], "rewardmiddle") == 0) {
          reward_area_num = 0;
        }
        else if (strcmp(argv[0], "RD_cnt") == 0) {
          RD_cnt=atoi(argv[1]);
        }
        else if (strcmp(argv[0], "RD_cnt_curr") == 0) {
          RD_cnt_curr=atoi(argv[1]);        }
        }
        else if (strcmp(argv[0], "startTraining") == 0) {
          endpos = 400000; // hardcoded for now
          homepos = 1; // hardcoded for now
          training = 1;
        }
        else if (strcmp(argv[0], "stopTraining") == 0) {
          training = 0;
          servoCommand(1,STOP_CMD,0);
        }
        else if (strcmp(argv[0], "reward") == 0) {
          printRD();
        }
        else if (strcmp(argv[0], "videoRecON") == 0) {
          videoRecON();
        }
        else if (strcmp(argv[0], "videoRecOFF") == 0) {
          videoRecOFF();
        }
        else if (strcmp(argv[0], "loopTimeMaxReset") == 0) {
          loopTimeMax = 0;
        }
        else if (strcmp(argv[0], "overflow") == 0) {
          printValue0_U32((uint32_t)pcrxovf);
          uart0_put(',');
          printValue0_U32((uint32_t)vrrxovf);
          printNewline0();
        }
        idx = 0;
      }
      else if (((c == '\b') || (c == 0x7f)) && (idx > 0)) {
        idx--;
      }
      else if ((c >= ' ') && (idx < sizeof(buffer) - 1)) {
        buffer[idx++] = c;
      }
    } // END serial loop for PC communication



///////////////////////////////////
// DIGITAL INPUT-SPECIFIC RESPONSES
///////////////////////////////////


    if (digitalRead(DIGITAL4) == HIGH) {
      if (pm_sent == 0) {
        printTimestamp();
        sprintf(stringBuff, "LK"); // indicate a Lick event, attached to string string
        printlnString0((char*)stringBuff);
        pm_sent = 1;
      }
    }
    else {
      pm_sent = 0;
    }

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Lick detection triggered by the rising edge of digital 5. When it's reviously LOW (lk_sent=0) but now HIGH, lk_tag was set to 1.
// Falling edge does not set lk_tag to 0. lk_tag is reset to 0 by reward delivery (see lick-dependent RDS).

    if (digitalRead(DIGITAL5) == HIGH) {
      if (lk_sent == 0) {
        printTimestamp();
        sprintf(stringBuff, "LK"); // indicate a lick event string
        printlnString0((char*)stringBuff);  //to the PC
        lk_sent = 1;
        //lk_tag = 1;

        //lk_cnt ++;  //update th lick count. The lick count is reset to 0 when the animal move to a new location or a reward is delivered.

        //Serial1.print(0x99, BYTE); //move the cursur to position 5 (counted from 0), the second line.
        //if (lk_cnt==0) {
        //     sprintf(stringBuff, "0"); //show the lick count;
        //}
        //else if (lk_cnt==1){
        //  sprintf(stringBuff, "1");
        //}
        //else if (lk_cnt==2) {
        //  sprintf(stringBuff, "2");
        //}
        //else if (lk_cnt==3) {
        //  sprintf(stringBuff, "3");
        //}
        //else if (lk_cnt>3) {
        //  sprintf(stringBuff, "M");
        //}
        //printString1((char*)stringBuff);

      }
    }
    else {
      lk_sent = 0;
    }
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



//////////////////////////////////////////////////////////
// FINAL CHECKS - UPDATE BEHAVIORAL SCORES - PRINT CHANGES
//////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////
//  THIS IS THE LAST SECTION OF CODE, CALCULATES PROCESSING LOOP TIME
/////////////////////////////////////////////////////////////////////

    // get the time stamp
    loopTime_us = getTimestamp() - ts;
    // see if this is the longest ever
    if (loopTime_us > loopTimeMax) {
      loopTimeMax = loopTime_us;
      printTimestamp();
      sprintf(stringBuff, "MaxLoopTime,");
      printString0((char*)stringBuff);
      printValue0_U32(loopTimeMax);
      printNewline0();
    }


  } // END for (;;) loop
} // END void loop()

