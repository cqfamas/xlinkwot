// Xlink examples
//
// xiaoyu <xiaokong1937@gmail.com>
//
// 2014/12/26
// 
#include <Bridge.h>
#include <String.h>
#include <Process.h>

// Xlink apis
#define APIKEY "727c554409d5fa166860008db638582d5728" // Apikey of Xlink 
#define APIUSER "apiuser" // Username of Xlink 
#define SENSORID "4" // Sensor ID
#define DEFAULT_CMD "off" // Default command used for execCommand
// String that store the current command.
String command;

void setup() {
  // Bridge takes about two seconds to start up
  // it can be helpful to use the on-board LED
  // as an indicator for when it has initialized

  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  digitalWrite(13, LOW);

  Bridge.begin();
  digitalWrite(13, HIGH);

  Console.begin();

  while (!Console); // wait for a serial connection
  Console.println("Console ready.");
}

void loop() {
  digitalWrite(12, LOW);
  // Get command from xlink server.
  command = getCommand();
  Console.print(command);
  // Execute the command.
  execCommand(command);
  delay(3000);
}

String getCommand() {
  Process p;
  String cmd="";
  p.begin("xlink");
  p.addParameter("get_sensor_cmd");
  p.addParameter("-k");
  p.addParameter(APIKEY);
  p.addParameter("-u");
  p.addParameter(APIUSER);
  p.addParameter("-s");
  p.addParameter(SENSORID);
  p.run();
  
  while (p.available()>0) {
    char c = p.read();
    Console.print(int(c));
    cmd.concat(c);
  }
  cmd.trim();
  if (cmd == ""){
    return DEFAULT_CMD;
  }
  return cmd;
}

void execCommand(String command){
  if (command == "on" ){
    digitalWrite(12, HIGH);
  }else{
    digitalWrite(13, LOW);
  };
}
