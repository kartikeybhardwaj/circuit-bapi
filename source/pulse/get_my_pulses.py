import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from database.user.user import DBUser
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone
from database.pulse.pulse import DBPulse

dbu = DBUser()
dbpr = DBProject()
dbm = DBMilestone()
dbpu = DBPulse()

# fetch active pulses only in user's access projectId

class GetMyPulsesResource:

    def getLimitedPulseIdsForUser(self, userId: str) -> list:
        return dbu.getAccessibleUserPulses(userId)

    def idMapForPulseIds(self, pulses: "list of dict") -> dict:
        idMap = {}
        # 01. get title and map it to _id from pulses
        for pulse in pulses:
            idMap[pulse["_id"]["$oid"]] = pulse["title"]
        return idMap

    def idMapForUserIds(self, pulses: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for pulse in pulses:
            if pulse["meta"]["addedBy"]:
                allUserIds.append(pulse["meta"]["addedBy"]["$oid"])
            if pulse["meta"]["lastUpdatedBy"]:
                allUserIds.append(pulse["meta"]["lastUpdatedBy"]["$oid"])
            for assignee in pulse["assignees"]:
                allUserIds.append(assignee["$oid"])
            for comment in pulse["comments"]:
                allUserIds.append(comment["meta"]["addedBy"])
        # 02. a user can exist in different pulses, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, pulses: "list of dict") -> "list of dict":
        for pulse in pulses:
            pulse["_id"] = pulse["_id"]["$oid"]
            pulse["pulseMetaId"] = pulse["pulseMetaId"]["$oid"]
            pulse["linkedProjectId"] = pulse["linkedProjectId"]["$oid"]
            pulse["linkedMilestoneId"] = pulse["linkedMilestoneId"]["$oid"]
            pulse["assignees"] = [assignee["$oid"] for assignee in pulse["assignees"]]
            for comment in pulse["comments"]:
                comment["meta"]["addedBy"] = comment["meta"]["addedBy"]["$oid"]
                comment["meta"]["addedOn"] = comment["meta"]["addedOn"]["$date"]
            if pulse["meta"]["addedBy"]:
                pulse["meta"]["addedBy"] = pulse["meta"]["addedBy"]["$oid"]
            if pulse["meta"]["addedOn"]:
                pulse["meta"]["addedOn"] = pulse["meta"]["addedOn"]["$date"]
            if pulse["meta"]["lastUpdatedBy"]:
                pulse["meta"]["lastUpdatedBy"] = pulse["meta"]["lastUpdatedBy"]["$oid"]
            if pulse["meta"]["lastUpdatedOn"]:
                pulse["meta"]["lastUpdatedOn"] = pulse["meta"]["lastUpdatedOn"]["$date"]
        return pulses

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            # 01. get user accessible pulses
            pulseIds = self.getLimitedPulseIdsForUser(req.params["kartoon-fapi-incoming"]["_id"])
            # 02. get activePulses from pulseIds
            pulses = dbpu.getPulsesByIds(pulseIds)
            # 03. create idMap from idMapForPulseIds
            idMap = self.idMapForPulseIds(pulses)
            # 04. update idMap with idMapForUserIds
            idMap.update(self.idMapForUserIds(pulses))
            # 05. clean up mongo objects
            pulses = self.convertMongoDBObjectsToObjects(pulses)
            # 06. attach pulses in response
            responseObj["data"]["pulses"] = pulses
            # 07. attach idMap in response
            responseObj["data"]["idMap"] = idMap
            # 08. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
