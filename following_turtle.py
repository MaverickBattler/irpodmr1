#! /usr/bin/python3

import roslib
import rospy
import math
import tf
import geometry_msgs.msg
from turtlesim.srv import Spawn
import turtlesim.msg

class TurtleBot:

	def handle_turtle_pose(self, msg, turtlename):
		br = tf.TransformBroadcaster()
		br.sendTransform((msg.x, msg.y, 0),
			tf.transformations.quaternion_from_euler(0, 0, msg.theta),
			rospy.Time.now(),
			turtlename,
			"world")
			
	def set_subscriber_callback(self, turtlename):
		rospy.Subscriber('/%s/pose' % turtlename,
			turtlesim.msg.Pose,
			self.handle_turtle_pose,
			turtlename)
		
	def spawn_a_turtle(self):
		rospy.wait_for_service('spawn')
		spawner = rospy.ServiceProxy('spawn', Spawn)
		spawner(4, 2, 0, 'turtle2')
    	
	def define_turtle_movement(self):
		listener = tf.TransformListener()
		turtle_vel = rospy.Publisher('turtle2/cmd_vel', geometry_msgs.msg.Twist,queue_size=1)
		
		rate = rospy.Rate(10.0)
		while not rospy.is_shutdown():
			try:
				(trans,rot) = listener.lookupTransform('/turtle2', '/turtle1', rospy.Time(0))
			except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
				continue

			angular = 4 * math.atan2(trans[1], trans[0])
			linear = float(rospy.get_param('vel')) * math.sqrt(trans[0] ** 2 + trans[1] ** 2)
			cmd = geometry_msgs.msg.Twist()
			cmd.linear.x = linear
			cmd.angular.z = angular
			turtle_vel.publish(cmd)

			rate.sleep()
		
	def make_turtle_follow(self):
		self.set_subscriber_callback('turtle1')
		self.set_subscriber_callback('turtle2')
		self.spawn_a_turtle()
		self.define_turtle_movement()
		
		
if __name__ == '__main__':
	try:
		rospy.init_node('turtle_controller')
		x = TurtleBot()
		x.make_turtle_follow()
	except rospy.ROSInterruptException:
		pass