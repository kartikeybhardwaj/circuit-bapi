import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_pulse import validate_get_pulse_schema

from database.user.user import DBUser
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone
from database.pulse.pulse import DBPulse

dbu = DBUser()
dbpr = DBProject()
dbm = DBMilestone()
dbpu = DBPulse()

# check if projectId is valid ObjectId
# does this projectId exists
# is this projectId active
# check if milestoneId is valid ObjectId
# does this milestoneId exists
# is this milestoneId active
# check if pulseId is valid ObjectId
# does this pulseId exists
# is this pulseId active
# verify access for user
# or, is userId superuser (fetch this pulse)
# or, is public projectId (fetch this pulse)
# or, is internal projectId, and user member (fetch this pulse)
# or, is private projectId, and user's access to projectId (fetch this pulse only in user's access projectId)

class GetPulseResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_pulse_schema)
            success = True
        except Exception as ex:
            message = ex.message
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

    def validatePulseId(self, pulseId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(pulseId)
        except Exception as ex:
            success = False
            message = "Invalid pulseId"
        if success:
            if dbpu.countDocumentsById(pulseId) != 1:
                success = False
                message = "Invalid pulseId"
        return [success, message]

    def verifyAccess(self, pulseId: str, milestoneId: str, projectId: str, userId: str) -> bool:
        success = False
        if (dbpr.isPubliclyVisible(projectId) or
            # or check for project public visibility
            dbpr.isInternalAndHasThisMember(projectId, userId) or
            # or check for project internal visibility and if user exist in project
            (dbpr.isPrivateAndHasThisMember(projectId, userId) and dbu.hasPulseAccess(userId, projectId, milestoneId, pulseId)) or
            # or check for project private visibility and if user exist in project and if user access has milestoneId
            dbu.checkIfUserIsSuperuser(userId)):
            # or check for super user access
            success = True
        return success

    def idMapForPulseId(self, pulse: dict) -> dict:
        idMap = {}
        # 01. get title and map it to _id from pulse
        idMap[pulse["_id"]["$oid"]] = pulse["title"]
        return idMap

    def idMapForUserIds(self, pulse: dict) -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
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

    def convertMongoDBObjectsToObjects(self, pulse: dict) -> "list of dict":
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
        return pulse

    """
    REQUEST:
        projectId: str
        milestoneId: str
        pulseId: str
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
            # validate projectId
            afterValidationProjectId = self.validateProjectId(req.params["projectId"])
            if not afterValidationProjectId[0]:
                responseObj["responseId"] = 110
                responseObj["message"] = afterValidationProjectId[1]
            else:
                # validate milestoneId
                afterValidationMilestoneId = self.validateMilestoneId(req.params["milestoneId"])
                if not afterValidationMilestoneId[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationMilestoneId[1]
                else:
                    # validate pulseId
                    afterValidationPulseId = self.validatePulseId(req.params["pulseId"])
                    if not afterValidationPulseId[0]:
                        responseObj["responseId"] = 110
                        responseObj["message"] = afterValidationPulseId[1]
                    elif not dbpu.hasThisLinkedMilestoneId(req.params["milestoneId"], req.params["pulseId"]):
                        # validate if pulseId is in milestoneId
                        responseObj["responseId"] = 110
                        responseObj["message"] = "Invalid linkedMilestoneId"
                    elif not dbm.hasThisLinkedProjectId(req.params["projectId"], req.params["milestoneId"]):
                        # validate if milestoneId is in projectId
                        responseObj["responseId"] = 110
                        responseObj["message"] = "Invalid linkedProjectId"
                    elif not self.verifyAccess(req.params["pulseId"], req.params["milestoneId"], req.params["projectId"], req.params["kartoon-fapi-incoming"]["_id"]):
                        # verify access for user
                        responseObj["responseId"] = 109
                        responseObj["message"] = "Unauthorized access"
                    else:
                        try:
                            pulseId = req.params["pulseId"]
                            # 01. get activePulse from pulseId
                            pulse = dbpu.getPulseById(pulseId)
                            # 02. create idMap from idMapForPulseId
                            idMap = self.idMapForPulseId(pulse)
                            # 03. update idMap with idMapForUserIds
                            idMap.update(self.idMapForUserIds(pulse))
                            # 04. clean up mongo objects
                            pulse = self.convertMongoDBObjectsToObjects(pulse)
                            # 05. attach pulse in response
                            responseObj["data"]["pulse"] = pulse
                            # 06. attach idMap in response
                            responseObj["data"]["idMap"] = idMap
                            # 07. set responseId to success
                            responseObj["responseId"] = 211
                        except Exception as ex:
                            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                            responseObj["message"] = str(ex)
        resp.media = responseObj
