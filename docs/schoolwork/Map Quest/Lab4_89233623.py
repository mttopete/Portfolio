import urllib.parse
import urllib.request
import json
class MapQuest():
    def __init__(self,apikey):
        self._key = apikey
        self._base = "http://open.mapquestapi.com/directions/v2/route?"
    def build(self,mats):
        if len(mats) <= 1:
            return ""
        parameters = [("key",self._key)]
        parameters.append(("from",mats[0]))
        for stop in mats[1:]:
            parameters.append(("to",stop))
        return self._base + urllib.parse.urlencode(parameters)
    def load_directions(self,url):
        response = None
        try:  
            response = urllib.request.urlopen(url)
            return json.load(response)
        finally:
            if response != None:
                response.close()
    def directions(self,loclist):
        directs = []
        if len(loclist) <=1 :
            return ""
        url = self.build(loclist)
        doc = self.load_directions(url)
        for thing in doc["route"]["legs"]:
            for x in thing["maneuvers"]:
                directs.append(x["narrative"])
        retstr = ""
        for direction in directs:
            retstr = retstr + direction +"\n"
        return retstr   
    def totalDistance(self,loclist):
        dist = 0
        if len(loclist) <= 1:
            return 0
        url = self.build(loclist)
        doc = self.load_directions(url)
        for stop in doc["route"]["legs"]:
            dist += stop["distance"]
        return dist
    def totalTime(self,loclist):
        times = 0
        if len(loclist) <= 1:
            return 0
        url = self.build(loclist)
        doc = self.load_directions(url)
        for stop in doc["route"]["legs"]:
            times += stop["time"]
        return times
    def pointOfInterest(self,locations: str, keyword: str, reslim:int):
        urlbase = "http://www.mapquestapi.com/geocoding/v1/address?"
        urlenc = urlbase + urllib.parse.urlencode([("key",self._key),("location",locations)])
        coords = self.load_directions(urlenc)
        lat = float(coords["results"][0]["locations"][0]["latLng"]["lat"])
        lon = float(coords["results"][0]["locations"][0]["latLng"]["lng"])
        things = "https://www.mapquestapi.com/search/v4/place?"
        things = things + urllib.parse.urlencode([("key","mNbMj74GIaV9TJHDG720KFOYkkdGEDvV"),("sort","distance"),("q",keyword)]) + "&location="+str(lon)+"%2C"+str(lat)
        testsss = self.load_directions(things)
        reslist = []
        for x in testsss["results"]:
            reslist.append(x["displayString"])
        retlist = []
        m = 0
        while len(retlist) < reslim:
            retlist.append(reslist[m])
            m += 1
        return retlist