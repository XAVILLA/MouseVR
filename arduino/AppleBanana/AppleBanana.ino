// Arduino code for AppleBanana experiment
// Simpler time implementation.

#define REWARD 2//pin for digital output to Reward delivery system
#define LICK 4//pin for digital input from Lick sensors
#define SHOCK 6//pin for digital output to Shock delivery system
#define LICKLED 9 //pin for digital output to lickport led


/////////////
//VARIABLES//
/////////////
char *argv[32]; // input line arguments (as character strings)
char c;
char buffer[128];
int idx;
uint8_t verbose;
uint8_t isSanworks;
uint8_t isPumpOn;
uint8_t lk_sent; // state for whether or not a lick signal has been sent, 0=not sent, 1=sent
uint8_t target;
unsigned long pumpStartTime; 
unsigned long pumpDelay;
int brightness;

/////////////
//FUNCTIONS//
/////////////
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
    // get the time stamp
    Serial.print(micros());
    Serial.print(",");
}

void printRD() {
    digitalWrite(REWARD, HIGH);
    if (verbose){
        printTimestamp();
        Serial.println("TTT");
    }
    delay(100);
    digitalWrite(REWARD, LOW);
}




/////////
//SETUP//
/////////
void setup() {
    verbose = 0;
    lk_sent = 1;
    isSanworks = 1;
    pinMode(REWARD, OUTPUT); // Reward delivery
    pinMode(LICK, INPUT);  // Lick Detection
    pinMode(SHOCK,OUTPUT); // Shock delivery
    pinMode(LICKLED,OUTPUT); // Lickport led delivery
    digitalWrite(REWARD, LOW);
    digitalWrite(SHOCK,LOW);
    analogWrite(LICKLED,LOW);
    brightness = 0;
    pumpDelay =10000000;

    // PC communications
    Serial.begin(115200);
    Serial.println("0,ArduinoInitialized");
} 

void loop() {
    if (Serial.available() > 0) { // PC communication via usb (Online matlab GUI)
        c = Serial.read(); // read port
        if (c == '\r') { // end of line
            buffer[idx] = 0; // reset buffer counter
            parse((char*)buffer, argv, sizeof(argv)); // parse buffer into args,see void parse()
            // process buffer. (read usb inputs from Matlab gui)
            if (strcmp(argv[0], "reward") == 0) {
                printRD();
            }
            else if (strcmp(argv[0], "timestamp") == 0) {
                printTimestamp();
                Serial.println("timestamp");
            }
            else if (strcmp(argv[0], "shock") == 0) {
                if (verbose){
                    printTimestamp();
                    Serial.println("SHOCK");
                }
                digitalWrite(SHOCK,HIGH);
                delay(100);
                digitalWrite(SHOCK,LOW);
            }
            else if (strcmp(argv[0], "verbose") ==0) {
                verbose = 1;
                Serial.println("0,verbose");
            }
            else if (strcmp(argv[0], "quiet") == 0) {
                verbose = 0;
            }
            else if (strcmp(argv[0], "sanworks") == 0) {
                isSanworks = 1;
            }
            else if (strcmp(argv[0], "panasonic") == 0) {
                isSanworks = 0;
            }
            else if (strcmp(argv[0], "startpump") == 0) {
                digitalWrite(REWARD,HIGH);
                if (verbose) {
                    Serial.println("0,startpump");
                }
                pumpStartTime = micros();
                isPumpOn = 1;

            }
            else if (strcmp(argv[0], "stoppump") == 0) {
                digitalWrite(REWARD,LOW);
                isPumpOn = 0;
                if (verbose) {
                    Serial.println("0,stoppump");
                }
            }
            else if (strcmp(argv[0], "brightness") ==0) {
                brightness = atoi(argv[1]);
                if (verbose) {
                    Serial.print(brightness);
                    Serial.print(",");
                    Serial.println("brightness");
                }
            }
            else {
                if (verbose) {
                    Serial.print("Cannot recognize :");
                    Serial.println(argv[0]);
                }
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
    if (isSanworks) {
      target = HIGH;
    }
    else {
      target = LOW;
    }
    if (digitalRead(LICK) == target)  {
        analogWrite(LICKLED,brightness);
        if (lk_sent == 0) {
            if (verbose){
                printTimestamp();
                Serial.println("LK");  //to the PC
            } else {
                Serial.println("0,LK");
            }
            lk_sent = 1;
            //delay(10);
        }
    }
    else {
        digitalWrite(LICKLED,LOW);
        lk_sent = 0;
    }
    if (isPumpOn && micros() - pumpStartTime > pumpDelay) {
            digitalWrite(REWARD,LOW);
            if (verbose) {
              Serial.println("0,stoppump");
            }
            isPumpOn = 0;
    }
}
