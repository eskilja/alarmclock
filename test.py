from flask import Flask, request
from time import sleep
from enum import Enum
from queue import Queue, Empty, Full
import threading
import time
import datetime
import requests
import random
import pygame
import os

#kanskje legg til sånn at klokken vekker deg 10 min før om det er kaldt ute
#angående hvor mye du snur Rpi så har det en effekt på spillet

#just so that it works on computers as well
try:
    from sense_hat import SenseHat
    sense = SenseHat()
except:
    sense = None


#starts pygame mixer
pygame.mixer.init()

app = Flask(__name__)
alarms = []
alarm_is_active = False
curweather = ""
ttemp = ""
temp_onoff = False
weather_onoff = False
current_display = None
on_off = 0
screen = 0
alarm_on = 2
Game = 1
joystick_queue = Queue(maxsize=3)

class Joystick(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    MIDDLE = 5

O = [0, 0, 0]       # Black (Off)
W = [255, 255, 255] # White (On)
T = [255,0,0]       #Red (off is true)

# Define the "ON" pattern
on = [
    O, O, O, O, O, O, O, O,
    O, W, O, O, W, O, O, W,
    W, O, W, O, W, W, O, W,
    W, O, W, O, W, W, O, W,
    W, O, W, O, W, O, W, W,
    O, W, O, O, W, O, W, W,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
]

# Define the "OFF" pattern
offselect = [
    O, O, O, O, O, O, O, O,
    O, T, O, T, T, O, T, T,
    T, O, T, T, O, O, T, O,
    T, O, T, T, T, O, T, T,
    T, O, T, T, O, O, T, O,
    O, T, O, T, O, O, T, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
]

offfalse = [
    O, O, O, O, O, O, O, O,
    O, W, O, W, W, O, W, W,
    W, O, W, W, O, O, W, O,
    W, O, W, W, W, O, W, W,
    W, O, W, W, O, O, W, O,
    O, W, O, W, O, O, W, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
]

#mabye print the ip adress on startup

# Replace with your OpenWeatherMap API key
API_KEY = '9fe7bc1bc1f94de3538a3338cfb6087a'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
city = "Oslo"  # Replace with your desired city

# Function to get weather data
def get_weather():
    global curweather
    global ttemp
    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'  # Use 'imperial' for Fahrenheit
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = ['description']
            curweather = f"{description.capitalize()}"
            ttemp = f"{temp}°C"
            return (curweather, temp)
        else: 
            curweahter = "Weather data unavalible"
            ttemp = "Weather data unavalible"
            return "Weather data unavailable" or (curweather, temp)
    except Exception as e:
        curweather = "error fetching weather data"
        ttemp = "error fetching weather data"
        return "Error fetching weather data" or (curweather, temp)

def check_alarms():
    global alarm_is_active, alarm_on
    while True:
        now = datetime.datetime.now()
        day_week = now.weekday()
        weathercheck = get_weather()
        #print("Current time:", now)
        #print("Day of the week:", day_week)
        #print("Alarms:", alarms)

        if ttemp == "error fetching weather data" or ttemp == "Weather data unavalible":
            mintemp = 0
            #print("mintep (ttemp didnt work)", mintemp)
        else:
            try:
                mintemp = float(ttemp)  # Convert ttemp to a float
            except ValueError:
                mintemp = 0  # Handle invalid numeric values by assigning a default
                #print("it didnt work :(")
                #print("mintemp", mintemp)
                #print("again ttemp", ttemp)

        for alarm in alarms:
            if mintemp <= 0:
                #print("Alarm set for day", alarm["day"], "hour", alarm["hour"], "minute", alarm["minute"])
                i = 0
                i += (-2 * mintemp)

                if (now.hour*60+now.minute, day_week) == (alarm["hour"]*60+alarm["minute"]-i, alarm["day"]):
                    print("Alarm triggered!")
                    alarm_on = 0
                    alarm_is_active = True
                    time.sleep(60)

            else:
                if (now.hour, now.minute, day_week) == (alarm["hour"], alarm["minute"], alarm["day"]):
                    print("Alarm triggered!")
                    alarm_on = 0
                    alarm_is_active = True
                    time.sleep(60)


        time.sleep(1)

def play_sound():
    while True:
        global alarm_is_active, alarm_on

        # gets the location of the folder we are inn
        file_dir = os.path.dirname(__file__)
        print("file dir =", file_dir)
        print("------------")

        #the sound file we are trying to play
        sound_file = "police_s.wav"
        print("sound file is", sound_file)
        print("------------")

        # this is where we define evryting together
        sound_path = os.path.join(file_dir, sound_file)
        print("sound path is", sound_path)
        print("------------")

        #this loads the file and readies it to be played
        alarm_sound = pygame.mixer.Sound(sound_path)
        print("alarm sound is", alarm_sound)
        print("------------")

        if alarm_is_active and alarm_on == 0:
            print("playing the sound file")
            alarm_sound.play()
            time.sleep(4)
            
        time.sleep(1)


def play_snake_game():
    global alarm_on, alarm_is_active, Game
    green, red, black = (0, 255, 0), (255, 0, 0), (0, 0, 0)

    try:
        snake = [(3, 3)]
        food = (random.randint(0, 7), random.randint(0, 7))
        direction = 'right'
        apples_eaten = 0

        def draw():
            sense.clear()
            for segment in snake:
                sense.set_pixel(segment[0], segment[1], green)
            sense.set_pixel(food[0], food[1], red)

        def move_snake():
            global alarm_on
            nonlocal food, apples_eaten
            head_x, head_y = snake[0]
            if direction == 'up': head_y -= 1
            elif direction == 'down': head_y += 1
            elif direction == 'left': head_x -= 1
            elif direction == 'right': head_x += 1

            if head_x < 0 or head_x > 7 or head_y < 0 or head_y > 7 or (head_x, head_y) in snake:
                alarm_on = 0
                return False  # Game over

            new_head = (head_x, head_y)
            snake.insert(0, new_head)

            if new_head == food:
                apples_eaten += 1
                food = (random.randint(0, 7), random.randint(0, 7))
            else:
                snake.pop()

            return True

        def get_tilt_direction():
            nonlocal direction
            acceleration = sense.get_accelerometer_raw()
            x, y = acceleration['x'], acceleration['y']
            if abs(x) > abs(y):
                if x < -0.3: direction = 'left'
                elif x > 0.3: direction = 'right'
            else:
                if y < -0.3: direction = 'up'
                elif y > 0.3: direction = 'down'

        while apples_eaten < Game:
            get_tilt_direction()
            if not move_snake():
                sense.show_message("Try Again!", text_colour=red)
                #alarm_on = 0 # Game failed
                break
            draw()
            time.sleep(0.3)

        if apples_eaten >= Game:
            sense.show_message("You Win!", text_colour=green)
            alarm_on = 2  # Game completed
            alarm_is_active = False  # Turn off the alarm

    except Exception as e:
        print(f"Error in play_snake_game: {e.with_traceback()}")
        sense.show_message("Error!", text_colour=red)
        alarm_on = 2  # Ensure the alarm is turned off even if an error occurs
        alarm_is_active = False


def display_pattern(pattern, name):
    global current_display
    sense.set_pixels(pattern)
    current_display = name

def joystick_handler(pushed: Joystick):
    print(f"pushed: {pushed}")
    global screen
    global on
    global offfalse
    global offselect
    global current_display
    global on_off
    global alarm_on
    global alarm_is_active

    if pushed == Joystick.LEFT:
        sense.clear()
        screen = 1
        #print("Moved left")
        #if on_off == 1:
        #    display_pattern(on, "on")
        #elif on_off == 0:
        #    display_pattern(offselect, "off")

    elif pushed == Joystick.RIGHT:
        sense.clear()
        screen = 0  # Switch to status display mode
        #print("Moved right → Showing ON/OFF status")
        if on_off == 1:
            display_pattern(on, "on")
        elif on_off == 0:
            display_pattern(offselect, "off")

    elif pushed == Joystick.MIDDLE:  # Joystick pressed down
        if alarm_is_active and alarm_on == 0:  # Start the game only if the alarm is active
            #print("Joystick pressed down - starting Snake game")
            alarm_on = 1  # Start the game

    if screen == 0:
        if pushed == Joystick.UP or pushed == Joystick.DOWN:
            if current_display == "on":
                display_pattern(offfalse, "off")
                #print("Preparing to turn OFF")
            else:
                display_pattern(on, "on")
                #print("Preparing to turn ON")

        elif pushed == Joystick.MIDDLE:
            if current_display == "on":
                sense.clear()
                #print("on")
                screen = 1
                on_off = 1
                sleep(1)
            else:
                screen = 1
                display_pattern(offselect, "off")
                sleep(1)
                display_pattern(offfalse, "off")
                sleep(1)
                display_pattern(offselect, "off")
                sleep(1)
                display_pattern(offfalse, "off")
                sense.clear()
                #print("off")
                on_off = 0
                sleep(1)



def joystick_event(event):
    if event.action == "pressed":
        #print(current_display)
        #print(f"Joystick pressed: {event.direction}")  # Debugging
        try:
            match event.direction:
                case "left":
                    joystick_queue.put(Joystick.LEFT, block=False)
                case "right":
                    joystick_queue.put(Joystick.RIGHT, block=False)
                case "middle":
                    joystick_queue.put(Joystick.MIDDLE, block=False)
                case "up":
                    joystick_queue.put(Joystick.UP, block=False)
                case "down":
                    joystick_queue.put(Joystick.DOWN, block=False)
        except Full:
            pass #vi ignorerer inputet


def display():
    while True:
        global on_off
        global screen
        global on
        global offfalse
        global offselect
        global current_display
        global alarm_on
        global alarm_is_active
        global Game

        sense.stick.direction_any = joystick_event

        #print("Current display is", current_display)
        #print(joystick_queue.qsize())

        try:
            pushed = joystick_queue.get(block=False)
            joystick_handler(pushed)
        except Empty:
            pass


        if screen == 1:
            if on_off == 1:
                now = datetime.datetime.now()
                #print("VIKTIG!!!", alarm_is_active)
                if alarm_is_active:
                    print("Alarm is on")
                    text_color = (255, 0, 0)
                    sense.show_message("ALARM!", scroll_speed=0.08, text_colour=text_color)
                    sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)

                    if alarm_on == 1:  # Start the game if joystick is pressed
                        try:
                            play_snake_game()

                        except Exception as e:
                            print(f"Error in play_snake_game: {e.with_traceback()}")
                else:
                    text_color = (255, 255, 255)
                    sense.show_message("time", scroll_speed=0.08)
                    sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)

                    weather = get_weather()
                    if weather_onoff and not alarm_is_active:
                        sense.show_message("temperature", scroll_speed=0.08)
                        sense.show_message(ttemp, text_colour=(0, 255, 0), scroll_speed=0.1)

                    if temp_onoff and not alarm_is_active:
                        sense.show_message("weather", scroll_speed=0.08)
                        sense.show_message(curweather, text_colour=(0, 0, 255), scroll_speed=0.1)

            else:
                #print("Program off")
                
                if alarm_is_active:
                    print("Alarm is on")
                    text_color = (255, 0, 0)
                    sense.show_message("ALARM!", scroll_speed=0.08, text_colour=text_color)
                    sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)

                    if alarm_on == 1:  # Start the game if joystick is pressed
                        try:
                            play_snake_game()
                            
                        except Exception as e:
                            print(f"Error in play_snake_game: {e.with_traceback()}")
                else:
                    sense.clear()

        time.sleep(1)

