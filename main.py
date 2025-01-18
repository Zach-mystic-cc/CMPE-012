import time
import machine
import dht
from machine import ADC, Pin
import lcd_api
import pico_i2c_lcd
from machine import Pin, PWM

# Initialize I2C for the LCD (SDA on GP0, SCL on GP1)
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# Initialize the LCD
lcd = pico_i2c_lcd.I2cLcd(i2c, 39, 2, 16)

# Initialize DHT11/DHT22 sensor (GPIO2)
dht_sensor = dht.DHT22(machine.Pin(2))

# Initialize MQ-135 Air Quality Sensor (GPIO26) using ADC
mq_sensor = ADC(Pin(26))  # GPIO26 (ADC0) on Pico

# Initialize Passive Buzzer (GPIO4)184
buzzer = PWM(Pin(4))  # PWM pin
buzzer.freq(1000)     # Set frequency to 1000Hz (audible tone)

# Initialize LEDs (GPIO 5, 6, 7)
leds = {
    "healthy": machine.Pin(5, machine.Pin.OUT),
    "mediocre": machine.Pin(7, machine.Pin.OUT),
    "very_unhealthy": machine.Pin(8, machine.Pin.OUT),  # Add this line for "VERY unhealthy"
}


# Function to reset all LEDs
def reset_leds():
    for led in leds.values():
        led.value(0)

# Function to get humidity and temperature
def get_humidity_temp():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()  # Temperature in °C
        humidity = dht_sensor.humidity()  # Humidity in %
        return temp, humidity
    except OSError as e:
        print(f"Error reading DHT sensor: {e}")
        return None, None

# Function to get air quality
def get_air_quality():
    try:
        value = mq_sensor.read_u16()  # Reads a 16-bit analog value (0–65535)
        return value
    except Exception as e:
        print(f"Error reading MQ sensor: {e}")
        return -1

# Function to sound the buzzer
def sound_buzzer(frequency, duration, volume=100):
    """
    Sound the buzzer for a given duration and volume.
    :param frequency: Frequency in Hz (pitch)
    :param duration: Duration in seconds
    :param volume: Volume as a percentage (0-100)
    """
    buzzer.freq(frequency)             #Set the pitch
    duty = int((volume / 100) * 65535)  # Convert volume % to duty cycle (0-65535)
    buzzer.duty_u16(duty)              # Set the duty cycle
    time.sleep(duration)               # Keep the buzzer on for 'duration'
    buzzer.duty_u16(0)                 # Turn off the buzzer

# Function to make LEDs flicker
def flicker_leds(cycles=5, delay=0.2):
    for _ in range(cycles):
        for led in leds.values():
            led.value(1)
            time.sleep(delay)
            led.value(0)

# Function to set LEDs based on air quality
def set_leds(air_quality_value):
    # Define thresholds for air quality
    healthy_threshold = 5000   # Adjusted for 16-bit ADC values
    mediocre_threshold = 10000
    very_unhealthy_threshold = 15000

    reset_leds()

    # Set LEDs based on the air quality
    if air_quality_value < healthy_threshold:
        leds["healthy"].value(1)  # Healthy air quality
    elif healthy_threshold <= air_quality_value < mediocre_threshold:
        leds["mediocre"].value(1)  # Mediocre air quality
        sound_buzzer(2000, 1)
    else:
        leds["very_unhealthy"].value(1)  # Unhealthy air quality
        sound_buzzer(2000, 5)

 # Define thresholds for air quality
def get_air_quality_status(air_quality_value):
    
    healthy_threshold = 5000
    mediocre_threshold = 10000
    very_unhealthy_threshold = 15000

    if air_quality_value < healthy_threshold:
        return "Healthy"
    elif healthy_threshold <= air_quality_value < mediocre_threshold:
        return "Mediocre"
    else:
        return "Very Unhealthy"


# Function to log data
def log_data(temp, humidity, air_quality):
    try:
        with open("data_log.txt", "a") as log_file:
            log_file.write(f"{time.time()}, {temp}, {humidity}, {air_quality}\n")
    except OSError as e:
        print(f"Error logging data: {e}")

# Function to display greeting message
def display_greeting():
    lcd.clear()
    lcd.putstr("Env Monitor")
    lcd.move_to(0, 1)  # Move to column 0, row 1
    lcd.putstr("By Group 4")
    flicker_leds()
    time.sleep(2)

# Function to display credits
def display_credits():
    credits = ["John Victor D.", "Jhonel F.", "Janelle A.", "Elaine M."]
    for name in credits:
        lcd.clear()
        lcd.putstr("Created by:")
        lcd.move_to(0, 1)
        lcd.putstr(name)
        flicker_leds()
        time.sleep(2)
    lcd.clear()
    lcd.putstr("Thank you!")
    lcd.move_to(0, 1)
    lcd.putstr(":)")
    flicker_leds()
    time.sleep(2)


# Function to display data on LCD and check air quality
def display_data():
    last_reset_time = time.time()
    while True:
        try:
            # Display greeting every 5 minutes
            if time.time() % 300 < 5:
                display_greeting()

            # Reset sensors every 10 minutes to prevent drift
            if time.time() - last_reset_time > 600:
                machine.reset()

            # Get temperature, humidity, and air quality
            temp, humidity = get_humidity_temp()
            air_quality = get_air_quality()
            
            # Determine air quality status
            air_quality_status = get_air_quality_status(air_quality)

            # Display data on LCD
            lcd.clear()
            if temp is not None and humidity is not None:
                lcd.putstr("Temp:{:.1f}C".format(temp))
                lcd.move_to(0, 1)
                lcd.putstr("Hum:{:.1f}%".format(humidity))
                time.sleep(2)

                lcd.clear()
                lcd.putstr(f"AQI: {air_quality}")
                lcd.move_to(0, 1)
                lcd.putstr(air_quality_status)
                
            else:
                    lcd.putstr("Sensor error")
                    lcd.move_to(0, 1)
                    lcd.putstr("AQI:{}".format(air_quality))
            
           
           
            # Log data
            log_data(temp, humidity, air_quality)

            # Set LEDs based on air quality
            set_leds(air_quality)

            time.sleep(5)  # Wait 5 seconds before the next cycle

        except Exception as e:
            print(f"Unexpected error: {e}")
            lcd.clear()
            lcd.putstr("System error")
            time.sleep(5)

# Main function
if __name__ == "__main__":
    print("Starting Environment Monitor...")
    try:
        display_greeting()
        display_credits()
        display_data()
    except KeyboardInterrupt:
        print("Shutting down...")
        lcd.clear()
        reset_leds()
        buzzer.value(0)

