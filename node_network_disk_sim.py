import simpy
import datetime
import sys
import random
import matplotlib.pyplot as plt
from collections import deque 
import matplotlib.patches as mpatches

I_O_queue_A = deque([])
I_O_queue_B = deque([])
Response_A=[None] * 1000 
Response_B=[None] * 1000
packet_ID_A = 0 											
packet_ID_B = 0										
I_O_B_to_A = 1
I_O_A_to_B = 1
internal_A = 1
internal_B = 1
disk_response_A=[]
disk_response_B=[]
disk_write_response_A = []
disk_read_response_A = []
disk_write_response_A = []
disk_write_response_B = []
disk_read_response_B = []
Network_queue_in = deque([])
Network_response = []
cache_hit_A=0
cache_hit_B=0
disk_hit_A=0
disk_hit_B=0
network_hit=0

def main():
	global I_O_A_to_B
	global I_O_B_to_A
	global internal_A
	global internal_B
	num_of_int_req= int (sys.argv[1])
	num_of_ext_req = int (sys.argv[2])
	internal_A = num_of_int_req
	internal_B = num_of_int_req
	I_O_A_to_B = I_O_B_to_A = num_of_ext_req
	print ("Num of internal_request: %d and number of external request is: %d" % (num_of_int_req, num_of_ext_req))
 	print "Calling process function server A"
        env = simpy.Environment()
	env.process(server_A(env))
	env.process(server_B(env))
	env.process(switch(env))
	print "process execution done"
        env.run(until=100)
        print "Simulation Completed"
	plot_latency_A(env)
#	plot_latency_B(env)

def server_A(env):
        global  I_O_queue_A
        global  I_O_queue_B
	global 	Response_A
	global 	Response_B
	global packet_ID_A
	global packet_ID_B
	global internal_A
	global disk_write_response_A
	global disk_response_A
	global disk_read_response_A
	global Network_queue_in
	

	disk_queue_A = deque([])
	process_A = []
	packet_ID_A = 0
	num_packets_A = 100000000
	print "Inside serverA" 
#       time_now=datetime.datetime.now().time()
#       hour=time_now.hour
	
	
	while True:
		if (num_packets_A > 0):										#IO request from A to itself
			block_size = random.randint(5,200)
			propogation_delay = random.randint(4,10)
			disk_queue_delay= random.randint(1,2)
			read_delay = random.randint(2,3)
			write_delay = random.randint(4,6)
			--num_packets_A
			start_time = env.now
			end_time = -1
			r_w = random.choice('rccccccwcccc')								#It can be cache hit or read or write
			DNode= random.choice('AAAAB')
			SNode = 'A'
			delay =0
			packet = [packet_ID_A, block_size, r_w, SNode, start_time, delay, end_time, DNode]
#			yield env.timeout(1)
			
			if (DNode=='B'):
				packet[5] = packet[5] + propogation_delay					#Network propogation delay 4 milli seconds 
				Network_queue_in.append(packet)
				print "Network Queue"
				print Network_queue_in
			else:
				packet[5] = packet[5] +	0.001							#Nodal packet processing delay .01 milli seconds
				I_O_queue_A.append(packet)
				print "System queuq at node A"
				print I_O_queue_A
#			yield env.timeout(1)
			
			try: 
				process_A = I_O_queue_A.popleft()
			except IndexError:
    				print "No Load at node A"
			else: 


				if (process_A[2]== 'c'):
                                        ++cache_hit_A

				if ((process_A[2]== 'c' ) or (process_A[6] == 1) ):
#				if (process_A[2]== 'c'  ):
					process_A[5] = process_A[5] + 0.01					#Cache hit delay of .01 mili seconds		
					if (process_A[7] =='A'):						# Checking if it is should be processed at node A or node B
						print "Node A data at node Node A... Marking it as complete"
						Response_A[process_A[0]] = process_A[5]
					else:
						print"Node B data at node A... Moving to network queue adding propogation delay"
						process_A[5] = process_A[5] + propogation_delay			#Network propogation delay 4 milli seconds 
						process_A[6]=1
                                		Network_queue_in.append(process_A)
					
	
				else:
					print "Not a cache hit, moving to disk queue"
					process_A[5] = process_A[5] + disk_queue_delay 
					++disk_hit_A
					disk_queue_A.append(process_A)	
					print "Disk queue at node Node A"
					print disk_queue_A
