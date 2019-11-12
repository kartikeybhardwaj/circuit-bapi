import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from database.user.user import DBUser
from database.milestone.milestone import DBMilestone

dbu = DBUser()
dbm = DBMilestone()

class GetMetaMilestonesResource:

    def idMapForMetaMilestoneIds(self, metaMilestones: "list of dict") -> "list of dict":
        idMap = {}
        # 01. get title and map it to _id from metaMilestones
        for metaMilestone in metaMilestones:
            idMap[metaMilestone["_id"]["$oid"]] = metaMilestone["title"]
        return idMap

    def idMapForUserIds(self, metaMilestones: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for metaMilestone in metaMilestones:
            if metaMilestone["meta"]["addedBy"]:
                allUserIds.append(metaMilestone["meta"]["addedBy"]["$oid"])
            if metaMilestone["meta"]["lastUpdatedBy"]:
                allUserIds.append(metaMilestone["meta"]["lastUpdatedBy"]["$oid"])
        # 02. a user can exist in different metaMilestones, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, metaMilestones: "list of dict") -> "list of dict":
        for metaMilestone in metaMilestones:
            metaMilestone["_id"] = metaMilestone["_id"]["$oid"]
            if metaMilestone["meta"]["addedBy"]:
                metaMilestone["meta"]["addedBy"] = metaMilestone["meta"]["addedBy"]["$oid"]
            if metaMilestone["meta"]["addedOn"]:
                metaMilestone["meta"]["addedOn"] = metaMilestone["meta"]["addedOn"]["$date"]
            if metaMilestone["meta"]["lastUpdatedBy"]:
                metaMilestone["meta"]["lastUpdatedBy"] = metaMilestone["meta"]["lastUpdatedBy"]["$oid"]
            if metaMilestone["meta"]["lastUpdatedOn"]:
                metaMilestone["meta"]["lastUpdatedOn"] = metaMilestone["meta"]["lastUpdatedOn"]["$date"]
        return metaMilestones

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
                # 01. get all meta milestones
                metaMilestones = dbm.getAllMetaMilestones()
                # 02. create idMap from idMapForMetaMilestoneIds
                idMap = self.idMapForMetaMilestoneIds(metaMilestones)
                # 03. update idMap from idMapForUserIds
                idMap.update(self.idMapForUserIds(metaMilestones))
                # 04. clean up mongo objects
                metaMilestones = self.convertMongoDBObjectsToObjects(metaMilestones)
                # 05. attach milestones in response
                responseObj["data"]["metaMilestones"] = metaMilestones
                # 06. attach idMap in response
                responseObj["data"]["idMap"] = idMap
                # 07. set responseId to success
                responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
