from flask import Flask, request
import threading
import time
import datetime
from sense_hat import SenseHat
#import winsound

sense = SenseHat()

app = Flask(__name__)
alarms = []
alarm_is_active = False

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
        
        sense.show_message("time", scroll_speed=0.08)
        sense.show_message(f"{now.hour}:{now.minute:02d}", text_colour=text_color, scroll_speed=0.1)
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
                alarms.append({"hour": hour, "minute": minute, "day": day})

        elif "remove_index" in request.form:
            idx = int(request.form["remove_index"])
            if 0 <= idx < len(alarms):
                alarms.pop(idx)
    alarm_list = []
    for i, a in enumerate(alarms):
        alarm_list.append(
            f"""
            {a['day']} - {a['hour']}:{a['minute']:02d}
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
        <p>  </p>
        <p>days equivelent in numbers</p>
        <p> </p>
        <p>0 = Monday</p>
        <p>1 = Tuesday</p>
        <p>2 = Wednesday</p>
        <p>3 = Thursday</p>
        <p>4 = Friday</p>
        <p>5 = Saturday</p>
        <p>6 = Sunday</p>
        <p> </p>
        <h2>Current Alarms</h2>
        {''.join(alarm_list)}
    <p></p>
    <p>Thank you for using somali electric</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    threading.Thread(target=check_alarms, daemon=True).start()
    threading.Thread(target=display, daemon=True).start()
    app.run(host="0.0.0.0", port=2001)
