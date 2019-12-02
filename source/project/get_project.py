import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_project import validate_get_project_schema

from database.user.user import DBUser
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone

dbu = DBUser()
dbpr = DBProject()
dbm = DBMilestone()

# check if projectId is valid ObjectId
# does this projectId exists
# is this projectId active
# verify access for user
# or, is userId superuser (fetch this project)
# or, is public projectId (fetch this project)
# or, is internal projectId, and user member (fetch this project)
# or, is private projectId, and user's access to projectId (fetch this project only in user's access projectId)

class GetProjectResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_project_schema)
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

    def removeInactiveMilestones(self, project: dict) -> dict:
        # 01. prepare allMilestoneIds
        allMilestoneIds = []
        for milestoneId in project["milestonesList"]:
            allMilestoneIds.append(milestoneId["$oid"])
        # 02. get only activeMilestoneIds out of allMilestoneIds
        activeMilestones = dbm.getActiveMilestoneIdsByIds(allMilestoneIds)
        activeMilestoneIds = [ami["_id"]["$oid"] for ami in activeMilestones]
        # 03. remove all inactive milestoneIds
        for milestoneId in project["milestonesList"]:
            if milestoneId["$oid"] not in activeMilestoneIds:
                project["milestonesList"].remove(milestoneId)
        return project

    def removeInactiveMembers(self, project: dict) -> dict:
        # 01. prepare allMemberIds
        allMemberIds = []
        for member in project["members"]:
            allMemberIds.append(member["userId"]["$oid"])
        # 02. a member can exist in different projects, get the set of allMemberIds
        allMemberIds = list(set(allMemberIds))
        # 03. get only activeMemberIds out of allMemberIds
        activeMembers = dbu.getActiveUserIdsByIds(allMemberIds)
        activeMemberIds = [ami["_id"]["$oid"] for ami in activeMembers]
        # 04. remove all inactive memberIds
        for member in project["members"]:
            if member["userId"]["$oid"] not in activeMemberIds:
                project["members"].remove(member)
        # NOTE: we'll be removing members from project if they're supposed to go inactive
        # thus, we need not to scan members individually for a project
        return project

    def idMapForProjectId(self, project: dict) -> dict:
        idMap = {}
        # 01. get title and map it to _id from project
        idMap[project["_id"]["$oid"]] = project["title"]
        return idMap

    def idMapForMilestoneIds(self, project: dict) -> dict:
        idMap = {}
        # 01. prepare allMilestoneIds
        allMilestoneIds = []
        for milestoneId in project["milestonesList"]:
            allMilestoneIds.append(milestoneId["$oid"])
        # 02. get [{_id, title}, ..] from getTitlesMapByIds
        titlesMapByIds = dbm.getTitlesMapByIds(allMilestoneIds)
        # 03. get title and map it to _id from titlesMapByIds
        for titlesMap in titlesMapByIds:
            idMap[titlesMap["_id"]["$oid"]] = titlesMap["title"]
        return idMap

    def idMapForUserIds(self, project: dict) -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for member in project["members"]:
            allUserIds.append(member["userId"]["$oid"])
        if project["meta"]["addedBy"]:
            allUserIds.append(project["meta"]["addedBy"]["$oid"])
        if project["meta"]["lastUpdatedBy"]:
            allUserIds.append(project["meta"]["lastUpdatedBy"]["$oid"])
        # 02. a user can exist in different projects, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, project: dict) -> dict:
        project["_id"] = project["_id"]["$oid"]
        project["milestonesList"] = [ml["$oid"] for ml in project["milestonesList"]]
        for member in project["members"]:
            member["userId"] = member["userId"]["$oid"]
            member["roleId"] = member["roleId"]["$oid"]
        project["projectMetaId"] = project["projectMetaId"]["$oid"]
        if project["meta"]["addedBy"]:
            project["meta"]["addedBy"] = project["meta"]["addedBy"]["$oid"]
        if project["meta"]["addedOn"]:
            project["meta"]["addedOn"] = project["meta"]["addedOn"]["$date"]
        if project["meta"]["lastUpdatedBy"]:
            project["meta"]["lastUpdatedBy"] = project["meta"]["lastUpdatedBy"]["$oid"]
        if project["meta"]["lastUpdatedOn"]:
            project["meta"]["lastUpdatedOn"] = project["meta"]["lastUpdatedOn"]["$date"]
        return project

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
            else:
                try:
                    projectId = req.params["projectId"]
                    # 01. get project from activeProjectId
                    project = dbpr.getProjectById(projectId)
                    # 04. removeInactiveMilestones from project
                    project = self.removeInactiveMilestones(project)
                    # 05. removeInactiveMembers from project
                    project = self.removeInactiveMembers(project)
                    # 06. create idMap from idMapForProjectId
                    idMap = self.idMapForProjectId(project)
                    # 07. update idMap with idMapForMilestoneIds
                    idMap.update(self.idMapForMilestoneIds(project))
                    # 08. update idMap with idMapForUserIds
                    idMap.update(self.idMapForUserIds(project))
                    # 09. clean up mongo objects
                    project = self.convertMongoDBObjectsToObjects(project)
                    # 10. attach project in response
                    responseObj["data"]["project"] = project
                    # 11. attach idMap in response
                    responseObj["data"]["idMap"] = idMap
                    # 12. set responseId to success
                    responseObj["responseId"] = 211
                except Exception as ex:
                    log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                    responseObj["message"] = str(ex)
        resp.media = responseObj