#			yield env.timeout(1)

			try: 
				disk_A = disk_queue_A.popleft()
                        except IndexError:
                                print "No Load at node A disk queue"
                        else:   

				if(disk_A[2] == 'r'):
					print "Read request at Node A disk"
					total_read_delay = disk_queue_delay + read_delay
					disk_A[5] = disk_A[5] + read_delay 	
					disk_read_response_A.append(read_delay)
					disk_response_A.append(total_read_delay)
				else:
					print "Write request at Node A disk"
					disk_A[5] = disk_A[5] + write_delay 
					total_write_delay = disk_queue_delay + write_delay
					disk_write_response_A.append(write_delay)
					disk_response_A.append(total_write_delay)
				if (disk_A[7] == 'A'):
					print "Local request at node A disk, move it status complete state"
					Response_A[disk_A[0]]= disk_A[5]
				else:
					print "Remote request at node A disk, moving it to network switch queue"
					Network_queue_in.append(disk_A)
		packet_ID_A = packet_ID_A+1
		yield env.timeout(1)                   
			


def server_B(env):
        global  I_O_queue_A
        global  I_O_queue_B
        global  Response_A
        global  Response_B
        global packet_ID_A
        global packet_ID_B
        global internal_A
        global disk_write_response_A
        global disk_response_A
        global disk_read_response_A
        global Network_queue_in

        disk_queue_B = deque([])
        process_B = []
        packet_ID_B = 0
        num_packets_B = 1000000000
        print "Inside serverB"
#       time_now=datetime.datetime.now().time()
#       hour=time_now.hour


        while True:
                if (num_packets_B > 0):                                                                         #IO request from B to itself
                        --num_packets_B
			block_size = random.randint(5,2000)
			propogation_delay = random.randint(6,10)
			disk_queue_delay= random.randint(2,4)
			read_delay = random.randint(4,6)
			write_delay = random.randint(6,10)
                        start_time = env.now
                        end_time = -1
                        r_w = random.choice('rcw')                                                             #It can be cache hit or read or write
                        DNode= random.choice('ABB')
                        SNode = 'B'
			delay =0
                        packet = [packet_ID_B, block_size, r_w, SNode, start_time, delay, end_time, DNode]
#                        yield env.timeout(1)

                        if (DNode=='A'):
                                packet[5] = packet[5] + propogation_delay                                       #Network propogation delay 4 milli seconds 
                                Network_queue_in.append(packet)
                                print "Network Queue:"
                                print Network_queue_in
                        else:   
                                packet[5] = packet[5] + 0.01                                                   #Nodal packet processing delay .01 milli seconds
                                I_O_queue_B.append(packet)
                                print "System queuq at node B"
                                print I_O_queue_B
#                       yield env.timeout(1)
	
	
                        try:
                                process_B = I_O_queue_B.popleft()
                        except IndexError:
                                print "No Load at node B"
                        else:	
				if (process_B[2]== 'c'):
					++cache_hit_B

				if ((process_B[2]== 'c' ) or (process_B[6] == 1) ):
					process_B[5] = process_B[5] + 0.01					#Cache hit delay of .01 mili seconds		
					if (process_B[7] =='B'):						# Checking if it is should be processed at node A or node B
						print "Node B data at node Node B... Marking it as complete"
						Response_B[process_B[0]] = process_B[5]
					else:
						print"Node A data at node B... Moving to network queue adding propogation delay"
						process_B[5] = process_B[5] + propogation_delay			#Network propogation delay 4 milli seconds 
						process_B[6]=1
                                		Network_queue_in.append(process_B)
					
				
                                else:
                                        print "Not a cache hit or already processed packet, moving to disk queue"
                                        process_B[5] = process_B[5] + disk_queue_delay
					++disk_hit_B
                                        disk_queue_B.append(process_B)
                                        print "Disk queue at node Node B:"
                                        print disk_queue_B
