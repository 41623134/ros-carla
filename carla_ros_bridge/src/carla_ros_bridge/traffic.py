#!/usr/bin/env python

#
# Copyright (c) 2018-2019 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
#
"""
Classes to handle Carla traffic objects
"""

import rospy
from visualization_msgs.msg import Marker
from carla_ros_bridge.actor import Actor
from carla import TrafficLightState
import carla_ros_bridge.transforms as transforms
from std_msgs.msg import ColorRGBA
from geometry_msgs.msg import TransformStamped


class Traffic(Actor):

    """
    Actor implementation details for traffic objects
    """

    @staticmethod
    def create_actor(carla_actor, parent):
        """
        Static factory method to create traffic actors

        :param carla_actor: carla actor object
        :type carla_actor: carla.Actor
        :param parent: the parent of the new traffic actor
        :type parent: carla_ros_bridge.Parent
        :return: the created traffic actor
        :rtype: carla_ros_bridge.Traffic or derived type
        """
        if carla_actor.type_id == "traffic.traffic_light":
            return TrafficLight(carla_actor=carla_actor, parent=parent)
        else:
            return Traffic(carla_actor=carla_actor, parent=parent)

    def __init__(self, carla_actor, parent, topic_prefix=None, append_role_name_topic_postfix=True):
        """
        Constructor

        :param carla_actor: carla actor object
        :type carla_actor: carla.Actor
        :param parent: the parent of this
        :type parent: carla_ros_bridge.Parent
        :param topic_prefix: the topic prefix to be used for this actor
        :type topic_prefix: string
        """
        if topic_prefix is None:
            topic_prefix = 'traffic'
        super(Traffic, self).__init__(carla_actor=carla_actor,
                                      parent=parent,
                                      topic_prefix=topic_prefix,
                                      append_role_name_topic_postfix=append_role_name_topic_postfix)
        if self.__class__.__name__ == "Traffic":
            rospy.logwarn("Created Unsupported Traffic Actor"
                          "(id={}, parent_id={}, type={}, attributes={})".format(
                              self.get_id(), self.get_parent_id(),
                              self.carla_actor.type_id, self.carla_actor.attributes))


class TrafficLight(Traffic):

    """
    Traffic implementation details for traffic lights
    """

    def __init__(self, carla_actor, parent):
        """
        Constructor

        :param carla_actor: carla actor object
        :type carla_actor: carla.TrafficLight
        :param parent: the parent of this
        :type parent: carla_ros_bridge.Parent
        """
        topic_prefix = 'traffic.traffic_light'
        super(TrafficLight, self).__init__(carla_actor=carla_actor,
                                           parent=parent, topic_prefix=topic_prefix)
        rospy.logwarn("Created Traffic-Light Actor(id={}, parent_id={}, type={}, attributes={}). "
                      "Not yet fully implemented!".format(
                          self.get_id(), self.get_parent_id(),
                          self.carla_actor.type_id, self.carla_actor.attributes))

    def send_marker_msg(self):
        """
        Function to send marker messages of this traffic light

        :return:
        """
        marker = self.get_marker(use_parent_frame=False)
        marker.type = Marker.CUBE
        #marker.pose = self.get_current_ros_pose()
        #todo: get bounding box from carla (currently only supported for vehicles)
        marker.pose.position.z = 2.6
        marker.scale.x = 0.4
        marker.scale.y = 0.3
        marker.scale.z = 1
        self.publish_ros_message('/carla/traffic_light_marker', marker)

    def get_marker_color(self):  # pylint: disable=no-self-use
        """

        """
        color = ColorRGBA()
        state = self.carla_actor.get_state()
        if state == TrafficLightState.Red:
            color.r = 255
            color.g = 0
            color.b = 0
        elif state == TrafficLightState.Yellow:
            color.r = 255
            color.g = 255
            color.b = 0
        elif state == TrafficLightState.Green:
            color.r = 0
            color.g = 255
            color.b = 0
        else: #unknown
            color.r = 255
            color.g = 255
            color.b = 255

        return color

    def update(self):
        """
        Function (override) to update this object.

        :return:
        """
        self.send_tf_msg()
        self.send_marker_msg()
        super(TrafficLight, self).update()
