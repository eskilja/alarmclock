from flask import Flask, request
from time import sleep
import threading
import time
import datetime
import requests
import random

#kanskje legg til sånn at klokken vekker deg 10 min før om det er kaldt ute
#angående hvor mye du snur Rpi så har det en effekt på spillet

#just so that it works on computers as well
try:
    from sense_hat import SenseHat
    sense = SenseHat()
except:
    sense = None

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
alarm_on =0
Game = 1

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
        #print(now)
        day_week = now.weekday()
        weathercheck = get_weather()
        #print(day_week)
        #print(alarms) 
        #it works but for some reason they still dont work together
        alarm_is_active=False
        print("ttemp", ttemp)
        if ttemp == "error fetching weather data" or ttemp == "Weather data unavalible":
            mintemp = 0
            print("mintep (ttemp didnt work)", mintemp)

        else:
            try:
                mintemp = float(ttemp)  # Convert ttemp to a float
            except ValueError:
                mintemp = 0  # Handle invalid numeric values by assigning a default
                print("it didnt work :(")
                print("mintemp", mintemp)
                print("again ttemp", ttemp)

        for alarm in alarms:
            if mintemp <= 0:
                print("alarmen er satt på. dag", alarm["hour"], "minut", alarm["minute"], "dag",alarm["day"])
                #atempting to do some regulering by minusing time depending on how cold it is
                
                i = 0
                while mintemp <=1:
                    i = i+2
                    mintemp = mintemp+1
                if (now.hour, now.minute, day_week) == (alarm["hour"], alarm["minute"]-i, alarm["day"]):
                    print("Alarm triggered!")
                    alarm_is_active = True   
                    alarm_on = 0
            else:
                if (now.hour, now.minute, day_week) == (alarm["hour"], alarm["minute"], alarm["day"]):
                    #winsound.Beep(440, 500)
                    print("Alarm triggered!")
                    alarm_is_active = True
                    alarm_on = 0   

            # ...check if current time matches alarm time and day...
            # ...trigger alarm if matched...
        time.sleep(1)

def play_snake_game():
    global alarm_on, Game
    green, red, black = (0, 255, 0), (255, 0, 0), (0, 0, 0)

    while alarm_on == 1:
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
            nonlocal food, apples_eaten
            head_x, head_y = snake[0]
            if direction == 'up': head_y -= 1
            elif direction == 'down': head_y += 1
            elif direction == 'left': head_x -= 1
            elif direction == 'right': head_x += 1

            if head_x < 0 or head_x > 7 or head_y < 0 or head_y > 7 or (head_x, head_y) in snake:
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
                break
            draw()
            time.sleep(0.3)

        if apples_eaten >= Game:
            sense.show_message("You Win!", text_colour=green)
            alarm_on = 2  # Stop alarm

def display_pattern(pattern, name):
    global current_display
    sense.set_pixels(pattern)
    current_display = name

def joystick_event(event):
        global screen
        global on
        global offfalse
        global offselect
        global current_display
        global on_off
        global alarm_on

        if event.action == "pressed":
            print(current_display)
            if event.direction == "left":
                sense.clear()
                screen =1
                print("moved left")
                if on_off == 1:
                    display_pattern(on, "on")
                elif on_off == 0:
                    display_pattern(offselect, "off")


            elif event.direction == "right":
                sense.clear()
                screen = 0  # Switch to status display mode
                print("Moved right → Showing ON/OFF status")
                if on_off == 1:
                    display_pattern(on, "on")
                elif on_off == 0:
                    display_pattern(offselect, "off")
            elif event.direction == "middle":
                if alarm_is_active:
                    alarm_on = 1

            if screen == 0:
                if event.direction == "up" or event.direction == "down":
                    # Prepare to toggle ON/OFF
                    if current_display == "on":
                        display_pattern(offfalse, "off")
                        print("Preparing to turn OFF")
                    else:
                        display_pattern(on, "on")
                        print("Preparing to turn ON")

                elif event.direction == "middle":
                    if current_display == "on":
                        sense.clear()
                        print("on")
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
                        print("off")
                        sense.clear()
                        print("off")
                        on_off = 0
                        sleep(1)



def display():
    while True:
        global on_off
        global screen
        global on
        global offfalse
        global offselect
        global current_display
        global alarm_on
        global Game
        
        sense.stick.direction_any = joystick_event

        print("current display is", current_display)

        if screen ==1:
            if on_off == 1:
                #print("program on")
                now = datetime.datetime.now()
                if alarm_is_active:
                    print("alarm is on")
                    text_color=(255,0,0)
                    if alarm_on == 1:
                        while alarm_on != 2:
                            play_snake_game()
                else:
                    text_color=(255,255,255)
            
                if sense:
                    sense.show_message("time", scroll_speed=0.08)
                    sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)

                    # Display weather if display weather is true
                    weather = get_weather()
                    #print(ttemp)
                    #print(curweather)
                    if weather_onoff == True and alarm_is_active != True:
                        sense.show_message("temprature", scroll_speed=0.08)
                        sense.show_message(ttemp, text_colour=(0, 255, 0), scroll_speed=0.1)

                    if temp_onoff == True and alarm_is_active != True:
                        sense.show_message("weather", scroll_speed=0.08)
                        sense.show_message(curweather, text_colour=(0,0,255), scroll_speed=0.1)

                #if weather_onoff == True:
                #    print("it works")
                #else:
                #    print("it doesnt work")

                #if temp_onoff == True:
                #    print("it works")
                #else:
                #    print("but why?")


                #print(alarms)
        
            else:
                print("program off")
                
                now = datetime.datetime.now()
                if alarm_is_active:
                    print("alarm is on")
                    if alarm_on == 0:
                        text_color=(255,0,0)
                        sense.show_message("time", scroll_speed=0.08)
                        sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)
                    else:
                        while alarm_on != 2:
                            play_snake_game()
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
            print(weather_onoff)
            

        if "temp" in request.form:
            
            if temp_onoff == True:
                temp_onoff = False
            else:
                temp_onoff = True
            print(temp_onoff)

        if "number_input" in request.form:
            Game = int(request.form["number_input"])
            print(f"User entered number: {Game}")  # You can process the number as needed

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
    app.run(host="0.0.0.0", port=2000)