#                        yield env.timeout(1)

                        try:
                                disk_B = disk_queue_B.popleft()
                        except IndexError:
                                print "No Load at node B disk queue"
                        else:

                                if(disk_B[2] == 'r'):
                                        print "Read request at Node B disk"
					total_read_delay = disk_queue_delay + read_delay
                                        disk_B[5] = disk_B[5] + read_delay
                                        disk_read_response_B.append(read_delay)
					disk_response_B.append(total_read_delay)
                                else:
                                        print "Write request at Node A disk"
					total_write_delay = disk_queue_delay + write_delay
                                        disk_B[5] = disk_B[5] + write_delay
                                        disk_write_response_B.append(write_delay)
                                        disk_response_B.append(total_write_delay)
                                if (disk_B[7] == 'B'):
                                        print "Local request at node B disk, move it status complete state"
                                        Response_B[disk_B[0]]= disk_B[5]
                                else:
                                        print "Remote request at node B disk, moving it to network switch queue"
                                        Network_queue_in.append(disk_B)
		
		packet_ID_B=packet_ID_B+1
		yield env.timeout(1)


def switch(env):
	global Network_queue_in
	global  I_O_queue_A
        global  I_O_queue_B
 	global Network_response
	global network_hit
	
	while True:
		print "Inside SWITCH"
		processing_delay = random.randint(1,3)
		transmission_delay = random.randint(1,2)
		queing_delay = random.randint(1,4)
		total_switch_delay=processing_delay + transmission_delay + queing_delay
		++network_hit
		if (len(Network_queue_in) >10):										#Dropping packets if queue is more than 1000 
			drop = Network_queue_in.popleft()
			print "Dropped packet:", drop

		try:
			pac = Network_queue_in.popleft()
		except IndexError:
			print "No load at the switch"
		else:
			print "Processing packet at switch", pac
			pac[5] = pac[5] +processing_delay + transmission_delay + queing_delay
			if (pac[7] == 'A'):
				Network_response.append(total_switch_delay)
				I_O_queue_A.append(pac)
				print "Moving packet from network switch to node A"
			else:
				I_O_queue_B.append(pac)
				Network_response.append(total_switch_delay)
				print "Moving packet from network switch to node B"
		yield env.timeout(4)
				
					

