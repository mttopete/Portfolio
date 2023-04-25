from __future__ import print_function
import time
import json
import numpy as np
import gym
from gym.spaces import Box
from learner import Learner
import math

class Jack(Learner):

    def __init__(self, env_config):  
        super().__init__(env_config)

        # Jack Parameters
        self.equipped_item = ''
        self.block_in_view = ''
        self.axe = True  # CHANGE THIS

        # Rllib Parameters
        self.action_space = Box(low=np.array([-1, -1, -2, -1, -1]), high=np.array([1, 1, 2, 1, 1]), dtype=np.byte)

    def reset(self):
        #self.axe = False
        return super().reset()

    def getInventory(self):
        # FROM craft_work.py in Python_Examples (From the Malmo Download)

        inventory = {
            'wooden_axe': 0,
            'planks': 0,
            'stick': 0,
            'log': 0
        }

        try:
            self.holding_axe = ( self.obs_dict['InventorySlot_0_item'] == 'wooden_axe' )

            for i in range(0,39):
                key = 'InventorySlot_'+str(i)+'_item'
                if key in self.obs_dict:
                    item = self.obs_dict[key]
                    if item in inventory.keys():
                        inventory[item] += int(self.obs_dict[u'InventorySlot_'+str(i)+'_size'])

                    if (not self.holding_axe) and (item == 'wooden_axe'):
                        time.sleep(0.2)
                        self.agent_host.sendCommand(f"swapInventoryItems inventory:0 inventory:{i}")
                        time.sleep(0.2)
        except TypeError:
            pass

        return inventory

    
    def printStep(self, move, turn, pitch, reward, attack, print_too = True):
        s = super().printStep(move, turn, pitch, reward, printing = False)

        i = s.index('| reward')

        new_s = s[:i] + f'| attack: {attack} ' + s[i:]

        if print_too:
            print(new_s)

        return new_s

    
    def step(self, action):
        self.checkEndTrain()

        reward = 0
        move = "{:.1f}".format(action[0])
        turn = "{:.1f}".format(action[1])
        self.last_turn = action[1]
        pitch = "{:.1f}".format(action[2] * 0.1)
        attack = 0 if action[3] < 0 else 1

        while not self.agent_host.getWorldState().has_mission_begun:
            time.sleep(0.1)

        if attack:
            self.checkAttack(attack)

        time.sleep(.2)
        self.agent_host.sendCommand(f'pitch {pitch}')
        time.sleep(.2)
        self.agent_host.sendCommand(f'move {move}')
        time.sleep(.2)
        self.agent_host.sendCommand(f'turn {turn}')
        time.sleep(.2)
            
        self.episode_step += 1
        
        if self.block_in_view == 'log':
            reward += 10
        elif self.block_in_view == 'leaves':
            reward += 3

        if not self.axe:
            self.craftAxe()

        # Get Observation
        world_state = self.agent_host.getWorldState()
        for error in world_state.errors:
            if "commands connection is not open. Is the mission running?" not in error.text:
                print("Error:", error.text)

        self.get_observation(world_state) 

        # Get Done
        done = not world_state.is_mission_running 

        # Get Reward
        for r in world_state.rewards:
            reward += r.getValue()
        
        self.episode_return += reward

        self.printStep(move, turn, pitch, reward, attack)
      
        return self.obs, reward, done, dict()


    def checkAttack(self, attack):
        self.observe(peek=True)

        if self.block_in_view in {'log', 'leaves'}:
            
            self.halt(peeked=True)

            if self.onTarget():
                cursor = self.coord(self.getCursor(peeked = True))
                wood = (self.block_in_view == 'log') 
                self.chop(cursor)

                self.updatePos()
                
                if wood and (not self.cursorAdjacent(cursor)):
                    run_time = self.getWaitTime(cursor)

                    if run_time > 0:
                        self.collectWood(run_time)

    
    def attackTarget(self, cursor):
        last = cursor

        attacking = False

        while last == cursor:
            if not attacking:
                time.sleep(.2)
                self.agent_host.sendCommand(f'attack 1')
                attacking = True

            time.sleep(.2)
            
            self.observe(peek=True)

            last = cursor
            cursor = self.coord(self.getCursor(peeked = True))

        self.agent_host.sendCommand(f'attack 0')
        


    
    def halt(self, peeked = False):
        cursor = self.coord(self.getCursor(peeked=peeked))
        old_cursor = []
        old_pos = []

        i = 0

        while (i < 20) and (cursor != old_cursor) and (self.pos != old_pos):
            i += 1

            self.agent_host.sendCommand('move 0')
            self.agent_host.sendCommand('turn 0')
            self.agent_host.sendCommand('pitch 0')

            if cursor:
                old_cursor = list(cursor)

            old_pos = self.pos
            cursor = self.getCursor()
        
        self.updatePos(peeked = True)


    def getCursor(self, peeked=False):
        if not peeked:
            self.observe(peek=True)

        try:
            cursor = [self.obs_dict['LineOfSight']['x'], self.obs_dict['LineOfSight']['y'], self.obs_dict['LineOfSight']['z']]
            return cursor
        except BaseException:
            return None

    
    def chop(self, cursor):
        last_cursor = cursor
        original_block = self.block_in_view

        attacking = False

        while cursor:

            if not attacking:
                attacking = True
                time.sleep(0.2) 
                self.agent_host.sendCommand(f'attack 1')
            
            if (cursor != last_cursor) or (original_block != self.block_in_view):
                self.halt(peeked=True)
                break

            last_cursor = cursor
            cursor = self.coord(self.getCursor())
        
        self.agent_host.sendCommand(f'attack 0')


    def cursorAdjacent(self, cursor):
        return ((abs(self.pos[0] - cursor[0]), (abs(self.pos[1] - cursor[2]))) in {(0, 0), (0, 1), (1, 0), (1, 1)})


    def getWaitTime(self, cursor):
        a = abs(self.pos[0] - cursor[0])
        b = abs(self.pos[1] - cursor[2])

        distance = int(math.sqrt(a**2 + b**2))

        return distance / 8 # assuming we run around 8 blocks in 1 second

    
    def collectWood(self, wait_time):

        original_pitch = self.pitch

        self.setPitch(62, speed = 0.3)

        moving, time_waited = False, 0

        while time_waited < wait_time:

            if not moving:
                moving = True
                self.wait(.2)
                self.agent_host.sendCommand('move .7')
                self.wait(.1)

            elif (self.block_in_view != 'dirt'):
                tree = (self.block_in_view in {'log', 'leaf'})

                if tree:
                    time_waited += self.wait(0.2)

                self.agent_host.sendCommand('move 0')

                if not tree:
                    time_waited += self.wait(0.2)

            else:
                time_waited += self.wait(0.2)

            self.observe(peek=True)

        self.setPitch(original_pitch, speed = 0.3)


    def setPitch(self, target_pitch, speed = 0.2):
        if self.pitch != target_pitch:
            orientation = (self.pitch > target_pitch)
            dir = -1 if (self.pitch > target_pitch) else 1 

            while orientation == (self.pitch > target_pitch):
                self.agent_host.sendCommand(f'pitch {dir * speed}')
                self.updatePos()

            self.agent_host.sendCommand('pitch 0')

    def wait(self, t):
        time.sleep(t)
        return t


    def updatePos(self, peeked = False):
        if not peeked:
            self.observe(peek = True)

        try: 
            if self.obs_dict[u'YPos'] == 2:
                self.reset()

            self.pos = [self.obs_dict[u'XPos'], self.obs_dict[u'ZPos']]
            self.pitch = self.obs_dict[u'Pitch']
            obs_yaw = self.obs_dict[u'Yaw']
            self.yaw = obs_yaw if obs_yaw > 0 else (360+obs_yaw)
        except BaseException:
            self.reset()


    def onTarget(self):
        if (self.block_in_view in {'log', 'leaves'}) or ((self.last_pitch != 0) and self.targetInDir(self.last_pitch, 'pitch')):
            return True
        
        return (5 <= self.yaw <= 85) and (self.last_turn != 0) and self.targetInDir(self.last_turn, 'turn')
        

    def targetInDir(self, last, move):
        dir = -1 if (last > 0) else 1
        found = self.visitAdjBlock(last, move, dir)
        
        if found:
            return True

        self.visitAdjBlock(last, move, (-1 *dir))
        return False


    def visitAdjBlock(self, last, move, dir):

        self.agent_host.sendCommand('attack 0')

        last = cursor = self.coord(self.getCursor(peeked=True))

        iterations = 0
        while (iterations <= 6) and (self.block_in_view not in {'log', 'leaves'}):
            if cursor == last:
                break

            if iterations == 0:
                time.sleep(.2)
                self.agent_host.sendCommand(f'{move} {dir * 0.4}' )

            iterations += 1
            last = cursor
            cursor = self.coord(self.getCursor())

        self.halt()

        return (self.block_in_view in {'log', 'leaves'})


    def coord(self, pos):
        if not pos:
            return None
        coordinate = []
        for p in pos:
            coordinate.append(self.roundDown(p))
        return coordinate

    
    def roundDown(self, num):
        if num < 0:
            num -= 1

        return int(num)


    def craftAxe(self):

        self.observe(peek=True)

        inventory = self.getInventory()
        # we edit an inventory dict instead of continually checking the inventory so that we can save time

        if (inventory['log'] >= 2):

            while inventory['planks'] < 5: # we'll have either 0, 3, 2, or 1 excess planks
                self.craftItem(inventory,'planks')
                time.sleep(0.1)

            while inventory['stick'] < 2: # we'll either have 2 excess sticks or no sticks
                self.craftItem(inventory,'stick')
                time.sleep(0.1)
                
            self.craftItem(inventory,'wooden_axe')
            time.sleep(0.1)
            self.equip('wooden_axe')
            self.axe = True

        return 0

    
    def craftItem(self, inventory, item):
        if item == 'wooden_axe':
            self.agent_host.sendCommand("craft wooden_axe")
            inventory['planks'] -= 3
            inventory['stick'] -= 2
            inventory['wooden_axe'] += 1
            
        elif item == 'stick':
            self.agent_host.sendCommand("craft stick")
            inventory['planks'] -= 2
            inventory['stick'] += 4

        elif item == 'planks':
            self.agent_host.sendCommand("craft planks")
            inventory['log'] -= 1
            inventory['planks'] += 4


    def equip(self, item_name):
        # FROM craft_work.py in Python_Examples (From the Malmo Download)

        self.observe(peek=True)

        try:
            self.equipped_item = ( self.obs_dict['InventorySlot_0_item'] == item_name )

            if (self.equipped_item != item_name) and (item_name in self.obs_dict.values()):
                for i in range(0,39):
                    key = 'InventorySlot_'+str(i)+'_item'

                    if (key in self.obs_dict.keys()) and (self.obs_dict[key] == item_name):
                        time.sleep(0.2)
                        self.agent_host.sendCommand(f"swapInventoryItems inventory:0 inventory:{i}")
                        time.sleep(0.2)
                        break

        except TypeError:
            pass
    
