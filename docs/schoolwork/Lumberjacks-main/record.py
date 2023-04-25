import MalmoPython
import os
import time
from lumberjacks import trainJack
from setup import findSaveLocation
from bridgeBuilder import BridgeBuilder
import tarfile
import shutil
from numpy.random import randint

def getLatestTar(tars):
    latest = None

    for file in tars:
        latest = file
    
    return latest

class recordJack(BridgeBuilder):

    def __init__(self, env_config):
        self.save_dir = findSaveLocation('video')
        self.latest_tar = self.save_dir + "/viewpoint.tgz"
        super().__init__(env_config)
    
    def extract(self):
        try:
            tar_file = tarfile.open(self.latest_tar)
        except FileNotFoundError:
            return

        tar_file.extractall(self.save_dir)
        tar_file.close()

        folder = [directory for directory in os.listdir(self.save_dir) if not directory.endswith('.tgz')][0]

        shutil.move(f"{self.save_dir}/{folder}/video.mp4", self.save_dir)

        os.chdir(f"{self.save_dir}")
        os.rename("video.mp4", f"video{self.episode_count}.mp4")
        os.chdir("..")
        os.chdir("..")

        shutil.rmtree(f"{self.save_dir}/{folder}")

    def init_malmo(self):
        self.extract()
        
        my_mission = MalmoPython.MissionSpec(self.get_mission_xml(), True)

        client_pool = MalmoPython.ClientPool()
        client_pool.add( MalmoPython.ClientInfo('127.0.0.1', 10000) )

        jack_recording_spec = MalmoPython.MissionRecordSpec()
        jack_recording_spec.setDestination(f"{self.save_dir}//viewpoint.tgz")
        jack_recording_spec.recordMP4(MalmoPython.FrameType.VIDEO, 24, 2000000, False)

        max_retries = 3

        for retry in range(max_retries):
            try:
                self.agent_host.startMission( my_mission, client_pool, jack_recording_spec, 0, 'Jack' )
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
                    t = randint(1,50)
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
                                
                                </Inventory>
                            </AgentStart>
                        <AgentHandlers>
                            <ContinuousMovementCommands/>
                            <VideoProducer>
                                <Width>1920</Width>
                                <Height>1080</Height>
                            </VideoProducer>
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

if __name__ == '__main__':
    training = True
    
    trainJack(training, recordJack)
