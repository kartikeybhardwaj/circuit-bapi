import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_pulses import validate_get_pulses_schema

from database.user.user import DBUser
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone
from database.pulse.pulse import DBPulse

dbu = DBUser()
dbpr = DBProject()
dbm = DBMilestone()
dbpu = DBPulse()

# check if milestoneId is valid ObjectId
# does this milestoneId exists
# is this milestoneId active
# check if projectId is valid ObjectId
# does this projectId exists
# is this projectId active
# is this milestoneId in this projectId
# verify access for user
### projectId - is publicly visible
### projectId - is internally visible, and user exists in project
### projectId - is privately visible, and projectId exists in user access
### is user superuser
# or, is userId superuser (fetch all active pulses)
# or, is public projectId (fetch all active pulses)
# or, is internal projectId, and user member (fetch all active pulses)
# or, is private projectId, and user's access to milestoneId (fetch active pulses only in user's access milestoneId)

class GetPulsesResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_pulses_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def validateMilestoneId(self, milestoneId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(milestoneId)
        except Exception as ex:
            success = False
            message = "Invalid milestoneId"
        if success:
            if dbm.countDocumentsById(milestoneId) != 1:
                success = False
                message = "Invalid milestoneId"
        return [success, message]

    def validateProjectId(self, projectId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(projectId)
        except Exception as ex:
            success = False
            message = "Invalid projectId"
        if success:
            if dbpr.countDocumentsById(projectId) != 1:
                success = False
                message = "Invalid projectId"
        return [success, message]

    def verifyAccess(self, milestoneId: str, projectId: str, userId: str) -> bool:
        success = False
        if (dbpr.isPubliclyVisible(projectId) or
            # or check for project public visibility
            dbpr.isInternalAndHasThisMember(projectId, userId) or
            # or check for project internal visibility and if user exist in project
            (dbpr.isPrivateAndHasThisMember(projectId, userId) and dbu.hasMilestoneAccess(userId, projectId, milestoneId)) or
            # or check for project private visibility and if user exist in project and if user access has milestoneId
            dbu.checkIfUserIsSuperuser(userId)):
            # or check for super user access
            success = True
        return success

    def getAllPulseIds(self, projectId: str, milestoneId: str) -> "list of str":
        return dbm.getPulsesList(projectId, milestoneId)

    def getLimitedPulseIds(self, projectId: str, milestoneId: str, userId: str) -> "list of str":
        return dbu.getAccessiblePulsesInMilestone(userId, projectId, milestoneId)

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
            pulse["pulseMetaId"] = pulse["pulseMetaId"]["$oid"] if pulse["pulseMetaId"] else None
            pulse["timeline"]["begin"] = pulse["timeline"]["begin"]["$date"]
            pulse["timeline"]["end"] = pulse["timeline"]["end"]["$date"]
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

    """
    REQUEST:
        projectId: str
        milestoneId: str
    """
    def on_get(self, req, resp):
        requestObj = req.params
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        # validate schema
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            # validate milestoneId
            afterValidationMilestoneId = self.validateMilestoneId(req.params["milestoneId"])
            if not afterValidationMilestoneId[0]:
                responseObj["responseId"] = 110
                responseObj["message"] = afterValidationMilestoneId[1]
            else:
                # validate projectId
                afterValidationProjectId = self.validateProjectId(req.params["projectId"])
                if not afterValidationProjectId[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationProjectId[1]
                elif not dbm.hasThisLinkedProjectId(req.params["projectId"], req.params["milestoneId"]):
                    # validate if milestoneId is in projectId
                    responseObj["responseId"] = 110
                    responseObj["message"] = "Invalid linkedProjectId"
                elif not self.verifyAccess(req.params["milestoneId"], req.params["projectId"], req.params["kartoon-fapi-incoming"]["_id"]):
                    # verify access for user
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    try:
                        pulseIds = []
                        # 01. check if user is superuser OR if projectId is public OR if projectId is internal having userId as member
                        if (dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]) or
                            dbpr.isPubliclyVisible(req.params["projectId"]) or
                            dbpr.isInternalAndHasThisMember(req.params["projectId"], req.params["kartoon-fapi-incoming"]["_id"])):
                            # 02. 01. if yes, fetch all active milestoneIds
                            pulseIds = self.getAllPulseIds(req.params["projectId"], req.params["milestoneId"])
                        else:
                            # 02. 02. if no, fetch limited milestoneIds
                            pulseIds = self.getLimitedPulseIds(req.params["projectId"], req.params["milestoneId"], req.params["kartoon-fapi-incoming"]["_id"])
                        # 03. get activePulses from pulseIds
                        pulses = dbpu.getPulsesByIds(pulseIds)
                        # 06. create idMap from idMapForPulseIds
                        idMap = self.idMapForPulseIds(pulses)
                        # 07. update idMap with idMapForUserIds
                        idMap.update(self.idMapForUserIds(pulses))
                        # 08. clean up mongo objects
                        pulses = self.convertMongoDBObjectsToObjects(pulses)
                        # 09. attach pulses in response
                        responseObj["data"]["pulses"] = pulses
                        # 10. attach idMap in response
                        responseObj["data"]["idMap"] = idMap
                        # 11. set responseId to success
                        responseObj["responseId"] = 211
                    except Exception as ex:
                        log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                        responseObj["message"] = str(ex)
        resp.media = responseObj
