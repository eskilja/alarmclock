from flask import Flask, request
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

def display():
    while True:
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
        time.sleep(1)

@app.route("/", methods=["GET", "POST"])
def index():
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
            print("it work")
            weather_onoff = True
            

        if "temp" in request.form:
            print("it works")
            temp_onoff = True

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
    <label for="weather">Weather updates On/OFF:</label>
    <input type="checkbox" name="weather" value="1"><br>
    <button type="submit">Commit</button>
    <p> </p>
    <label for="temp">Temprature updates ON/OFF:</label>
    <input type="checkbox" name="temp" value="1"><br>
    <button type="submit">Commit</button>
    <p> </p>
    <p>Thank you for using somali electric</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    threading.Thread(target=check_alarms, daemon=True).start()
    threading.Thread(target=display, daemon=True).start()
    app.run(host="0.0.0.0", port=2000)
