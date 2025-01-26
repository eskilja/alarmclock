from flask import Flask, request
from time import sleep
import threading
import time
import datetime
import requests

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
on_off = 1
screen = 0

O = [0, 0, 0]       # Black (Off)
W = [255, 255, 255] # White (On)
T = [255,0,0] #Red (off is true)

# Define the "ON" pattern
on = [
    O, O, W, W, W, W, O, O,
    O, W, O, O, O, O, W, O,
    O, W, O, W, W, O, W, O,
    O, W, O, W, W, O, W, O,
    O, W, O, W, W, O, W, O,
    O, W, O, O, O, O, W, O,
    O, O, W, W, W, W, O, O,
    O, O, O, O, O, O, O, O,
]

# Define the "OFF" pattern
offselect = [
    O, T, T, T, T, O, O, O,
    O, T, O, O, O, T, O, O,
    O, T, O, O, O, T, O, O,
    O, T, T, T, T, O, O, O,
    O, T, O, O, O, T, O, O,
    O, T, O, O, O, T, O, O,
    O, T, T, T, T, O, O, O,
    O, O, O, O, O, O, O, O,
]

offfalse = [
    O, W, W, W, W, O, O, O,
    O, W, O, O, O, W, O, O,
    O, W, O, O, O, W, O, O,
    O, W, W, W, W, O, O, O,
    O, W, O, O, O, W, O, O,
    O, W, O, O, O, W, O, O,
    O, W, W, W, W, O, O, O,
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
            return curweather and ttemp
        else: 
            curweahter = "Weather data unavalible"
            ttemp = "Weather data unavalible"
            return "Weather data unavailable" and curweather and temp
    except Exception as e:
        curweather = "error fetching weather data"
        ttemp = "error fetching weather data"
        return "Error fetching weather data" and curweather and temp

def check_alarms():
    global alarm_is_active
    while True:
        now = datetime.datetime.now()
        #print(now)
        day_week = now.weekday()
        #print(day_week)
        #print(alarms) 
        #it works but for some reason they still dont work together
        alarm_is_active=False
        for alarm in alarms:
            if (now.hour, now.minute, day_week) == (alarm["hour"], alarm["minute"], alarm["day"]):
                #winsound.Beep(440, 500)
                print("Alarm triggered!")
                alarm_is_active = True   

            # ...check if current time matches alarm time and day...
            # ...trigger alarm if matched...
        time.sleep(1)

def display_pattern(pattern, name):
    global current_display
    sense.set_pixels(pattern)
    current_display = name


def display():
    while True:
        global on_off
        global screen
        global on
        global offfalse
        global offselect
        global current_display
        
        if sense.stick.direction_any == "pressed":
            if sense.stick.direction == "left":
                screen ==1
            elif sense.stick.direction == "right":
                screen == 0

        if screen == 0:
            if on_off == 1:
                display_pattern(on, "on")
            else:
                display_pattern(offselect, "off")

            if sense.stick.direction_any == "pressed":

                if sense.stick.direction == "up":
                    if current_display == "on":
                        sense.clear()
                        display_pattern(offfalse, "off")
                    else:
                        sense.clear()
                        display_pattern(on, "on")
                        
                elif sense.stick.direction == "down":
                    if current_display == "on":
                        sense.clear()
                        display_pattern(offfalse, "off")
                    else:
                        sense.clear()
                        display_pattern(on, "on")

                elif sense.stick.direction == "middle":
                    if current_display == "on":
                        on_off == 1
                    else:
                        display_pattern(offselect, "off")
                        sleep(1)
                        display_pattern(offfalse, "off")
                        sleep(1)
                        display_pattern(offselect, "off")
                        sense.clear()


        elif screen ==1:
            if on_off == 1:
                #print("program on")
                now = datetime.datetime.now()
                if alarm_is_active:
                    text_color=(255,0,0)
                else:
                    text_color=(255,255,255)
            
                if sense:
                    sense.show_message("time", scroll_speed=0.08)
                    sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)

                    # Display weather if display weather is true
                    weather = get_weather()
                    #print(ttemp)
                    #print(curweather)
                    if weather_onoff == True:
                        sense.show_message("temprature", scroll_speed=0.08)
                        sense.show_message(ttemp, text_colour=(0, 255, 0), scroll_speed=0.1)

                    if temp_onoff == True:
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

        time.sleep(1)

@app.route("/", methods=["GET", "POST"])
def index():
    global weather_onoff
    global temp_onoff
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

    <p>Thank you for using somali electric</p>
    <script>

    function submitFormW() {{
        document.getElementById('weatherForm').submit();
    }}
    
    function submitFormT() {{
    document.getElementById('TempForm').submit();
    }}

    </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    threading.Thread(target=check_alarms, daemon=True).start()
    threading.Thread(target=display, daemon=True).start()
    app.run(host="0.0.0.0", port=2000)
