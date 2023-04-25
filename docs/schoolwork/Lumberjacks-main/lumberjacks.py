import ray
from ray.rllib.agents import sac
from setup import getCommands, operate, EndTrain, findSaveLocation
from bridgeBuilder import BridgeBuilder
import os

def trainJack(training, environment):
    ray.init()
    load_dest, save_dest, episodes = getCommands(training)

    trainer = sac.SACTrainer(env=environment, config={
        'env_config': {"episodes_per_train": episodes}, 
        'framework': 'torch',       # Use pyotrch instead of tensorflow
        'num_gpus': 0,              # We aren't using GPUs
        'num_workers': 0,            # We aren't using parallelism
        'model' : {"conv_filters": [ [64, [5, 5], 64], [32, [5, 1], 32], [32, [1, 5], 32], [32, [1, 1], 1] ]},
    })

    operate(load_dest, agent=trainer)
    print()

    no_error = True
    
    try:
        trainer.train()
        while (type(episodes) == str) and (episodes == 'forever'):
            # train forever when the user wants to
            trainer.train()
        
    except (EndTrain, KeyboardInterrupt):
        pass

    except BaseException as e:
        print(e)
        print("UNEXPECTED ERROR")

        no_error = False

        if save_dest: 
            # if an uenexpected error occurs and we wanted to save, 
            # it's best that we save somehere else
            # and not overwrite any other saves
            save_dest = findSaveLocation('checkpoint')

    if no_error:
        print("TRAINING FINISHED")
    
    if save_dest:
        checkpoint_path = trainer.save()
        operate(save_dest, path=checkpoint_path.replace('\\', '/'))


if __name__ == '__main__':
    training = False
    
    trainJack(training, BridgeBuilder)
    
