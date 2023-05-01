// Peltier sensing and PID control
// ken iiyoshi. 
// Oct 19
#include <PID_v2.h> // for PID control
// #include <movingAvg.h>  //for filtering input. not used for now. https://github.com/JChristensen/movingAvg
// movingAvg avgTemp(5);      
#include <LiquidCrystal.h>
// from https://create.arduino.cc/projecthub/najad/interfacing-lcd1602-with-arduino-764ec4
// updated Feb 13, 2023:https://www.hackster.io/najad/interfacing-lcd1602-with-arduino-764ec4
// apr 19th: update below by adding the wire mapping. Worst case, redo the process with newer tutorials.
// change: for en, pin 6 is used instead of 11
// const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;

// Pin Mappings Arduino Uno pins to LCD1602 pins based on the link:
// Generally order from the leftmost to rightmost LCD pins, when the pens are oriented on the top left
// when the LCD screen is facing up:
// GND - VSS, V0, RW, K
// 5V - V00
// 12 - R5
// 11 - E
// 2 = D7
// 3 - D6
// 4 - D5
// 5 - D4
// 3.3V - A

const int rs = 12, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


//TEC element driver pins
int pinINA = 10;
int pinINB = 11;
float setpoint = 24.0 ; 
//Analog pin for thermocouple is A0
String myStr= "" ;
float raw_input = 0.0;
float filtered_input = 0.0;
float old_input = 0.0;
double output; //PID output
//original
//double Kp = 2, Ki = 5, Kd = 1;
// from nov1, before adding top heatsink and replacing peltier cell double Kp = 6.60, Ki = 0.4, Kd = 1.40; 
// double Kp = 6.60, Ki = 0.4, Kd = 1.40;  
// with larger Ki, there is more overshoot, which is handy for crystal actuation
double Kp = 6.60, Ki = 2.4, Kd = 1.40; //nov 3rd
PID_v2 myPID(Kp, Ki, Kd, PID::Direct);
float avg;
int timeElapsed = 0;
int heatingTransTemp = 46;
int coolingTransTemp = 32;

void setup() {
  //setup LCD. Upon compilation, the first row is white, and 2nd row is dark
  // use that to check if the camera is working.
  lcd.begin(16, 2);
  lcd.print("Don't touch,");
  lcd.setCursor(0,1);
  lcd.print("it costs $10k!");
  
  
  // Setting driver pins to OUTPUT
  pinMode(pinINA, OUTPUT);
  pinMode(pinINB, OUTPUT);
  Serial.begin(115200);
//  Serial.print("Temperature: ");
  Serial.println(getTemp());
  // avgTemp.begin();
  myPID.Start(getTemp(),  // input
              0,          // current output
              setpoint);  // setpoint
  myPID.SetOutputLimits(-255, 255);


}

void loop() {
  
  // user-control through serial communication.
  if(Serial.available())
  {
    myStr=Serial.readString();
    setpoint = myStr.toFloat();
    myPID.Start(getTemp(),  // input
              output,                      // current output
              setpoint);
  }
  
  // //for TBB, want to  between 32 and 46˚C as in, we want the setpoint plot to look like:_/``\_/``\_
  // // overshoots when starting temperature is far away from these values.
  // if(filtered_input>=heatingTransTemp)
  // {
  //   setpoint = coolingTransTemp;
  //   myPID.Start(getTemp(),  // input
  //             output,                      // current output
  //             setpoint);
  // }
  // else if (filtered_input<=coolingTransTemp) {
  //   setpoint = heatingTransTemp;
  //   myPID.Start(getTemp(),  // input
  //             output,                      // current output
  //             setpoint);
  // }


  // put your main code here, to run repeatedly:
  // filter input and feed it to PID control.
  // input = getTemp();
  raw_input = getTemp();
  filtered_input = 0.85*old_input + 0.15*getTemp();
  old_input = filtered_input;
  // avg = avgTemp.reading(input);
  // output = myPID.Run(avg);
  output = myPID.Run(filtered_input);

  // controls h-bridge based on required PID output
  if (output >= 0)
  {
    analogWrite(pinINA, int(output));
    analogWrite(pinINB, 0);
  }
  else
  {
    analogWrite(pinINA, 0);
    analogWrite(pinINB, abs(int(output)  ));
  }

// For printing values on serial monitor and serial plotter.
// Serial.print(avg);
// Serial.print("raw_input:");
// Serial.print(raw_input);
// Serial.print(", ");
Serial.print("filtered_input:");
Serial.print(filtered_input);
Serial.print(", ");
Serial.print("setpoint:");
Serial.print(setpoint);
// Serial.print(input);
Serial.print(", ");
Serial.print("output/100:");
Serial.println(output/100.0); //maps [-255,255] to [-2.5,2.5]
// delay(500);
delay(100);
}

float getTemp() {
  int an_value = analogRead(A0);
  // apr27, 2023 edit:
  float mid_value = ((float(an_value) / (1024.0 - 1.0)) * 5.0 - 1.25) / 0.005 +18.00;
  // float mid_value = ((float(an_value) / (1024.0 - 1.0)) * 5.0 - 1.25) / 0.005;
  // return ((float(an_value) / (1024.0 - 1.0)) * 5.0 - 1.25) / 0.005 - 6.0; // before nov 1st. maps [0,1023]mV*˚C to [-256, 744]˚C . 31.39 or 32.37 , 32.7 actually
  // Nov 1. fixing temperature difference: finger:31.8vs 46.0 (14 deg difference). ambient:22 vs 36 (14 degrees difference)) 
  // note that the amount of offset compensation fluctuates when the temperature increases. i.e. ±5 degrees between 20~50˚C.
  // return mid_value - 21.0; // maps [0,1023]mV*˚C to [-256, 744]˚C . 31.39 or 32.37 , 32.7 actually
    // return mid_value - 13.5; from nov 3
    // return mid_value - 10.5; //for nov 16th thermal imaging
    // return mid_value - 26.0; //for nov 20th thermal imaging
    // return mid_value - 7.0; //for nov 29th thermal imaging
    // return mid_value - 26.0; //for nov 20th thermal imaging
    return mid_value - 16.0; //for nov 20th thermal imaging
}


///********************************************************
// * PID Basic Example
// * Reading analog input 0 to control analog PWM output 3
// ********************************************************/
//
//#include <PID_v2.h>
//
//#define PIN_INPUT 0
//#define PIN_OUTPUT 3
//
//// Specify the links and initial tuning parameters
//double Kp = 2, Ki = 5, Kd = 1;
//PID_v2 myPID(Kp, Ki, Kd, PID::Direct);
//
//void setup() {
//  myPID.Start(analogRead(PIN_INPUT),  // input
//              0,                      // current output
//              100);                   // setpoint
//}
//
//void loop() {
//  const double input = analogRead(PIN_INPUT);
//  const double output = myPID.Run(input);
//  analogWrite(PIN_OUTPUT, output);
//}
