#helpers
import requests
from auth import *  
knx_start="http://10.84.82.239:50001/knx/"

# -------------------------------- COMMANDS --------------------------------
def shutterDown(shutters):
	for shutter in shutters:
		r = requests.post(knx_start+shutter+"/down", json=authStr)

def shutterUp(shutters):
	for shutter in shutters:
		r = requests.post(knx_start+shutter+"/up", json=authStr)

def shutterStop(shutters):
	for shutter in shutters:
		r = requests.post(knx_start+shutter+"/stop", json=authStr)

def shutterStepUp(shutters):
	for shutter in shutters:
		r = requests.post(knx_start+shutter+"/stepup", json=authStr)
	
def shutterStepDown(shutters):
	for shutter in shutters:
		r = requests.post(knx_start+shutter+"/stepdown", json=authStr)

def cmd_player_play():
    pass

def cmd_player_pause():
    pass

def cmd_player_next():
    pass

def cmd_player_prev():
    pass

def cmd_player_volume_up():
    pass

def cmd_player_volume_down():
    pass

# -------------------------------- BUTTONS --------------------------------
	
#create a list of button addresses
btns = dict()
btns["80:e4:da:71:ed:dc"]= ["g"] #80:e4:da:71:ed:dc grün
btns["80:e4:da:71:d6:be"]= ["s"] #80:e4:da:71:d6:be schwarz
btns["80:e4:da:71:da:3d"]= ["b"] #80:e4:da:71:da:3d blue

#comand pattern and respective function
# button triggers:
# .  = short click
# :  = double click
# 1  = 1s click
# 2  = 2s click
# 3  = 3s click
# 4  = 4s click

#key:   your desired pattern
#value: a list of tuples, each entry starts with a funciotn (see above), followed by attributes (1-n)
#expample 1: [(shutterDown,["5_2C19/south"])]  --> shutterDown("5_2C19/south")
#expample 2: [(shutterStepUp,["5_2C19/south","5_2C19/west"]),(shutterStepUp,["5_2C19/south","5_2C19/west"])]  
#            --> shutterStepUp(["5_2C19/south","5_2C19/west"]) ; shutterStepUp(["5_2C19/south","5_2C19/west"]) 

commands = dict()
#button black
commands["s.."]=[(shutterDown,["5_2C19/south"])]
commands["s.:"]=[(shutterUp,["5_2C19/south"])]
commands["s:."]=[(shutterStepDown,["5_2C19/south"])]
commands["s::"]=[(shutterStepUp,["5_2C19/south"])]
commands["s1"]=[(shutterStop,["5_2C19/south","5_2C19/west"])]
#button green
commands["g1"]=[(shutterDown,["5_2C19/south","5_2C19/west"])]
commands["g2"]=[(shutterUp,["5_2C19/south","5_2C19/west"])]
#button blue
commands["b."]=[(shutterStepDown,["5_2C19/south","5_2C19/west"])]
commands["b1"]=[(shutterStepUp,["5_2C19/south","5_2C19/west"])]


#init a "queue" for each button
btn_queue = dict()
btn_clickTime = dict()
btn_lastClick = dict()

#add btns to dicts
for btn in btns.keys():
	btn_queue[btn]=list()
	btn_clickTime[btn]=0
	btn_lastClick[btn]=0

#config parameters flic service (everything in milliseconds)
queue_timeout = 5000
doubleClickTimeout = 300
click_short_max = 500
click_1s_max = 1500
click_2s_max = 2500
click_3s_max = 3500
#no max for click_4s as its the default > 3s
