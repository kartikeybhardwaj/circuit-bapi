import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_milestone import validate_get_milestone_schema

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
# verify access for user
# or, is userId superuser (fetch this milestone)
# or, is public projectId (fetch this milestone)
# or, is internal projectId, and user member (fetch this milestone)
# or, is private projectId, and user's access to projectId (fetch this milestone only in user's access projectId)

class GetMilestoneResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_milestone_schema)
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

    def verifyAccess(self, milestoneId: str, projectId: str, userId: str) -> bool:
        success = False
        if (dbpr.isPubliclyVisible(projectId) or
            # or check for project public visibility
            dbpr.isInternalAndHasThisMember(projectId, userId) or
            # or check for project internal visibility and if user exist in project
            (dbpr.isPrivateAndHasThisMember(projectId, userId) and dbu.hasMilestoneAccess(userId, projectId, milestoneId)) or
            # or check for project private visibility and if user exist in project and if user access has projectId
            dbu.checkIfUserIsSuperuser(userId)):
            # or check for super user access
            success = True
        return success

    def removeInactivePulses(self, milestone: dict) -> dict:
        # 01. prepare allPulseIds
        allPulseIds = []
        for pulseId in milestone["pulsesList"]:
            allPulseIds.append(pulseId["$oid"])
        # 02. get only activePulseIds out of allPulseIds
        activePulses = dbpu.getActivePulseIdsByIds(allPulseIds)
        activePulseIds = [ap["_id"]["$oid"] for ap in activePulses]
        # 03. remove all inactive pulseIds
        for pulseId in milestone["pulsesList"]:
            if pulseId["$oid"] not in activePulseIds:
                milestone["pulsesList"].remove(pulseId)
        return milestone

    def idMapForMilestoneId(self, milestone: dict) -> dict:
        idMap = {}
        # 01. get title and map it to _id from milestone
        idMap[milestone["_id"]["$oid"]] = milestone["title"]
        return idMap

    def idMapForPulseIds(self, milestone: dict) -> dict:
        idMap = {}
        # 01. prepare allPulseIds
        allPulseIds = []
        for pulseId in milestone["pulsesList"]:
            allPulseIds.append(pulseId["$oid"])
        # 02. get [{_id, title}, ..] from getTitlesMapByIds
        titlesMapByIds = dbpu.getTitlesMapByIds(allPulseIds)
        # 03. get title and map it to _id from titlesMapByIds
        for titlesMap in titlesMapByIds:
            idMap[titlesMap["_id"]["$oid"]] = titlesMap["title"]
        return idMap

    def idMapForUserIds(self, milestone: dict) -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        if milestone["meta"]["addedBy"]:
            allUserIds.append(milestone["meta"]["addedBy"]["$oid"])
        if milestone["meta"]["lastUpdatedBy"]:
            allUserIds.append(milestone["meta"]["lastUpdatedBy"]["$oid"])
        # 02. get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, milestone: dict) -> dict:
        milestone["_id"] = milestone["_id"]["$oid"]
        milestone["pulsesList"] = [pl["$oid"] for pl in milestone["pulsesList"]]
        if milestone["milestoneMetaId"]:
            milestone["milestoneMetaId"] = milestone["milestoneMetaId"]["$oid"]
        milestone["locationId"] = milestone["locationId"]["$oid"]
        milestone["linkedProjectId"] = milestone["linkedProjectId"]["$oid"]
        milestone["timeline"]["begin"] = milestone["timeline"]["begin"]["$date"]
        milestone["timeline"]["end"] = milestone["timeline"]["end"]["$date"]
        if milestone["meta"]["addedBy"]:
            milestone["meta"]["addedBy"] = milestone["meta"]["addedBy"]["$oid"]
        if milestone["meta"]["addedOn"]:
            milestone["meta"]["addedOn"] = milestone["meta"]["addedOn"]["$date"]
        if milestone["meta"]["lastUpdatedBy"]:
            milestone["meta"]["lastUpdatedBy"] = milestone["meta"]["lastUpdatedBy"]["$oid"]
        if milestone["meta"]["lastUpdatedOn"]:
            milestone["meta"]["lastUpdatedOn"] = milestone["meta"]["lastUpdatedOn"]["$date"]
        return milestone

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
                        milestoneId = req.params["milestoneId"]
                        # 01. get milestone from activeMilestoneId
                        milestone = dbm.getMilestoneById(milestoneId)
                        # 02. removeInactivePulses from milestone
                        milestone = self.removeInactivePulses(milestone)
                        # 03. ceate idMap from idMapForMilestoneId
                        idMap = self.idMapForMilestoneId(milestone)
                        # 04. update idMap with idMapForPulseIds
                        idMap.update(self.idMapForPulseIds(milestone))
                        # 05. update idMap with idMapForUserIds
                        idMap.update(self.idMapForUserIds(milestone))
                        # 06. clean up mongo objects
                        milestone = self.convertMongoDBObjectsToObjects(milestone)
                        # 07. attach milestone in response
                        responseObj["data"]["milestone"] = milestone
                        # 08. attach idMap in response
                        responseObj["data"]["idMap"] = idMap
                        # 09. set responseId to success
                        responseObj["responseId"] = 211
                    except Exception as ex:
                        log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                        responseObj["message"] = str(ex)
        resp.media = responseObj
