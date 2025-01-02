from flask import Flask, request
import threading
import time
import datetime
import winsound

app = Flask(__name__)
alarms = []


def check_alarms():
    while True:
        now = datetime.datetime.now()
        for alarm in alarms:
            if (now.hour, now.minute) == (alarm["hour"], alarm["minute"]):
                winsound.Beep(440, 500)
                print("Alarm triggered!")

            # ...check if current time matches alarm time and day...
            # ...trigger alarm if matched...
        time.sleep(1)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "time" in request.form:
            time_str = request.form["time"]
            hour, minute = map(int, time_str.split(":"))
            alarms.append({"hour": hour, "minute": minute})
        elif "remove_index" in request.form:
            idx = int(request.form["remove_index"])
            if 0 <= idx < len(alarms):
                alarms.pop(idx)
    alarm_list = []
    for i, a in enumerate(alarms):
        alarm_list.append(
            f"""
            {a['hour']}:{a['minute']:02d}
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
            <button type="submit">Add Alarm</button>
        </form>
        <h2>Current Alarms</h2>
        {''.join(alarm_list)}
    </body>
    </html>
    """


if __name__ == "__main__":
    threading.Thread(target=check_alarms, daemon=True).start()
    app.run(host="0.0.0.0", port=80)