These code contains the neccessary commands in order to run the Sustainable Prototype Development Project:
 “Solar-Powered Air Quality Monitoring System” each line of code serves a purpose towards each of the individual modules
The I2C LCD is used to display the air quality, air humidity, air temperature, and so on.
The devices that are being used to measure these variables are called the DHT 22, MQ 135 and a passive buzzer module and LEDS that lights up corresponding to the air quality given
When the LED turns green that means the air quality present is healthy, however when it turns yellow it means its unhealthy thus signaling the buzzer to ring and furthermore
When the LED turns red thats means the air quality is very bad or rather very unhealthy thus making the buzzer ring a long time. Those are functions of each of the devices used in this project.
The devices names are the following "DHT22", "MQ 135", "PASSIVE BUZZER MODULE", "GREEN, YELLOW, RED LEDS".
The prototype can function on many ways it can be done by connecting the VBUS towards the solar charge controller thus using up the power stored in the battery via the solar panels voltage which then goes through a step down or "AC TO DC" 
The step down voltage used is a "LM2596" the prototype can also be run by simply connecting a type a cable to the raspberry pi pico into a usb slot in either a computer or a laptop.

The whole process is explained within the project charter.