#
#
#			packet_ID_A = packet_ID_A+1
#			print "Testing123"
#			print packet_ID_A
#		if (I_O_A_to_B > 0):										#If there any IO request from A to B 
#			--I_O_A_to_B
#			start_time = env.now
#			end_time = 0
#			packet = [packet_ID_A,block_size,r_w,"Node-A",start_time, end_time]
#			I_O_queue_B.append(packet)
#			print "Writing to I_O_queue_from_A_to_B at Node B's queue"
#			print I_O_queue_B
#			packet_ID_A = packet_ID_A+1
#			print "Testing123"
#			print packet_ID_A
#			yield env.timeout(1)                   
#		if (len(disk_queue_A) > 0):
#			process_A = disk_queue_A.popleft()
#			print "Pop first element from queue_A"
#			print process_A
#			packet_ID = process_A[0]
#			if (process_A[2] == "r"):
#				r_w_delay = random.randint(2,3)
#				disk_read_response_A.append(r_w_delay)
#			else:
#				r_w_delay = random.randint(2,5)
#				disk_write_response_A.append(r_w_delay)
#			disk_response_A.append(r_w_delay)
#			if (process_A[3] == "Node-B"):
#				network_delay = random.randint(2,6)								#extra delay to movethe packet over network to other node, if its same node no extra delay
#				++Network_Q_len
#				Network_queue_in.append(packet)
#				print "TESTING SWITCH"
#				print n
#				Response_B[packet_ID] = (network_delay + r_w_delay)			#Total response time for one of the packet of node B
#				print ("Updating total response time for naode B packetID: %d and response time: %d "% (packet_ID, Response_B[packet_ID])
#			else:
#				Response_A[packet_ID] = (r_w_delay)			#Total response time for one of the packet of node A
#			if (len(I_O_queue_A) > 0):
#				packet_from_B_to_A = I_O_queue_A.popleft() 
#				disk_queue_A.append(packet_from_B_to_A)
#			
##			yield env.timeout(r_w_delay)                   
#def server_B(env):
#       global I_O_queue_A
#        global I_O_queue_B
#	global Response_A
#	global Response_B
#	global packet_ID_A
#	global packet_ID_B
#	global internal_B
#	global Network_queue_in
#	global Network_queue_out
#
#	disk_queue_B = deque([])
#	process_B = []												#Temp list to hold value from list of list	
#	print "Inside serverB" 
#       time_now=datetime.datetime.now().time()
#       hour=time_now.hour
#	packet_ID_B = 0
#	in_B=[None]*500000
#	
#	block_size = 100
#	r_w = "r"
#	while True:
#		if (internal_B > 0):
#			--internal_B
#			start_time = env.now
#			r_w = random.choice('rw')
#			end_time = 0
#			packet = [packet_ID_B,block_size,r_w,"Node-B",start_time, end_time]
#			disk_queue_B.append(packet)	
#			print disk_queue_B
#			packet_ID_B=packet_ID_B+1
#			yield env.timeout(1)
#		if (I_O_B_to_A > 0):										#If there any IO request from A to B 
#			--I_O_B_to_A
#			start_time = env.now
#			end_time = 0
#			packet = [packet_ID_B,block_size,r_w,"Node-B",start_time, end_time]
#			I_O_queue_A.append(packet)
#			print "Writing to I_O_queue-B"
#			print I_O_queue_B
#			packet_ID_B=packet_ID_B+1
#			yield env.timeout(3)                   
#		if (len(disk_queue_B) > 0):
#			process_B = disk_queue_B.popleft()
#			print "Pop first element from queue_B"
#			print process_B
#			packet_ID = process_B[0]
#			if (process_B[2] =="r"):								#Delay depends on if its is read or if its write
#				r_w_delay = time_out = random.randint(2,3)
#				disk_read_response_B.append(r_w_delay)
#			else:
#				r_w_delay = time_out = random.randint(2,6)
#				disk_write_response_B.append(r_w_delay)	
#	
#			disk_response_B.append(r_w_delay)
#			if (process_B[3] == "Node-A"):
#				network_delay = random.randint(2,8)
#				Response_A[packet_ID] = ((network_delay + r_w_delay) )			#Total response time for one of the packet of node B
#			else:
#				Response_B[packet_ID] = (r_w_delay )			#Total response time for one of the packet of node A
#			disk_response_B.append(r_w_delay)	
#			if (len(I_O_queue_B) > 0):
#				packet_from_A_to_B = I_O_queue_B.popleft() 
#				disk_queue_B.append(packet_from_A_to_B)
#			yield env.timeout(time_out)                   
#
#
#def network_switch(pac):
#	print "TEST SWITCH"
#	print pac
#	print pac[5]
#	pac[5] = random.randint(3,4)
#	print pac[5]
#	return pac 
#	

def plot_latency_A(env):
	global cache_hit_A
	global cache_hit_B
	global disk_hit_A
	global disk_hit_B
	global network_hit

	axes = plt.gca()
	axes.set_ylim([1,15])
	print Response_A
	print Response_B
	plt.rcParams.update({'font.size': 17})
	red_patch = mpatches.Patch(color='blue', label='Overall I/O latency at node A')
	plt.legend(handles=[red_patch])
	plt.figure(1)
	plt.plot(Response_A)
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Total Disk latency at node A')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(disk_response_A)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Disk Read latency at node A')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(disk_read_response_A)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Disk write latency at node A')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(disk_write_response_A)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Overall I/O latency at node B')
	plt.legend(handles=[red_patch])
	#plt.figure(2)
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(Response_B)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Total Disk latency at node B')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(disk_response_B)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Disk Read latency at node B')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(disk_read_response_B)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Disk write latency at node B')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(disk_write_response_B)
	plt.show()
	red_patch = mpatches.Patch(color='blue', label='Switch Respose time')
	plt.legend(handles=[red_patch])
	plt.ylabel('Latency in milli seconds')
	plt.xlabel('Requests')
	plt.plot(Network_response)
	plt.show()
#	red_patch = mpatches.Patch(color='blue', label='Num of Packets at different locations')
#	plt.legend(handles=[red_patch])
#	plt.ylabel('Number of packets')
#	plt.xlabel('Packets at different locations, Cache, disk and Network')
#	plt.bar((cache_hit_A+cache_hit_B),(disk_hit_A+disk_hit_B),network_hit)
#	plt.show()

#def plot_latency_B(env):
#	axes = plt.gca()
#	axes.set_ylim([1,15])
#	plt.plot(Response_B)
#	plt.ylabel('I/O Latency at server B in mili seconds')
#	plt.show()

	

if __name__ == '__main__':
        main()

