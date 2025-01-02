from flask import Flask, request, redirect, url_for
import threading
import time
import datetime
import requests

try:
    from sense_hat import SenseHat
    sense = SenseHat()
except:
    sense = None

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to use sessions

alarms = []
alarm_is_active = False
set_temprature = 0  # Global variable to store the temperature setting (1 for on, 0 for off)

# Replace with your OpenWeatherMap API key
API_KEY = '9fe7bc1bc1f94de3538a3338cfb6087a'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
city = "Oslo"  # Replace with the city you want

# Function to get weather data
def get_weather():
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
            description = data['weather'][0]['description']
            return f"{temp}°C"
        else:
            return "Weather data unavailable"
    except Exception as e:
        return f"Error: {str(e)}"

def check_alarms():
    global alarm_is_active
    while True:
        now = datetime.datetime.now()
        day_week = now.weekday()
        alarm_is_active = False
        for alarm in alarms:
            if (now.hour, now.minute, day_week) == (alarm["hour"], alarm["minute"], alarm["day"]):
                print("Alarm triggered!")
                alarm_is_active = True
        time.sleep(1)

def display():
    global set_temprature
    while True:
        now = datetime.datetime.now()
        if alarm_is_active:
            text_color = (255, 0, 0)
        else:
            text_color = (255, 255, 255)

        if sense:
            sense.show_message("time", scroll_speed=0.08)
            sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)

            # Check if temperature display is enabled
            if set_temprature == 1:
                weather = get_weather()
                sense.show_message("Temperature", scroll_speed=0.08)
                sense.show_message(weather, text_colour=(0, 255, 0), scroll_speed=0.1)
        time.sleep(1)

@app.route("/", methods=["GET", "POST"])
def index():
    global set_temprature
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

        # Manage temperature checkbox state
        if "temprature" in request.form:  # If the checkbox is checked
            set_temprature = 1
        else:
            set_temprature = 0  # If the checkbox is not checked

        return redirect(url_for('index'))  # Redirect to avoid re-posting form on refresh

    # Display alarms
    alarm_list = []
    day_name = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
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

    # Retrieve temperature setting from global variable
    temp_checked = "checked" if set_temprature == 1 else ""

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

        <h3>Temperature</h3>
        <label for="temprature">Temperature on/off:</label>
        <input type="checkbox" name="temprature" value="1" {temp_checked}><br>
        <button type="submit">Commit</button>
    <p> </p>
    <p>Thank you for using Somali Electric</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    threading.Thread(target=check_alarms, daemon=True).start()
    threading.Thread(target=display, daemon=True).start()
    app.run(host="0.0.0.0", port=2001)
