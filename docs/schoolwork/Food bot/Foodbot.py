import requests
import json


KEY = "gSQL1rxlcXbKTLhNY1hmhOjIcB37DyR8"
location_parameters = {
    'key':KEY,
    'location':'' 
}
parameters = {
    'key':KEY,
    'sort':'distance',
    'q':'food',
    'location':''
   
}
dparams = {
    'key':KEY,
    'to':'',
    'from':''
    }
requestInfo = {
        'personal_location':'',
        'custom_location':'',
        'plc':''
}


gotPersonalLocation = False

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
#a quick function to change the base location of the user
def changeLocation():
    print("please enter your location. (ex) \"6461 Hogan Dr Sacramento, CA 95822\"  or \"123 disk drive\"")
    inp = input()
    while inp == '':
        inp = input()
    location_parameters['location'] = inp
    requestInfo['plc'] = location_parameters['location']
    location_response = requests.get("https://www.mapquestapi.com/geocoding/v1/address",params = location_parameters)
    loc = str(location_response.json()['results'][0]['locations'][0]['displayLatLng']['lng']) +','+ str(location_response.json()['results'][0]['locations'][0]['displayLatLng']['lat'])
    parameters['location'] = loc
    requestInfo['personal_location'] = loc
    print("To change your location again, enter CL or make a request with the desired location")
    print("(ex) \"burgers near 123 Demo Drive\"     to exit, enter \'exit\'\n")
    
def parseInput(inp):
    try:
        custom = False
        requestInfo['custom_location'] = ''
        words = inp.split()
        #if it is a single word, we just pass it as the query and make a search request
        if len(words) == 1:
            parameters['q'] = words[0]
        else:   #if it is more than a single word, we expect that to mean it has a structure close to
                # "food near me" or "coffee shops near 124 disk drive"
            for w in range(len(words)):
                if(words[w] in {'near','around'}):
                    custom = True
                    parameters['q'] = ''
                    for word in words[0:w]:
                        parameters['q'] += word
                        parameters['q'] += ' '
                    if words[w+1] == 'me':
                        parameters['location'] = requestInfo['personal_location']
                    else:
                        for word in words[w+1:]:
                            requestInfo['custom_location'] += word;
                            requestInfo['custom_location'] += ' '
                    break
                elif(words[w] in ['nearest','closest']):
                    custom = True
                    parameters['q'] = ''
                    for word in range(w,len(words)):
                        if words[word] in ['to','around','near']:
                            for p in words[w+1:word]:
                                parameters['q'] += p
                                parameters['q'] += ' '
                            if words[word+1] == 'me':
                                parameters['location'] = requestInfo['personal_location']
                            else:
                                for p in words[word+1:]:
                                    requestInfo['custom_location'] += p
                                    requestInfo['custom_location'] += ' '
                    if parameters['q'] == '':
                        for x in words[w+1:]:
                            parameters['q'] += x
                            parameters['q'] += ' '
                        parameters['location'] = requestInfo['personal_location']
                    break
        if custom == False:
            parameters['location'] = requestInfo['personal_location']
            parameters['q'] = inp
        makeRequest()
    except:
        print("Sorry, your input was either in an incorrect format or unable to be processed.")
                        

def makeRequest():
    try:
        if(requestInfo['custom_location'] != ''):
            location_parameters['location'] = requestInfo['custom_location']
            location_response = requests.get("https://www.mapquestapi.com/geocoding/v1/address",params = location_parameters)
            loc = str(location_response.json()['results'][0]['locations'][0]['displayLatLng']['lng']) +','+ str(location_response.json()['results'][0]['locations'][0]['displayLatLng']['lat'])
            parameters['location'] = loc
            requestInfo['custom_location'] = loc
        printResults(requests.get("https://www.mapquestapi.com/search/v4/place?",params = parameters))
    except:
        print("Sorry, your input was either in an incorrect format or unable to be processed.")
        
def printResults(response):
    try:
        re = response.json()['results']
        print("The closest \"",parameters['q'], "\" are:\n")
        num = 0
        for result in re:
            print(num,") ",result['displayString'])
            num += 1
            if num > 9:
                break
        print("")
        print("Would you like directions to your location? (y/n)")
        inp = input()
        while inp not in ['y','Y','yes','Yes','n','N','No','no']:
            inp = input()
        if inp in ['y','Y','yes','Yes']:
            print("Select a location: (0-9)")
            inp = input()
            while int(inp) < 0 or int(inp) > 9:
                inp = input()
            dparams['to'] = response.json()['results'][int(inp)]['displayString']
            dparams['from'] = requestInfo['plc']
            directions = requests.get("http://www.mapquestapi.com/directions/v2/route",params = dparams)
            for thing in directions.json()["route"]["legs"]:
                for x in thing["maneuvers"]:
                    print(x["narrative"])
            print()
    except:
        print("Sorry, your input was either in an incorrect format or unable to be processed.")


def main():
    isRunning = True
    print("Hello, i am Foodbot. To get started,")
    changeLocation()
    print("To make a request, simply enter the type of food or restaurant you are looking for (no punctuation)")
    while isRunning:
        print()
        print("What kind of food are you looking for today?")
        inp = input()
        if(inp in {'cl','CL','Cl','cL'}):
            changeLocation()
        elif(inp in {'exit','Exit'}):
            isRunning = False
            print("I hope i helped you find what you were looking for, have a nice day!")
        else:
            if(inp != ''):
                parseInput(inp)
  
main()
