#!/usr/bin/env python3

#imports
import fliclib
import time
import threading
c = threading.Condition()

# our imports
from config import *  

client = fliclib.FlicClient("localhost")
current_milli_time = lambda: int(round(time.time() * 1000))



def queueHandle(bd_addr, currTime, clickType):
	"""
	1) Check if the current click still belongs to the queue or if we have to flush it.
	2) Check if we have a valid command
	3) If so execute and flush.
	"""
	global btn_lastClick
	global btn_queue
	tmp_comm = ""
	
	#clear list if needed
	if(currTime - btn_lastClick[bd_addr] > queue_timeout): btn_queue[bd_addr]=btns[bd_addr][:]
	
	#check for doubleclick (:)
	if clickType == "." and currTime - btn_lastClick[bd_addr] < doubleClickTimeout:
		clickType = ":"
		btn_queue[bd_addr][-1]=clickType
	else:
		#append click
		btn_queue[bd_addr].append(clickType)
	
	#set lastClickTime
	btn_lastClick[bd_addr]=currTime
	
	#print current command state
	tmp_comm=''.join(btn_queue[bd_addr])
	print(tmp_comm)
	
	

def clickkHandle(bd_addr, click_type):
	"""
	Handle clicks. Decide type of click and pass it to queueHandle()
	"""
	currTime=current_milli_time()
	global btn_clickTime
	totTime = 0
	clickType = ""
	
	#if button:down save time in milli and exit
	if(click_type == "ClickType.ButtonDown"):
		btn_clickTime[bd_addr]=currTime
		return
		
	#else button:up - calc total time of click
	totTime=currTime-btn_clickTime[bd_addr]
	
	#the fastest valid click wins
	clickType="4"
	if(totTime < click_3s_max):	clickType="3"
	if(totTime < click_2s_max):	clickType="2"
	if(totTime < click_1s_max):	clickType="1"
	if(totTime < click_short_max):	clickType="."
	#we handle double clicks later
	
	#call queueHandle
	queueHandle(bd_addr, currTime, clickType)
	
	
def got_button(bd_addr):
	cc = fliclib.ButtonConnectionChannel(bd_addr)
	cc.on_button_up_or_down = \
		lambda channel, click_type, was_queued, time_diff: \
			clickkHandle(channel.bd_addr,str(click_type))
			
	cc.on_connection_status_changed = \
		lambda channel, connection_status, disconnect_reason: \
			print(channel.bd_addr + " " + str(connection_status) + (" " + str(disconnect_reason) if connection_status == fliclib.ConnectionStatus.Disconnected else ""))
	client.add_connection_channel(cc)

	
	
def got_info(items):
	print(items)
	for bd_addr in items["bd_addr_of_verified_buttons"]:
		got_button(bd_addr)



			
class Thread_A(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		global client
		client.get_info(got_info)
		client.on_new_verified_button = got_button
		client.handle_events()

		
class Thread_B(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		global btn_queue
		while True:
			time.sleep(0.1)
			currTime=current_milli_time()
			#check if command exists
			for bd_addr in btns.keys():
				tmp_comm=''.join(btn_queue[bd_addr])
				if tmp_comm in commands and currTime - btn_lastClick[bd_addr] > doubleClickTimeout: 
					print("Exec: ",tmp_comm)
					for command in commands[tmp_comm]:
						command[0](*command[1:])
						btn_queue[bd_addr]=btns[bd_addr][:]


#create two threads
a = Thread_A("ExecuteQueue")
b = Thread_B("WriteQueue")

b.start()
a.start()

a.join()
b.join()







