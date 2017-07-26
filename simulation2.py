# This is a simpy based  simulation of a M/M/1 queue system
import numpy as np
import pylab as pl
import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 1000000
MU = 1
numOfHosts = 10


Binary = "Binary"
Linear = "Linear"


def BinaryReschedule(h,timeslot):
	k = min(h.numOfRetransmitted, 10)

		#print("Host # " + str(h.hostNum) + " with transmitSlot " + str(h.slotNumberOfNextTransmission) + " comparing with " + str(timeslot))
	r = (random.randint(0,2**k))

	h.slotNumberOfNextTransmission = timeslot + r + 1 # add one because transmit in next timeslot

		# print("Host # " + str(h.hostNum) + " reschedule at timeslot # " + str(h.slotNumberOfNextTransmission) +
		# " and num of retransmitted " + str(h.numOfRetransmitted))
	h.numOfRetransmitted += 1


def LinearReschedule(h,timeslot):
	k = min(h.numOfRetransmitted, 1024)

	r = (random.randint(0,k))

	h.slotNumberOfNextTransmission = timeslot + r + 1

	h.numOfRetransmitted += 1


""" Queue system  """
class Host:
	def __init__(self, env, arrival_rate):
		self.env = env
		self.arrival_rate = arrival_rate
		self.numOfRetransmitted = 0
		self.numOfPacket = 0
		self.env.process(self.packets_arrival(env))  # receiving packets
		self.slotNumberOfNextTransmission = -1
		#self.hostNum = hostnum

	def setSlotNumnberOfNextTransmission(self,nextSlotTime):
		if self.numOfPacket >=1 and self.slotNumberOfNextTransmission == -1:  # assgin the transmit slot for the head
			self.slotNumberOfNextTransmission = nextSlotTime

	def processPocket(self):
		self.numOfPacket -= 1
	def resetNumOfRetransmitted(self):
		self.numOfRetransmitted = 0
	def resetSlotNumberOfNextTransmission(self):
		self.slotNumberOfNextTransmission = -1
	def packets_arrival(self, env):
		# packet arrivals
		while True:
		     # Infinite loop for generating packets
			yield env.timeout(random.expovariate(self.arrival_rate))
			  # arrival time of one packet
			arrival_time = env.now   # arrival cannot to int
			self.numOfPacket += 1
			self.setSlotNumnberOfNextTransmission(int(arrival_time)+1) # need to add one because they are floating number
																		# transmit at next slot

class Link:
	def __init__(self, env , numOfHosts, arrival_rate, alg):
		self.currentSlottedTime = 0
		self.numOfIdle = 0
		self.numOfCollision = 0
		self.numOfSuccess = 0
		self.algorithm = alg # linear or binary
		self.hosts = [ Host(env,arrival_rate) for i in range(numOfHosts) ] # initize 10 hosts
	def run(self,env):

		while True:
			yield env.timeout(1)
			#x = 1

			# print("time slot # " + str(self.currentSlottedTime))
			# print("Before")
			#
			# for h in self.hosts:
			# 	print("Host # " + str(x) + " has "+ str(h.numOfPacket) +
			# 	" packets , next transmit start at " + str(h.slotNumberOfNextTransmission))
			# 	x += 1
			# x = 1
			tempHostArr = []
			counter = 0  #count num of host want to transmit
			for h in self.hosts:
				if h.slotNumberOfNextTransmission == self.currentSlottedTime:
					tempHostArr.append(h)



			# print("=======")
			# for h in tempHostArr:
			# 	print("host # "+str(h.hostNum))
			#
			# print("=======")
			if not tempHostArr: # if no host want to transmit
				#print("Idle")
				self.numOfIdle += 1
			elif len(tempHostArr) > 1: # if more than one hosts want to transmit, collision
				#print("collision")
				if self.algorithm == Binary: #choose algorithm
					for h in tempHostArr:
						BinaryReschedule(h,self.currentSlottedTime)
				elif self.algorithm == Linear:
					for h in tempHostArr:
						LinearReschedule(h,self.currentSlottedTime)
				self.numOfCollision += 1
			else: 						# only one host want to transmit
				#print("transmit")
				self.numOfSuccess += 1
				tempHostArr[0].resetNumOfRetransmitted()
				tempHostArr[0].processPocket()
				tempHostArr[0].resetSlotNumberOfNextTransmission()
				tempHostArr[0].setSlotNumnberOfNextTransmission(self.currentSlottedTime+1)


			#print("After")

			# for h in self.hosts:
			#  	print("Host # " + str(x) + " has "+ str(h.numOfPacket) +
			# 	" packets , next transmit start at " + str(h.slotNumberOfNextTransmission))
			#  	x += 1
			# x = 1
			self.currentSlottedTime += 1

			#print("--------------------")



def main():


	random.seed(RANDOM_SEED)
	lp = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

	algorithm = [Binary , Linear]

	for alg in algorithm:
		listOfThroughput = []
		print("---------------------------------------------------")
		print("simulating " + alg + " backoff algorithm: \n")
		print ("{0:<4} {1:<9} {2:<9} {3:<9} {4:<4}".format(
		        "Lambda", "Throughput", "Successes", "Collisions", "Idle"))
		for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
			env = simpy.Environment()
			link = Link(env, numOfHosts, arrival_rate, alg)
			env.process(link.run(env))
			env.run(until=SIM_TIME)

			throughtPut = float(link.numOfSuccess)/float(link.numOfSuccess + link.numOfIdle + link.numOfCollision)
			listOfThroughput.append(throughtPut)
			print ("{0:<9} {1:<9.5f} {2:<9} {3:<9} {4:<4}".format(
		        str(arrival_rate), round(throughtPut,5), str(link.numOfSuccess), str(link.numOfCollision) ,str(link.numOfIdle)))
		pl.plot(lp, listOfThroughput)
		pl.title("Throughput vs. lambda" + alg)
		pl.xlabel("arrival rate(lambda)")
		pl.ylabel("throughtPut")
		pl.show()		

if __name__ == '__main__': main()
