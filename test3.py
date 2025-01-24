from sense_hat import SenseHat
from signal import pause

# Create a SenseHat object
sense = SenseHat()

# Function to handle joystick events
def joystick_event(event):
    # Check the event type and direction
    if event.action == "pressed":  # Options: "pressed", "released", "held"
        if event.direction == "up":
            print("Joystick moved up!")
        elif event.direction == "down":
            print("Joystick moved down!")
        elif event.direction == "left":
            print("Joystick moved left!")
        elif event.direction == "right":
            print("Joystick moved right!")
        elif event.direction == "middle":
            print("Joystick pressed in the middle!")

# Set up the joystick
sense.stick.direction_any = joystick_event  # Call on any joystick action

# Keep the program running
print("Use the joystick and watch the output!")
pause()
