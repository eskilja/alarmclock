from sense_hat import SenseHat
import time
import random

sense = SenseHat()
sense.clear()

green = (0, 255, 0)
red = (255, 0, 0)
black = (0, 0, 0)

snake = [(3, 3)]
food = (random.randint(0, 7), random.randint(0, 7))
direction = 'right'

def draw():
    sense.clear()
    for segment in snake:
        sense.set_pixel(segment[0], segment[1], green)
    sense.set_pixel(food[0], food[1], red)

def move_snake():
    global food
    head_x, head_y = snake[0]
    if direction == 'up':
        head_y -= 1
    elif direction == 'down':
        head_y += 1
    elif direction == 'left':
        head_x -= 1
    elif direction == 'right':
        head_x += 1
    
    new_head = (head_x % 8, head_y % 8)
    
    if new_head in snake:  # Game over if snake runs into itself
        sense.show_message("Game Over!", text_colour=red)
        sense.clear()
        return False
    
    snake.insert(0, new_head)
    
    if new_head == food:
        food = (random.randint(0, 7), random.randint(0, 7))
    else:
        snake.pop()
    
    return True

def get_tilt_direction():
    global direction
    acceleration = sense.get_accelerometer_raw()
    x = acceleration['x']
    y = acceleration['y']
    
    if abs(x) > abs(y):  # Tilt left/right
        if x < -0.3:
            direction = 'left'
        elif x > 0.3:
            direction = 'right'
    else:  # Tilt up/down
        if y < -0.3:
            direction = 'up'
        elif y > 0.3:
            direction = 'down'

while True:
    get_tilt_direction()
    if not move_snake():
        break
    draw()
    time.sleep(0.3)
