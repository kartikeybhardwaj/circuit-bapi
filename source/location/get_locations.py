import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from database.location.location import DBLocation
from database.user.user import DBUser

dbl = DBLocation()
dbu = DBUser()

class GetLocationsResource():

    def idMapForLocationIds(self, locations: "list of dict") -> dict:
        idMap = {}
        # 01. get city and country and map it to _id from locations
        for location in locations:
            idMap[location["_id"]["$oid"]] = [
                location["city"],
                location["country"]
            ]
        return idMap

    def idMapForUserIds(self, locations: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for location in locations:
            if location["meta"]["addedBy"]:
                allUserIds.append(location["meta"]["addedBy"]["$oid"])
            if location["meta"]["lastUpdatedBy"]:
                allUserIds.append(location["meta"]["lastUpdatedBy"]["$oid"])
        # 02. a user can exist in different locations, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, locations: "list of dict") -> "list of dict":
        for location in locations:
            location["_id"] = location["_id"]["$oid"]
            if location["meta"]["addedBy"]:
                location["meta"]["addedBy"] = location["meta"]["addedBy"]["$oid"]
            if location["meta"]["addedOn"]:
                location["meta"]["addedOn"] = location["meta"]["addedOn"]["$date"]
            if location["meta"]["lastUpdatedBy"]:
                location["meta"]["lastUpdatedBy"] = location["meta"]["lastUpdatedBy"]["$oid"]
            if location["meta"]["lastUpdatedOn"]:
                location["meta"]["lastUpdatedOn"] = location["meta"]["lastUpdatedOn"]["$date"]
        return locations

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            # 01. fetch all locations
            locations = dbl.getAllLocations()
            # 02. create idMap from idMapForLocationIds
            idMap = self.idMapForLocationIds(locations)
            # 03. update idMap with idMapForUserIds
            idMap.update(self.idMapForUserIds(locations))
            # 04. clean up mongo objects
            locations = self.convertMongoDBObjectsToObjects(locations)
            # 05. attach locations in response
            responseObj["data"]["locations"] = locations
            # 06. attach idMap in response
            responseObj["data"]["idMap"] = idMap
            # 07. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
