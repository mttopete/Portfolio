# Rllib docs: https://docs.ray.io/en/latest/rllib.html
# Malmo XML docs: https://docs.ray.io/en/latest/rllib.html

import time
import numpy as np
from parseIsland import island

import gym
from gym.spaces import Box
from jack import Jack


class BridgeBuilder(Jack):

    def __init__(self, env_config):
        super().__init__(env_config)

        # Bridge Builder Parameters
        self.pos = [0, 0]
        self.pitch = 0
        self.yaw = 0
        self.movement_vector = None
        self.bridge_len = 0
        self.bridge_dir = 0

        # Rllib Parameters
        self.action_space = Box(low=np.array([-1, -1, -2, -1, -1]), high=np.array([1, 1, 2, 1, 1]), dtype=np.byte)


    def reset(self):
        self.pos = [0, 0]
        self.pitch = 0
        self.yaw = 0
        self.movement_vector = None
        self.bridge_len = 0
        self.bridge_dir = 0
        return super().reset()

    def step(self, action):
        self.checkEndTrain()

        reward = 0
        move = "{:.1f}".format(action[0])
        turn = "{:.1f}".format(action[1])
        self.last_turn = action[1]
        attack = 0 if action[2] < 0 else 1
        pitch = "{:.1f}".format(action[3] * 0.1)
        # build_bridge = 1
        build_bridge = 0 if action[4] < 0 else 1

        while not self.agent_host.getWorldState().has_mission_begun:
            time.sleep(0.1)

        # Get Observation
        world_state = self.agent_host.getWorldState()
        for error in world_state.errors:
            if "commands connection is not open. Is the mission running?" not in error.text:
                print("Error:", error.text)

        original_wood_amount = self.getInventory()['log']

        self.get_observation(world_state)

        if attack:
            self.checkAttack(attack)

        self.agent_host.sendCommand(f'pitch {pitch}')
        self.agent_host.sendCommand(f'move {move}')
        self.agent_host.sendCommand(f'turn {turn}')
        time.sleep(.2)

        self.episode_step += 1

        if build_bridge:
            reward += self.buildBridge()
        
        if self.block_in_view == 'log':
            reward += 10
        elif self.block_in_view == 'leaves':
            reward += 3

        if not self.axe:
            self.craftAxe()

        self.observe(peek=True)

        new_wood_amount = self.getInventory()['log']

        reward += ((new_wood_amount - original_wood_amount)*50)

        # Get Done
        done = not world_state.is_mission_running

        # Get Reward
        for r in world_state.rewards:
            reward += r.getValue()
        
        self.episode_return += reward

        #self.printStep(move, turn, pitch, reward, attack, build_bridge)

        self.observe()
      
        return self.obs, reward, done, dict()


    def printStep(self, move, turn, pitch, reward, attack, build_bridge):
        s = super().printStep(move, turn, pitch, reward, attack, print_too = False)

        i = s.index('| reward')
        
        print( s[:i] + f'| build_bridge: {build_bridge} ' + s[i:] )


    def buildBridge(self):

        if self.bridgeBuildable() and self.centerJack():
            self.startBuilding()
            reward = -1 * ((self.bridge_len // 4) * 50)
            return reward

        return 0


    def bridgeBuildable(self):

        if self.stoppedOnEdge():

            obs_island = island(self.obs)

            if obs_island:
                wood_quantity = self.woodQuantity()

                for b_len in range(2, 11):

                    if b_len > wood_quantity:
                        break

                    if self.islandExists(obs_island, b_len):
                        self.bridge_len = b_len
                        return True

        return False

    
    def stoppedOnEdge(self):
        try:
            ypos = self.obs_dict[u'YPos']
        except TypeError:  # indicates infinite loop
            return False

        self.observe()

        if (ypos == 3) and self.onEdge():

            self.agent_host.sendCommand('move 0')
            time.sleep(0.2)
            self.agent_host.sendCommand('turn 0')
            time.sleep(0.2)
            self.agent_host.sendCommand('pitch 0')
            time.sleep(0.2)

            return (self.obs_dict[u'YPos'] == 3) and self.onEdge()
        
        return False


    def onEdge(self):
        self.observe()
        try:
            self.pos = [self.obs_dict[u'XPos'], self.obs_dict[u'ZPos']]
        except TypeError:  # implies an inifinite loop
            return False

        return ([self.obs[0][11][10], self.obs[0][10][11], self.obs[0][9][10], self.obs[0][10][9]].count(0) == 1)


    def woodQuantity(self):
        planks = 0

        for i in range(0,39):

            try:
                if planks >= 10:
                    return planks

                if self.obs_dict['InventorySlot_'+str(i)+'_item'] == 'planks':
                    planks += self.obs_dict[u'InventorySlot_'+str(i)+'_size']

                elif self.obs_dict['InventorySlot_'+str(i)+'_item'] == 'log':

                    if planks < 10:
                        for log in range(self.obs_dict[u'InventorySlot_'+str(i)+'_size']):
                            time.sleep(.2)
                            self.agent_host.sendCommand("craft planks")
                            planks += 4
                            
                            if planks >= 10:
                                return planks

            except TypeError:
                return 0
        
        return planks
    

    def islandExists(self, obs_island, i):

        self.observe()

        if self.obs[0][10][10] != 2:
            return False

        front, _ = self.getIntendedYaw()

        if (obs_island[0][10-1][10], obs_island[0][10-i][10]) == (0, 2):
            self.bridge_dir = front
            return True

        elif (obs_island[0][10][10-1], obs_island[0][10][10-i]) == (0, 2):
            self.bridge_dir = self.yawPlus(front, 270)
            return True

        elif (obs_island[0][10][10+1], obs_island[0][10][10+i]) == (0, 2):
            self.bridge_dir = self.yawPlus(front, 90)
            return True

        elif (obs_island[0][10][10+1], obs_island[0][10+i][10]) == (0, 2):
            self.bridge_dir = self.yawPlus(front, 180)
            return True

        return False
        

    def centerJack(self):
        self.updatePos()
        x_yaw, dir = self.closestXDir()
        self.setYaw(x_yaw, dir, peeked=True)

        if not self.fixPos(x_yaw):
            return False

        z_yaw = x_yaw + (dir * 90)

        if z_yaw == -90:
            z_yaw = 270

        self.setYaw(z_yaw, dir)

        if not self.fixPos(z_yaw):
            return False

        return self.foundBridge(dir)


    def closestXDir(self):
        if self.yaw in {0, 180}:
            return self.yaw, 0

        if self.yaw > 180:
            diff = self.yaw - 180
            dir = -1
        else:
            diff = 180 - self.yaw
            dir = 1

        if diff < 90:
            return 180, dir
        else:
            return 0, (-1 * dir)

        
    def setYaw(self, target_yaw, dir, peeked=False):
        self.aim(target_yaw, dir, 0.5, observed=peeked)
        self.aim(target_yaw, (-1 * dir), 0.2)


    def aim(self, target_yaw, dir, speed, set_pitch = True, observed = False):
        self.updatePos(peeked=observed)

        last = self.yaw
        dir_switched = False
        moving = False

        # turn the correct direction
        
        while not self.isPast(last, target_yaw, dir):
            if (not set_pitch) and (not dir_switched) and self.movingAway(last, target_yaw):
                dir *= -1
                dir_switched = True

            if not moving:
                time.sleep(0.2)
                self.agent_host.sendCommand(f'turn {dir * speed}')
                moving = True

            last = self.yaw
            self.updatePos()
            
        self.agent_host.sendCommand('turn 0')

        if set_pitch:
            self.lookDown()


    def isPast(self, last, degree, dir):
        n = self.yaw

        if last == n:
            return n == degree

        if dir == -1:
            last, n = n, last

        if degree == 0:
            return (last == 0) or (n < last)
        else:
            return last <= degree < n


    def movingAway(self, last, target_yaw):
        return self.distanceBetween(target_yaw, self.yaw) > self.distanceBetween(target_yaw, last)


    def distanceBetween(self, target, point):

        if (target == 0) and (point > 180):
            return 360 - point

        if (target > point):
            return target - point

        return point - target


    def lookDown(self):
        while self.pitch < 90:
            self.agent_host.sendCommand('pitch 50')
            self.updatePos()
        self.agent_host.sendCommand('pitch 0')


    def fixPos(self, yaw):
        offset = self.offset(yaw)

        while offset:
            if self.obs_dict['LineOfSight']['type'] == 'stone':
                self.agent_host.sendCommand('move 0')
                return False

            self.agent_host.sendCommand(f'move {offset*.1}')

            offset = self.offset(yaw)
        
        self.agent_host.sendCommand('move 0')
        return True


    def offset(self, yaw):
        self.updatePos()

        i = 0 if yaw in {90, 270} else 1

        offset = (self.pos[i] % 1)

        if offset > .65:
            if yaw in {0, 270}:
                return -1
            else:
                return 1
        elif offset < .35:
            if yaw in {0, 270}:
                return 1
            else:
                return -1
        else:
            return 0

    
    def foundBridge(self, dir):

        for _ in range(4):
            self.setYaw(self.bridge_dir, dir)

            if self.edgeForward():
                self.setMovementVector()
                return True
                
            self.bridge_dir = self.yawPlus(self.bridge_dir, 90)

        return False

    
    def edgeForward(self):
        self.lookDown()

        last_cursor = cursor = self.coord(self.getCursor())

        moving = False

        while cursor:
            if cursor != last_cursor:

                try:
                    found_stone = (self.obs_dict['LineOfSight']['type'] == 'stone')
                except TypeError:
                    break
                
                return found_stone

            if not moving:
                self.agent_host.sendCommand('pitch -0.1')
                moving = True

            last_cursor = cursor
            cursor = self.coord(self.getCursor())

        return False

    
    def setMovementVector(self):
        if self.bridge_dir == 0:
            self.movement_vector = [0, 1]

        elif self.bridge_dir == 90: # may need to switch
            self.movement_vector = [-1, 0]

        elif self.bridge_dir == 180:
            self.movement_vector = [0, -1]

        elif self.bridge_dir == 270:
            self.movement_vector = [1, 0]


    def getSubsequentYaws(self):
        target_yaw, dir = self.getIntendedYaw()

        if target_yaw == 0:
            subs = [90, 180, 270]
        elif target_yaw == 90:
            subs = [180, 270, 0]
        elif target_yaw == 180:
            subs = [270, 0, 90]
        else:
            subs = [0, 90, 180]

        if dir == -1:
            subs.reverse()

        yaws = [target_yaw, subs[0], subs[1], subs[2]]

        return dir, yaws

    
    def getIntendedYaw(self):

        if (45 <= self.yaw < 135):
            yaw = 90
        elif (135 <= self.yaw < 225):
            yaw = 180
        elif (225 <= self.yaw < 315):
            yaw = 270
        else:
            yaw = 0

        if yaw == self.yaw:
            dir = 0
        if yaw <= self.yaw < yaw + 90:
            dir = -1
        else:
            dir = 1

        return yaw, dir


    def yawPlus(self, yaw, num):
        result = yaw + num
        
        if result > 359:
            result -= 360
        
        return result



    def checkForBridge(self, yaw, dir):
        distance = 0
        moving = False
        movement_set = None

        self.setYaw(yaw, dir)
        last_cursor = cursor = self.coord(self.getCursor())

        while cursor:
            if cursor != last_cursor:
                distance += 1

                if (cursor[1] == 3) and (distance == 1):
                    break

                if not movement_set:
                    self.setMovementVector(cursor, last_cursor)
                    movement_set = True

                if (self.obs_dict['LineOfSight']['type'] == 'stone') or ( (distance == self.bridge_len) and (self.obs_dict['LineOfSight']['type'] == 'dirt')): 
                    self.agent_host.sendCommand('turn 0')
                    self.agent_host.sendCommand('pitch 0')
                    return True

                elif (distance == self.bridge_len) and (self.obs_dict['LineOfSight']['type'] != 'dirt'):
                    break

            if not moving: 
                self.agent_host.sendCommand('pitch -0.1')

            last_cursor = cursor
            cursor = self.alignedCursor(yaw, movement = movement_set)

        self.agent_host.sendCommand('turn 0')
        self.lookDown()

        return False


    def alignedCursor(self, yaw, movement = True):
        cursor = self.coord(self.getCursor())

        if not movement:
            self.agent_host.sendCommand('turn 0')
            return cursor

        dir = self.alignmentDir(cursor)

        if dir != 0:
            self.aim(yaw, dir, 0.1, set_pitch = False)

            cursor = self.coord(self.getCursor())

        self.agent_host.sendCommand('turn 0')

        return cursor


    def alignmentDir(self, cursor):
        if not cursor:
            return 0

        pos = self.coord(self.pos)

        for i in range(2):
            if self.movement_vector[i] == 0:
                if pos[i] < cursor[i]:
                    return 1
                elif pos[i] > cursor[i]:
                    return -1
                else:
                    return 0


    def startBuilding(self):

        last = list(self.pos)

        time.sleep(0.2)

        self.setPitch(77)

        b_len = 0

        self.equip('planks')

        moving = False
        first_move = True

        i = 0

        cursor = self.getCursor()
        
        while b_len < self.bridge_len:

            cursor = self.getCursor()

            if moving:
                if first_move:
                    time.sleep(0.2)
                    self.agent_host.sendCommand('move 0.2')
                    time.sleep(0.2)
                    first_move = False

                try:
                    sees_stone = (self.obs_dict['LineOfSight']['type'] == 'stone')
                except TypeError:
                    break  # indicates an infinite loop
                        
                if sees_stone:
                    self.agent_host.sendCommand('move 0')
                    moving = False
                        
                if self.coord(self.pos) == self.coord(last):
                    
                    if (self.obs_dict['LineOfSight']['type'] == 'planks'):
                        i+= 1

                    if i > 8:  # we're looking at a plank that's in front of us, not below us
                        self.agent_host.sendCommand('move 0')
                        self.observe(peek=True)
                        time.sleep(0.2)
                        if self.obs_dict['LineOfSight']['type'] == 'planks':
                            self.eliminatePlank()
                            i = 0
                        self.agent_host.sendCommand('move 0.2')
                        

                else:  # we have moved
                    i = 0
                    b_len += 1

                    self.correct(cursor)
                    

                    if b_len == self.bridge_len:
                        break

                
                last = self.pos
                self.updatePos()

            else:  # placing blocks
                try:
                    sees_stone = (self.obs_dict['LineOfSight']['type'] == 'stone')
                except TypeError:
                    break # indicates an infinite loop
                        
                if sees_stone:
                    time.sleep(.2)
                    self.agent_host.sendCommand('use 1')
                    time.sleep(.2)
                    self.agent_host.sendCommand('use 0')
                    
                    self.correct(cursor)
                else:
                    moving = True
                    first_move = True


    def stuckAtPlank(self, last):
        return self.coord(self.pos) == self.coord(last) and (self.obs_dict['LineOfSight']['type'] == 'planks')


    def eliminatePlank(self):
        time.sleep(.2)
        self.agent_host.sendCommand('move 0')
        self.equip('wooden_axe')
        time.sleep(.1)

        self.agent_host.sendCommand('attack 1')
        time.sleep(2.0)


        self.agent_host.sendCommand('attack 0')
        time.sleep(.2)
        self.agent_host.sendCommand('attack 0')

        self.equip('planks')


    def correct(self, c):
        c_x, c_z = c[0], c[2]
        x, z = self.roundDown(self.pos[0]), self.roundDown(self.pos[1])

        if self.bridge_dir in {0, 180}: 
            left, right = self.leftRight(c_x, x)
            
        else:
            left, right = self.leftRight(c_z, z)
            
        if self.bridge_dir in {0, 90}:
            left, right = right, left


        if left:
            time.sleep(.2)
            self.agent_host.sendCommand('turn -0.2')
        elif right:
            time.sleep(.2)
            self.agent_host.sendCommand('turn 0.2')

        time.sleep(.1)
        self.agent_host.sendCommand('turn 0')


    def correctPos(self):
        moving = False

        while self.obs_dict['LineOfSight']['type'] != 'stone':

            if not moving: 
                time.sleep(0.2)
                self.agent_host.sendCommand(f'pitch 0.1')

            self.observe()

        time.sleep(0.1)
        self.agent_host.sendCommand('pitch 0')

        self.setPitch(77)


    def leftRight(self, cursor, pos):
        left, right = False, False

        if self.roundDown(cursor) > pos:
            left = True

        elif self.roundDown(cursor) < pos:
            right = True

        else:
            remainder = (cursor % 1)

            if 0.25 <= remainder <= 0.75:
                return False, False

            if (cursor % 1) > 0.75:
                left = True
            else:
                right = True
        
        return left, right