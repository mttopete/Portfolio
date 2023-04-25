from pickle import UnpicklingError
import os

class EndTrain(Exception):
    pass

def findSaveLocation(dir):

    if (dir == 'video'):
        my_path = f"videos/session0"
        if not os.path.exists(f"videos"):
            os.mkdir(f"videos")
    else:
        my_path = f"{dir}0.txt"
        
    index = 0
    while os.path.exists(my_path):
        print('FINDSAVELOCATION LOOP')
        my_path = my_path.replace( str(index), str(index+1) )
        index += 1

    if (dir == 'video'):
        os.mkdir(my_path)

    return my_path

def validTrainTime(train_time):
    if train_time == '':
        return 'forever'
    elif train_time != '0' and train_time.isdigit():
        return int(train_time)
    return False
            
def getEpisodes():
    prompt = '\nHow many episodes will you train for? (1 episode = up to 100 steps)\nenter: run forever\n[int]: number '
    valid_answer = validTrainTime( input(prompt) )

    while not valid_answer:
        print('GETEPISODES LOOP')
        valid_answer = validTrainTime( input(prompt) )

    return valid_answer
        
def getDest(operation):
    prompt_dict = {
        "load": ["loaded from a previous point", "loaded from"],
        "save": ["saved", "stored in"]
    }

    prompt1 = f"Would you like this training session to be {prompt_dict[operation][0]}? [y/n]: "
    user_input = input("\n" + prompt1).lower()

    while user_input not in {'y', 'n'}:
        print('GETDEST LOOP')
        user_input = input("\nInvalid Input. " + prompt1).lower()

    if user_input == 'y':
        
        prompt2 = f"\nPICK {operation.upper()} LOCATION:\nenter: checkpoint.txt\n[0-9]: alternate checkpoint\nn: don't {operation} "
        user_input = input(prompt2).lower()
        valid_inputs = {'', 'n', 'y', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

        while not user_input in valid_inputs:
            print("Invalid input")
            user_input = input(prompt2).lower()

        if user_input == '':
            print(f"\nYour checkpoint will be {prompt_dict[operation][1]} checkpoint.txt")
            return 'checkpoint.txt'

        elif user_input.lower() == 'n':
            return False

        else:
            print(f"\nYour checkpoint will be {prompt_dict[operation][1]} checkpoint{user_input}.txt")
            return f'checkpoint{user_input}.txt'

    return False

def operate(dest, agent=None, path=None):
    if agent and dest:
        try:
            with open(dest, 'r') as checkpoint_file:
                checkpoint = checkpoint_file.read().replace('\\', '/')

                print(f"\nAttempting to load at: {dest}")
                agent.load_checkpoint(checkpoint)
                print("Load successful.")

        except (FileNotFoundError, EOFError, UnpicklingError) as e:
            print(f"LOAD FROM {dest} FAILED ({e})")

    elif path:
        try:
            with open(dest, 'w+') as checkpoint_file:
                print(f"\nAttempting to save at: {dest}")
                checkpoint_file.write(path)
                print("Save successful.")

        except (FileNotFoundError, EOFError) as e:
            print(f"SAVE TO {dest} FAILED ({e})")

def getCommands(training):
    if training:
        load_dest = getDest("load")
        save_dest = getDest("save")
        episodes = getEpisodes()

        return load_dest, save_dest, episodes
    else: 
        # just observing
        return False, False, 'forever'
        