@app.route("/", methods=["GET", "POST"])
def index():
    global weather_onoff
    global temp_onoff
    global Game
    if request.method == "POST":
        if "time" in request.form:
            time_str = request.form["time"]
            hour, minute = map(int, time_str.split(":"))

            selected_days = request.form.getlist("day")
            for day in selected_days:
                new_alarm = {"hour": hour, "minute": minute, "day": int(day)}
                if new_alarm not in alarms:
                    alarms.append(new_alarm)

        elif "remove_index" in request.form:
            idx = int(request.form["remove_index"])
            if 0 <= idx < len(alarms):
                alarms.pop(idx)

        if "weather" in request.form:
            #print(f"weather.request {request.form['weather']}")
            #weather_onoff = bool(int(request.form['weather']))
            if weather_onoff == True:
                weather_onoff = False
            else:
                weather_onoff = True
            #print(weather_onoff)
            

        if "temp" in request.form:
            
            if temp_onoff == True:
                temp_onoff = False
            else:
                temp_onoff = True
            #print(temp_onoff)

        if "number_input" in request.form:
            if int(request.form["number_input"]) <= 60:
                Game = int(request.form["number_input"])
                print(f"User entered number: {Game}")  

            else:
                print(f"User entered number: {Game}")  
                Game = 60
                print(f"new score is: {Game}")  

    alarm_list = []
    day_name={0:"Monday", 1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday", 6:"Sunday"}
    for i, a in enumerate(alarms):
        alarm_list.append(
            f"""
            {day_name[a['day']]} - {a['hour']}:{a['minute']:02d}
            <form method="POST" style="display:inline;">
                <input type="hidden" name="remove_index" value="{i}">
                <button type="submit">Remove</button>
            </form>
             <br>
        """
        )
    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-size: 1.2em;
            }}
        </style>
    </head>
    <body>
        <h1>Alarm Clock</h1>
        <form method="POST">
            <label for="time">Set Alarm:</label>
            <input type="time" name="time" required>
            <p> </p>
            <input type="checkbox" name="day" value="0"> Monday<br>
            <input type="checkbox" name="day" value="1"> Tuesday<br>
            <input type="checkbox" name="day" value="2"> Wednesday<br>
            <input type="checkbox" name="day" value="3"> Thursday<br>
            <input type="checkbox" name="day" value="4"> Friday<br>
            <input type="checkbox" name="day" value="5"> Saturday<br>
            <input type="checkbox" name="day" value="6"> Sunday<br>
            <button type="submit">Add Alarm</button>
        </form>
        <h2>Current Alarms</h2>
        {''.join(alarm_list)}
    <p> </p>
    <h1>List of funktions u can turn on or off</h1>
    <form id="weatherForm" method="POST">
        {"<label for='weather'>Weather updates On:</label>" if weather_onoff else "<label for='weather'>Weather updates OFF:</label>"}
        <input type="checkbox" name="weather" value="1" onchange="submitFormW()"><br>
        <p> </p>
    </form>
    
    <form id="TempForm" method="POST">
        {"<label for='temp'>Temprature updates On:</label>" if temp_onoff else "<label for='temp'>Temprature updates OFF:</label>"}
        <input type="checkbox" name="temp" value="1" onchange="submitFormT()"><br>
        <p> </p>
    </form>

    <form id="gameamount" method="POST">
        <label for="number_input">Enter how many apples u have to eat to beat the game:</label>
        <input type=="number" name="number_input" requierd>
        <p> </p>
    </form>

    <p>Thank you for using somali electric</p>
    <script>

    function submitFormW() {{
        document.getElementById('weatherForm').submit();
    }}
    
    function submitFormT() {{
    document.getElementById('TempForm').submit();
    }}

    function submitFormG() {{
    document.getElementById('gameamount').submit();
    }}

    </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    threading.Thread(target=check_alarms, daemon=True).start()
    threading.Thread(target=display, daemon=True).start()
    threading.Thread(target=play_sound, daemon=True).start()
    app.run(host="0.0.0.0", port=2000)
