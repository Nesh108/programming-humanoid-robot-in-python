'''In this exercise you need to implement the PID controller for joints of robot.

* Task:
    1. complete the control function in PIDController with prediction
    2. adjust PID parameters for NAO in simulation

* Hints:
    1. the motor in simulation can simple modelled by angle(t) = angle(t-1) + speed * dt
    2. use self.y to buffer model prediction
'''

# add PYTHONPATH
import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'introduction'))

import numpy as np
from collections import deque
from spark_agent import SparkAgent, JOINT_CMD_NAMES

import time

class PIDController(object):
    '''a discretized PID controller, it controls an array of servos,
       e.g. input is an array and output is also an array
    '''
    def __init__(self, dt, size):
        '''
        @param dt: step time
        @param size: number of control values
        @param delay: delay in number of steps
        '''
        self.dt = dt
        self.u = np.zeros(size)
        self.e1 = np.zeros(size)
        self.e2 = np.zeros(size)
        # ADJUST PARAMETERS BELOW
        delay = 0
        self.Kp = 5
        self.Ki = 5
        self.Kd = 0

        self.Derivator = 0
        self.Integrator = 0
        self.Integrator_max = 500
        self.Integrator_min = -500

        self.y = deque(np.zeros(size), maxlen=delay + 1)

    def set_delay(self, delay):
        '''
        @param delay: delay in number of steps
        '''
        self.y = deque(self.y, delay + 1)

    def control(self, target, sensor):
        '''apply PID control
        @param target: reference values
        @param sensor: current values from sensor
        @return control signal
        '''

        # YOUR CODE HERE
        #self.P_value = self.Kp * self.e1

        print "Current Sensors"
        print sensor

        print "Target Values"
        print target

        i = 0
        for current_val,set_point in np.c_[sensor,target]:
            print "{}# {} --> {}".format(i, current_val, set_point)
            self.error = set_point - current_val
            self.p_value = self.Kp * self.error
            self.d_value = self.Kd * (self.error - self.Derivator)
            self.Derivator = self.error
            self.Integrator = self.Integrator + self.error
            if self.Integrator > self.Integrator_max:
                    self.Integrator = self.Integrator_max
            elif self.Integrator < self.Integrator_min:
                    self.Integrator = self.Integrator_min
            self.i_value = self.Integrator * self.Ki
            self.u = np.insert(self.u,i, (self.p_value + self.i_value + self.d_value))
            i+=1

        print "new PID array:"
        print self.u

        return self.u


class PIDAgent(SparkAgent):
    def __init__(self, simspark_ip='localhost',
                 simspark_port=3100,
                 teamname='DAInamite',
                 player_id=0,
                 sync_mode=True):
        super(PIDAgent, self).__init__(simspark_ip, simspark_port, teamname, player_id, sync_mode)
        self.joint_names = JOINT_CMD_NAMES.keys()
        number_of_joints = len(self.joint_names)
        self.joint_controller = PIDController(dt=0.01, size=number_of_joints)
        self.target_joints = {k: 0 for k in self.joint_names}

    def think(self, perception):
        action = super(PIDAgent, self).think(perception)
        joint_angles = np.asarray(perception.joint.values())
        target_angles = np.asarray(self.target_joints.values())
        u = self.joint_controller.control(target_angles, joint_angles)
        action.speed = dict(zip(self.joint_names, u))
        return action


if __name__ == '__main__':
    agent = PIDAgent()
    agent.target_joints['HeadYaw'] = 1.0
    agent.run()
