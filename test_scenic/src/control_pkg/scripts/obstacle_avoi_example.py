#!/usr/bin/env python

import rospy
import math

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from kobuki_msgs.msg import BumperEvent 
from kobuki_msgs.msg import CliffEvent
import sys, select, termios, tty


range_center = Float32()
range_left = Float32()
range_right = Float32()
range_left_last = Float32()
range_right_last = Float32()


turnAngle = 17
backUpDistance = 6
speed = 0.5

def callback(data):
	#rospy.loginfo("Center: %f", data.ranges[359])
	#rospy.loginfo("Left: %f", data.ranges[180])
	#rospy.loginfo("Right: %f", data.ranges[540])
	range_center.data = data.ranges[359] 
	range_left.data = data.ranges[180]
	range_right.data = data.ranges[540]

def processBump(data):
	print ("Bump!")
	global bp
	global which_bp
	if (data.state == BumperEvent.PRESSED):
		bp = True
	else:
		bp = False
	rospy.loginfo("Bumper Event")
	rospy.loginfo(data.bumper)
	which_bp = data.bumper

def processCliff(data):
	print ("Cliff!")
	global cf
	global which_cf
	global dis
	if (data.state == CliffEvent.CLIFF):
		cf = True
	else:
		cf = False
	rospy.loginfo("Cliff Event")
	rospy.loginfo(data.sensor)
	which_cf = data.sensor
	dis = data.bottom


def set_normal_speed():
	twist.linear.x = speed
	twist.linear.y, twist.linear.z = 0, 0
	twist.angular.x, twist.angular.y = 0, 0
	twist.angular.z = 0

def turn_left():
	twist.linear.x = 0
	twist.linear.y, twist.linear.z = 0, 0
	twist.angular.x, twist.angular.y = 0, 0
	twist.angular.z = 1 * speed


def turn_right():
	twist.linear.x = 0
	twist.linear.y, twist.linear.z = 0, 0
	twist.angular.x, twist.angular.y = 0, 0
	twist.angular.z = -1 * speed


def set_backup_speed():
	twist.linear.x = -1 * speed
	twist.linear.y, twist.linear.z = 0, 0
	twist.angular.x, twist.angular.y = 0, 0
	twist.angular.z = 0

# mode = {'forward', 'backup', 'turnLeft', 'turnRight'}

def move():
	pub = rospy.Publisher('mobile_base/commands/velocity', Twist, queue_size = 20)
	sub1 = rospy.Subscriber("scan", LaserScan, callback)
	sub2 = rospy.Subscriber('mobile_base/events/bumper', BumperEvent, processBump)
	sub3 = rospy.Subscriber('mobile_base/events/cliff', CliffEvent, processCliff)
	rospy.init_node('test', anonymous = True)
	rate = rospy.Rate(10) # 10HZ
	global twist, mode, cf, which_cf, which_bp, dis, bp
	cf = False
	which_cf = 0
	which_bp = 0
	twist = Twist()
	left, right, bp = False, False, False
	mode = 'Forward'
	BackupCounter = 0
	TurnRightCounter, TurnLeftCounter = 0, 0
	ignoreCliff = False
	while not rospy.is_shutdown():

		if (mode == 'Forward'):
			set_normal_speed()
		elif (mode == 'Backup'):
			ignoreCliff = True
			set_backup_speed()
			BackupCounter += 1
		elif (mode == 'TurnLeft'):
			ignoreCliff = False
			left = False
			turn_left()
			TurnLeftCounter += 1
		elif (mode == 'TurnRight'):
			ignoreCliff = False
			right = False
			turn_right()
			TurnRightCounter += 1
		pub.publish(twist)

		if (left and BackupCounter > backUpDistance):
			BackupCounter = 0
			mode = 'TurnLeft'
		if (right and BackupCounter > backUpDistance):
			BackupCounter = 0
			mode = 'TurnRight'
		if (TurnRightCounter > turnAngle):
			TurnRightCounter = 0
			mode = 'Forward'
		if (TurnLeftCounter > turnAngle):
			TurnLeftCounter = 0
			mode = 'Forward'
		# if (range_center.data > 1 and not mode == 'Backup' and not mode == 'TurnLeft' and not mode == 'TurnRight'):
		# 	if (range_left.data < 0.2):
		# 		mode = 'Backup'
		# 		if (not right and not left):
		# 			BackupCounter = 0
		# 		right, left = True, False
		# 	elif (range_right.data < 0.2):
		# 		mode = 'Backup'
		# 		if (not right and not left):
		# 			BackupCounter = 0
		# 		right, left = False, True
		# elif (range_center.data < 1 and range_center.data > 0.001):
		# 	mode = 'Backup'
		# 	if (not right and not left):
		# 		BackupCounter = 0
		# 	right, left = False, True
		if (not ignoreCliff and cf and which_cf == 0):
			if (dis < 50000):
				which_cf = 0
				mode = 'Backup'
				print("left cliff")
				if (not right and not left):
					BackupCounter = 0
				right, left = True, False
		elif (not ignoreCliff and cf and (which_cf == 2 or which_cf == 1)):
			if (dis < 50000):
				which_cf = 0
				print("right cliff")
				mode = 'Backup'
				if (not right and not left):
					BackupCounter = 0
				right, left = False, True

		if (bp and which_bp == 0):
			which_bp = 0
			mode = 'Backup'
			print("left bump")
			if (not right and not left):
				BackupCounter = 0
			right, left = True, False
		elif (bp and (which_bp == 2 or which_bp == 1)):
			which_bp = 0
			print("right bump")
			mode = 'Backup'
			if (not right and not left):
				BackupCounter = 0
			right, left = False, True
		print(mode)
		rate.sleep()

if __name__ == '__main__':
	try:
		move()
	except rospy.ROSInterruptException:
		pass
