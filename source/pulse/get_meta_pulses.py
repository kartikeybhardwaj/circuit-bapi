from bson.objectid import ObjectId
import datetime

from database.user.user import DBUser
from database.pulse.pulse import DBPulse

dbu = DBUser()
dbpu = DBPulse()

class GetMetaPulsesResource:

    def idMapForMetaPulseIds(self, metaPulses: "list of dict") -> "list of dict":
        idMap = {}
        # 01. get title and map it to _id from metaPulses
        for metaPulse in metaPulses:
            idMap[metaPulse["_id"]["$oid"]] = metaPulse["title"]
        return idMap

    def idMapForUserIds(self, metaPulses: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for metaPulse in metaPulses:
            if metaPulse["meta"]["addedBy"]:
                allUserIds.append(metaPulse["meta"]["addedBy"]["$oid"])
            if metaPulse["meta"]["lastUpdatedBy"]:
                allUserIds.append(metaPulse["meta"]["lastUpdatedBy"]["$oid"])
        # 02. a user can exist in different metaPulses, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, metaPulses: "list of dict") -> "list of dict":
        for metaPulse in metaPulses:
            metaPulse["_id"] = metaPulse["_id"]["$oid"]
            if metaPulse["meta"]["addedBy"]:
                metaPulse["meta"]["addedBy"] = metaPulse["meta"]["addedBy"]["$oid"]
            if metaPulse["meta"]["addedOn"]:
                metaPulse["meta"]["addedOn"] = metaPulse["meta"]["addedOn"]["$date"]
            if metaPulse["meta"]["lastUpdatedBy"]:
                metaPulse["meta"]["lastUpdatedBy"] = metaPulse["meta"]["lastUpdatedBy"]["$oid"]
            if metaPulse["meta"]["lastUpdatedOn"]:
                metaPulse["meta"]["lastUpdatedOn"] = metaPulse["meta"]["lastUpdatedOn"]["$date"]
        return metaPulses

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            # check if this user exist and is active
            if not dbu.countDocumentsById(req.params["kartoon-fapi-incoming"]["_id"]) == 1:
                responseObj["responseId"] = 109
                responseObj["message"] = "Unauthorized access"
            else:
                # 01. get all meta pulses
                metaPulses = dbpu.getAllMetaPulses()
                # 02. create idMap from idMapForMetaPulseIds
                idMap = self.idMapForMetaPulseIds(metaPulses)
                # 03. update idMap from idMapForUserIds
                idMap.update(self.idMapForUserIds(metaPulses))
                # 04. clean up mongo objects
                metaPulses = self.convertMongoDBObjectsToObjects(metaPulses)
                # 05. attach pulses in response
                responseObj["data"]["metaPulses"] = metaPulses
                # 06. attach idMap in response
                responseObj["data"]["idMap"] = idMap
                # 07. set responseId to success
                responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
