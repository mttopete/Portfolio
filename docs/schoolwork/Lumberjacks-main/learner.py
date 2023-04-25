# Rllib docs: https://docs.ray.io/en/latest/rllib.html
# Malmo XML docs: https://docs.ray.io/en/latest/rllib.html

try:
    from malmo import MalmoPython
except:
    import MalmoPython

import sys
import time
import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint


import gym
from gym.spaces import Box
from setup import EndTrain

class Learner(gym.Env):

    def __init__(self, env_config):  
        # Static Parameters
        self.size = 50
        self.reward_density = .1 # not used?
        self.penalty_density = .02 # not used?
        self.obs_size = 21
        self.max_episode_steps = 600
        self.log_frequency = 10
        self.obs = None
        self.obs_dict = None
        self.episode_step = 0
        self.episode_return = 0
        self.returns = []
        self.steps = []
        self.episodes_per_train = env_config["episodes_per_train"]
        self.last_turn = 0
        self.last_pitch = 0

        # debugging
        '''
        self.get_obs_calls = 0
        self.go_total = 0
        self.s_total = 0
        self.obsconstructs = 0
        self.obs_c_total = 0
        '''

        # Rllib Parameters
        # actions: move, turn, attack, pitch, craft, build_bridge
        self.action_space = Box(low=np.array([-1, -1, -2, -1, -1]), high=np.array([1, 1, 2, 1, 1]), dtype=np.byte)
        self.observation_space = Box(0, 3, shape=(9 , self.obs_size , self.obs_size ), dtype=np.byte)
        self.episode_count = 0


        # Malmo Parameters
        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse( sys.argv )
        except RuntimeError as e:
            print(self.agent_host.getUsage())
            exit(1)


    def reset(self):
        """
        Resets the environment for the next episode.

        Returns
            observation: <np.array> flattened initial obseravtion
        """

        self.episode_count +=1

        # Reset Malmo
        world_state = self.init_malmo()

        # Reset Variables
        self.returns.append(self.episode_return)
        current_step = self.steps[-1] if len(self.steps) > 0 else 0
        self.steps.append(current_step + self.episode_step)
        self.episode_return = 0
        self.episode_step = 0
        self.get_obs_calls = 0

        # Log
        if len(self.returns) > self.log_frequency + 1 and \
            len(self.returns) % self.log_frequency == 0:
            self.log_returns()

        # Get Observation
        self.get_observation(world_state)
        return self.obs


    def step(self, action):
        self.checkEndTrain()
        """
        Take an action in the environment and return the results.

        Args
            action: <int> index of the action to take

        Returns
            observation: <np.array> flattened array of obseravtion
            reward: <int> reward from taking action
            done: <bool> indicates terminal state
            info: <dict> dictionary of extra information
        """

        reward = 0
        move = "{:.1f}".format(action[0])
        turn = "{:.1f}".format(action[1])
        self.last_turn = action[1]
        pitch = "{:.1f}".format(action[2] * 0.1)

        while not self.agent_host.getWorldState().has_mission_begun:
            time.sleep(0.1)

        self.agent_host.sendCommand(f'pitch {pitch}')
        self.agent_host.sendCommand(f'move {move}')
        self.agent_host.sendCommand(f'turn {turn}')
        time.sleep(.2)
            
        self.episode_step += 1

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
        
        if self.block_in_view == 'log':
            reward += 10
        elif self.block_in_view == 'leaves':
            reward += 3

        # self.printStep(move, turn, pitch, reward)
      
        return self.obs, reward, done, dict()
    
    
    def printStep(self, move, turn, pitch, reward, printing = True):
        s = ''

        if self.episode_step == 0:
            s += '\n\n_____________________________________________________________________\n'

        s += f' step '
        if self.episode_step <= 99:
            s += '0'
            if self.episode_step <= 9:
                s += '0'
        s += f'{self.episode_step} | move '

        if '-' not in move:
            s += ' '
        s += f'{move} | turn '

        if '-' not in turn:
            s += ' '
        s += f'{turn} | pitch '

        if '-' not in pitch:
            s += ' '
        s += f'{pitch} | reward {int(reward)} '

        if printing:
            print(s)

        return s


    def get_test_xml(self):
        has_dirt = []
        for x in range(-2,0):
            for y in range(-2,0):
                has_dirt.append((x,y))
        for x in range(0,2):
            for y in range(0,2):
                has_dirt.append((x,y))
        islands = ""
        trees = ""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                    <About>
                        <Summary>Chopping Trees</Summary>
                    </About>

                    <ServerSection>
                        <ServerInitialConditions>
                            <Time>
                                <StartTime>12000</StartTime>
                                <AllowPassageOfTime>false</AllowPassageOfTime>
                            </Time>
                            <Weather>clear</Weather>
                        </ServerInitialConditions>
                        <ServerHandlers>
                            <FlatWorldGenerator generatorString="3;7,1;1;"/>
                            <DrawingDecorator>''' + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='10' z1='{}' z2='{}' type='air'/>".format(-500, 500, -500, 500) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(-9, 7, 7, 7) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(-9, 7, -9, -9) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(7, 7, -9, 7) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(-9, -9, -9, 7) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(-2, 0, -2, 0) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='3' y2='10' z1='{}' z2='{}' type='air'/>".format(-1, 1, -1, 1) + \
                            islands + \
                            trees + \
                            '''</DrawingDecorator>
                            <ServerQuitWhenAnyAgentFinishes/>
                        </ServerHandlers>
                    </ServerSection>

                    <AgentSection mode="Survival">
                        <Name>Jack</Name>
                            <AgentStart>
                                <Placement x="0" y="5" z="0" pitch="30" yaw="0"/>
                                <Inventory>
                                    <InventoryItem slot="0" type="wooden_axe"/>
                                    <InventoryItem slot="1" type="log" quantity="3"/>
                                </Inventory>
                            </AgentStart>
                        <AgentHandlers>
                            <ContinuousMovementCommands/>
                            <SimpleCraftCommands/>
                            <InventoryCommands/>
                            <ObservationFromFullInventory/>
                            <ObservationFromFullStats/>
                            <ObservationFromRay/>
                            <ObservationFromGrid>
                                <Grid name="floorAll">
                                    <min x="-'''+str(int(self.obs_size/2))+'''" y="-1" z="-'''+str(int(self.obs_size/2))+'''"/>
                                    <max x="'''+str(int(self.obs_size/2))+'''" y="12" z="'''+str(int(self.obs_size/2))+'''"/>
                                </Grid>
                            </ObservationFromGrid>
                            <RewardForCollectingItem>
                                <Item reward="50" type="log" />
                                <Item reward="15" type ="wooden_axe" />
                            </RewardForCollectingItem>
                            <RewardForTouchingBlockType>
                                <Block reward="-100" type="stone" behaviour="onceOnly"/>
                            </RewardForTouchingBlockType>
                            <AgentQuitFromTouchingBlockType>
                                <Block type="stone" />
                            </AgentQuitFromTouchingBlockType>
                            <AgentQuitFromReachingCommandQuota total="'''+str(5*self.max_episode_steps)+'''" />
                        </AgentHandlers>
                    </AgentSection>
                </Mission>'''


    def get_mission_xml(self):
            has_dirt = []
            has_tree = []
            for x in range(-5,-3):
                for y in range(-5,-3):
                    has_dirt.append((x,y))
            for x in range(3,5):
                for y in range(3,5):
                    has_dirt.append((x,y))
            def island_locations():
                for a in range(-self.size,self.size):
                    for b in range(-self.size,self.size):
                        t = randint(1,120)
                        size = randint(5,10)
                        if t == 1:
                            for x in range(a,a+size):
                                for y in range(b,b+size):
                                    has_dirt.append((x,y))
                            yield "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(a, a+size, b, b+size)
            def tree_locations():
                for a in range(-self.size,self.size):
                    for b in range(-self.size,self.size):
                        t = randint(1,20)
                        if (0 >= t > 3) and ((a,b) in has_dirt) and ([(a-1,b-1),(a,b-1),(a-1,b),()] not in has_tree): #tall tree
                            has_tree.append((a,b))
                            yield f'''<DrawBlock x='{a}'  y='3' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='4' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b}' type='log' />
                                    <DrawBlock x='{a}'  y='7' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='8' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='7' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='7' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='7' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='7' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='7' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='7' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='7' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='7' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='8' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='8' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='8' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='8' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='8' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='8' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='8' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='8' z='{b+1}' type='leaves' />\n'''
                        elif (t == 3) and (a,b) in has_dirt: #mid tree
                            has_tree.append((a,b))
                            yield f'''<DrawBlock x='{a}'  y='3' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='4' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='7' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='5' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='5' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='5' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='5' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='5' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='5' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='7' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='7' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='7' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='7' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='7' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='7' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='7' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='7' z='{b+1}' type='leaves' />\n'''
                        elif (t == 4) and (a,b) in has_dirt: #low tree
                            has_tree.append((a,b))
                            yield f'''<DrawBlock x='{a}'  y='3' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='4' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b}' type='log' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='4' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='4' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='4' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='4' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='4' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='4' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='4' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='4' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='5' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='5' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='5' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='5' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='5' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='5' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='5' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b+1}' type='leaves' />\n
                                    <DrawBlock x='{a+1}'  y='6' z='{b-1}' type='leaves' />\n
                                    <DrawBlock x='{a-1}'  y='6' z='{b+1}' type='leaves' />\n'''
            islands = ""
            trees = ""
            for island in island_locations():
                islands += island
                islands += "\n"
            for tree in tree_locations():
                trees += tree
                trees += "\n"
            return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    
                        <About>
                            <Summary>Chopping Trees</Summary>
                        </About>
    
                        <ServerSection>
                            <ServerInitialConditions>
                                <Time>
                                    <StartTime>12000</StartTime>
                                    <AllowPassageOfTime>false</AllowPassageOfTime>
                                </Time>
                                <Weather>clear</Weather>
                            </ServerInitialConditions>
                            <ServerHandlers>
                                <FlatWorldGenerator generatorString="3;7,1;1;"/>
                                <DrawingDecorator>''' + \
                                "<DrawCuboid x1='{}' x2='{}' y1='2' y2='10' z1='{}' z2='{}' type='air'/>".format(-500, 500, -500, 500) + \
                                "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='dirt'/>".format(-5, 5, -5, 5) + \
                                "<DrawCuboid x1='{}' x2='{}' y1='3' y2='10' z1='{}' z2='{}' type='air'/>".format(-1, 1, -1, 1) + \
                                islands + \
                                trees + \
                                '''</DrawingDecorator>
                                <ServerQuitWhenAnyAgentFinishes/>
                            </ServerHandlers>
                        </ServerSection>
    
                        <AgentSection mode="Survival">
                            <Name>Jack</Name>
                                <AgentStart>
                                    <Placement x="0" y="5" z="0" pitch="30" yaw="0"/>
                                    <Inventory>
                                        <InventoryItem slot="0" type="wooden_axe"/>
                                    </Inventory>
                                </AgentStart>
                            <AgentHandlers>
                                <ContinuousMovementCommands/>
                                <SimpleCraftCommands/>
                                <InventoryCommands/>
                                <ObservationFromFullInventory/>
                                <ObservationFromFullStats/>
                                <ObservationFromRay/>
                                <ObservationFromGrid>
                                    <Grid name="floorAll">
                                        <min x="-'''+str(int(self.obs_size/2))+'''" y="-1" z="-'''+str(int(self.obs_size/2))+'''"/>
                                        <max x="'''+str(int(self.obs_size/2))+'''" y="12" z="'''+str(int(self.obs_size/2))+'''"/>
                                    </Grid>
                                </ObservationFromGrid>
                                <RewardForCollectingItem>
                                    <Item reward="50" type="log" />
                                    <Item reward="15" type ="wooden_axe" />
                                </RewardForCollectingItem>
                                <RewardForTouchingBlockType>
                                    <Block reward="-100" type="stone" behaviour="onceOnly"/>
                                </RewardForTouchingBlockType>
                                <AgentQuitFromTouchingBlockType>
                                    <Block type="stone" />
                                </AgentQuitFromTouchingBlockType>
                                <AgentQuitFromReachingCommandQuota total="'''+str(7*self.max_episode_steps)+'''" />
                            </AgentHandlers>
                        </AgentSection>
                    </Mission>'''

    def init_malmo(self):
        """
        Initialize new malmo mission.
        """
        my_mission = MalmoPython.MissionSpec(self.get_mission_xml(), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.setViewpoint(1)

        max_retries = 3
        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000)) # add Minecraft machines here as available

        for retry in range(max_retries):
            try:
                self.agent_host.startMission( my_mission, my_clients, my_mission_record, 0, 'Jack' )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)

        world_state = self.agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            for error in world_state.errors:
                if "commands connection is not open. Is the mission running?" not in error.text:
                    print("\nError:", error.text)

        return world_state


    def observe(self, peek = False):
        world_state = self.agent_host.getWorldState()

        self.get_observation(world_state, peek = peek)


    def get_observation(self, world_state, peek = False):
        #self.get_obs_calls += 1

        if not peek:
            self.obs = np.zeros((9 * self.obs_size * self.obs_size, ))
            #self.obsconstructs += 1

            
        self.block_in_view = ''
        self.obs_dict = ''
        
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                self.obs_dict = json.loads(msg)

                if not peek:

                    grid = self.obs_dict['floorAll']

                    for i, x in enumerate(grid):
                        if x == 'log':
                            self.obs[i] = 1
                        elif x == 'dirt' :
                            self.obs[i] = 2
                        elif x == 'leaves':
                            self.obs[i] = 3
                        elif x == 'planks':
                            self.obs[i] = 4

                    # Rotate observation with orientation of agent
                    self.obs = self.obs.reshape((9, self.obs_size, self.obs_size))
                    yaw = self.obs_dict['Yaw']

                    if yaw >= 225 and yaw < 315:
                        self.obs = np.rot90(self.obs, k=1, axes=(1, 2))
                    elif yaw >= 315 or yaw < 45:
                        self.obs = np.rot90(self.obs, k=2, axes=(1, 2))
                    elif yaw >= 45 and yaw < 135:
                        self.obs = np.rot90(self.obs, k=3, axes=(1, 2))
                    #obs = obs.flatten()
                                
                try:
                    if self.obs_dict['LineOfSight']['inRange']:
                        self.block_in_view = self.obs_dict['LineOfSight']['type']	
                except:
                    self.block_in_view = ''

                break

        if (not peek) and (self.obs_dict == ''):
            self.obs = self.obs.reshape((9, self.obs_size, self.obs_size))


    def log_returns(self):
        """
        Log the current returns as a graph and text file

        Args:
            steps (list): list of global steps after each episode
            returns (list): list of total return of each episode
        """
        box = np.ones(self.log_frequency) / self.log_frequency
        returns_smooth = np.convolve(self.returns[1:], box, mode='same')
        plt.clf()
        plt.plot(self.steps[1:], returns_smooth)
        plt.title('Jack')
        plt.ylabel('Return')
        plt.xlabel('Steps')
        plt.savefig('returns.png')

        with open('returns.txt', 'w') as f:
            for step, value in zip(self.steps[1:], self.returns[1:]):
                f.write("{}\t{}\n".format(step, value)) 

    
    def checkEndTrain(self):
        if (type(self.episodes_per_train) == int) and (self.episode_count > self.episodes_per_train):
            self.agent_host.sendCommand("quit")
            raise EndTrain()
