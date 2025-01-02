from sense_hat import SenseHat
import datetime
import time
from datetime import timedelta

sense = SenseHat()

red =(255,0,0)
blue=(0,0,255)
days = []

while True:
    print("do u want to set an alarm? (y/n)")
    alarm = input().lower()
    if alarm =="y":
        print("what days in the week do u want the alarm to go off")
        print(" ")
        print("use this format pick a number and then press enter and continue this untill u are done")
        print(" ") 
        print("0:monday")
        print("1:tuesday")
        print("2:wednesday")
        print("3:thursday")
        print("4:friday")
        print("5:saturday")
        print("6:sunday")
        print("7:weekdays")
        print("8:weekends")
        print("9:all")
        print(" ")
        print("when u are done adding days press (n)")
        #the easiest way to add days to the list
        while True:
            day=int(input())
            if day == 7:
                days.append(0)
                days.append(1)
                days.append(2)
                days.append(3)
                days.append(4)
                break

            elif day == 8:
                days.append(5)
                days.append(6)
                break

            elif day ==9:
                days.append(0)
                days.append(1)
                days.append(2)
                days.append(3)
                days.append(4)
                days.append(5)
                days.append(6)
        
            elif day == "n":
                break
    
            else:
                days.append(day)

        print(" ")
        alarmh = int(input("What hour do you want to be woken up? "))
        alarmm = int(input("What minute do you want to be woken up? "))
        break  # Exit the loop when valid input is provided
    elif alarm =="n":
        #just so that no alarm will be sett
        alarmh = None  
        alarmm = None
        break
    else:
        print("invalid input")


while True:
    #finds the current time
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    dateday=time.localtime().tm_mday
    datemonth=time.localtime().tm_mon
    dateyear=time.localtime().tm_year
    dayweek=time.localtime().tm_wday

    #makes the two variables into one so that we dont need three sense.show_message
    x= f"{hour}:{minute}"
    y= f"{dateday}/{datemonth}/{dateyear}"

    #displays the current date and time
    sense.show_message("time", scroll_speed=0.08)
    sense.show_message(x, text_colour=red, scroll_speed=0.1)
    sense.show_message("date", scroll_speed=0.08)
    sense.show_message(y, text_colour=blue, scroll_speed=0.1)

    #alarm goes of if its the correct time and day
    if alarm is not "n":
        if hour == alarmh and minute == alarmm and dayweek in days:
            sense.show_message("alarm went off")

    #idk just a small delay
    time.sleep(2)


#use while true to infinetly loop the file
#the website file is inside
#inside var/www/html u find the website file
#vim the file name to edit 
# :w to save
# :x to save and exit