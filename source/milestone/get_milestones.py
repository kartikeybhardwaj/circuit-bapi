import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_milestones import validate_get_milestones_schema

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
# verify access for user
### projectId - is publicly visible
### projectId - is internally visible, and user exists in project
### projectId - is privately visible, and projectId exists in user access
### is user superuser
# or, is userId superuser (fetch all active milestones)
# or, is public projectId (fetch all active milestones)
# or, is internal projectId, and user member (fetch all active milestones)
# or, is private projectId, and user's access to projectId (fetch active milestones only in user's access projectId)

class GetMilestonesResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_milestones_schema)
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

    def verifyAccess(self, projectId: str, userId: str) -> bool:
        success = False
        if (dbpr.isPubliclyVisible(projectId) or
            # or check for project public visibility
            dbpr.isInternalAndHasThisMember(projectId, userId) or
            # or check for project internal visibility and if user exist in project
            (dbpr.isPrivateAndHasThisMember(projectId, userId) and dbu.hasProjectAccess(userId, projectId)) or
            # or check for project private visibility and if user exist in project and if user access has projectId
            dbu.checkIfUserIsSuperuser(userId)):
            # or check for super user access
            success = True
        return success

    def getAllMilestoneIds(self, projectId: str) -> "list of str":
        return [mi["$oid"] for mi in dbpr.getAllMilestoneIds(projectId)]

    def getLimitedMilestoneIds(self, projectId: str, userId: str) -> "list of str":
        return [mi["milestoneId"]["$oid"] for mi in dbu.getAccessibleMilestonesInProject(userId, projectId)]

    def removeInactivePulses(self, milestones: "list of dict") -> "list of dict":
        # 01. prepare allPulseIds
        allPulseIds = []
        for milestone in milestones:
            for pulseId in milestone["pulsesList"]:
                allPulseIds.append(pulseId["$oid"])
        # 02. get only activePulseIds out of allPulseIds
        activePulses = dbpu.getActivePulseIdsByIds(allPulseIds)
        activePulseIds = [ap["_id"]["$oid"] for ap in activePulses]
        # 03. remove all inactive pulseIds
        for milestone in milestones:
            for pulseId in milestone["pulsesList"]:
                if pulseId["$oid"] not in activePulseIds:
                    milestone["pulsesList"].remove(pulseId)
        return milestones

    def idMapForMilestoneIds(self, milestones: "list of dict") -> dict:
        idMap = {}
        # 01. get title and map it to _id from milestones
        for milestone in milestones:
            idMap[milestone["_id"]["$oid"]] = milestone["title"]
        return idMap

    def idMapForPulseIds(self, milestones: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allPulseIds
        allPulseIds = []
        for milestone in milestones:
            for pulseId in milestone["pulsesList"]:
                allPulseIds.append(pulseId["$oid"])
        # 02. get [{_id, title}, ..] from getTitlesMapByIds
        titlesMapByIds = dbpu.getTitlesMapByIds(allPulseIds)
        # 03. get title and map it to _id from titlesMapByIds
        for titlesMap in titlesMapByIds:
            idMap[titlesMap["_id"]["$oid"]] = titlesMap["title"]
        return idMap

    def idMapForUserIds(self, milestones: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for milestone in milestones:
            if milestone["meta"]["addedBy"]:
                allUserIds.append(milestone["meta"]["addedBy"]["$oid"])
            if milestone["meta"]["lastUpdatedBy"]:
                allUserIds.append(milestone["meta"]["lastUpdatedBy"]["$oid"])
        # 02. a user can exist in different milestones, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, milestones: "list of dict") -> "list of dict":
        for milestone in milestones:
            milestone["_id"] = milestone["_id"]["$oid"]
            milestone["pulsesList"] = [pl["$oid"] for pl in milestone["pulsesList"]]
            milestone["milestoneMetaId"] = milestone["milestoneMetaId"]["$oid"]
            milestone["linkedProjectId"] = milestone["linkedProjectId"]["$oid"]
            if milestone["meta"]["addedBy"]:
                milestone["meta"]["addedBy"] = milestone["meta"]["addedBy"]["$oid"]
            if milestone["meta"]["addedOn"]:
                milestone["meta"]["addedOn"] = milestone["meta"]["addedOn"]["$date"]
            if milestone["meta"]["lastUpdatedBy"]:
                milestone["meta"]["lastUpdatedBy"] = milestone["meta"]["lastUpdatedBy"]["$oid"]
            if milestone["meta"]["lastUpdatedOn"]:
                milestone["meta"]["lastUpdatedOn"] = milestone["meta"]["lastUpdatedOn"]["$date"]
        return milestones

    """
    REQUEST:
        projectId: str
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
            elif not self.verifyAccess(req.params["projectId"], req.params["kartoon-fapi-incoming"]["_id"]):
                # verify access for user
                responseObj["responseId"] = 109
                responseObj["message"] = "Unauthorized access"
            else:
                try:
                    milestoneIds = []
                    # 01. check if user is superuser OR if projectId is public OR if projectId is internal having userId as member
                    if (dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]) or
                        dbpr.isPubliclyVisible(req.params["projectId"]) or
                        dbpr.isInternalAndHasThisMember(req.params["projectId"], req.params["kartoon-fapi-incoming"]["_id"])):
                        # 02. 01. if yes, fetch all active milestoneIds
                        milestoneIds = self.getAllMilestoneIds(req.params["projectId"])
                    else:
                        # 02. 02. if no, fetch limited milestoneIds
                        milestoneIds = self.getLimitedMilestoneIds(req.params["projectId"], req.params["kartoon-fapi-incoming"]["_id"])
                    # 03. get milestones from activeMilestoneIds
                    milestones = dbm.getMilestonesByIds(milestoneIds)
                    # 04. removeInactivePulses from milestones
                    milestones = self.removeInactivePulses(milestones)
                    # 05. ceate idMap from idMapForMilestoneIds
                    idMap = self.idMapForMilestoneIds(milestones)
                    # 06. update idMap with idMapForPulseIds
                    idMap.update(self.idMapForPulseIds(milestones))
                    # 07. update idMap with idMapForUserIds
                    idMap.update(self.idMapForUserIds(milestones))
                    # 08. clean up mongo objects
                    milestones = self.convertMongoDBObjectsToObjects(milestones)
                    # 09. attach milestones in response
                    responseObj["data"]["milestones"] = milestones
                    # 10. attach idMap in response
                    responseObj["data"]["idMap"] = idMap
                    # 11. set responseId to success
                    responseObj["responseId"] = 211
                except Exception as ex:
                    log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                    responseObj["message"] = str(ex)
        resp.media = responseObj
