import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from database.user.user import DBUser
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone

dbu = DBUser()
dbpr = DBProject()
dbm = DBMilestone()

class GetProjectsResource:

    def getAllProjectIds(self) -> "list of str":
        projectIds = [pi["_id"]["$oid"] for pi in dbpr.getAllProjectIds()]
        return projectIds

    def getLimitedProjectIds(self, userId: str) -> "list of str":
        # 01. fetch accessible projectIds from users collection
        accessibleProjects = dbu.getAccessibleProjects(userId)
        accessibleProjectIds = [api["projectId"]["$oid"] for api in accessibleProjects]
        # 02. fetch public projectIds
        publicProjects = dbpr.getPublicProjectIds()
        publicProjectIds = [ppi["_id"]["$oid"] for ppi in publicProjects]
        # 03. merge and get set of accessible and public projectIds
        projectIds = list(set(accessibleProjectIds + publicProjectIds))
        return projectIds

    def removeInactiveMilestones(self, projects: "list of dict") -> "list of dict":
        # 01. prepare allMilestoneIds
        allMilestoneIds = []
        for project in projects:
            for milestoneId in project["milestonesList"]:
                allMilestoneIds.append(milestoneId["$oid"])
        # 02. get only activeMilestoneIds out of allMilestoneIds
        activeMilestones = dbm.getActiveMilestoneIdsByIds(allMilestoneIds)
        activeMilestoneIds = [ami["_id"]["$oid"] for ami in activeMilestones]
        # 03. remove all inactive milestoneIds
        for project in projects:
            for milestoneId in project["milestonesList"]:
                if milestoneId["$oid"] not in activeMilestoneIds:
                    project["milestonesList"].remove(milestoneId)
        return projects

    def removeInactiveMembers(self, projects: "list of dict") -> "list of dict":
        # 01. prepare allMemberIds
        allMemberIds = []
        for project in projects:
            for member in project["members"]:
                allMemberIds.append(member["userId"]["$oid"])
        # 02. a member can exist in different projects, get the set of allMemberIds
        allMemberIds = list(set(allMemberIds))
        # 03. get only activeMemberIds out of allMemberIds
        activeMembers = dbu.getActiveUserIdsByIds(allMemberIds)
        activeMemberIds = [ami["_id"]["$oid"] for ami in activeMembers]
        # 04. remove all inactive memberIds
        for project in projects:
            for member in project["members"]:
                if member["userId"]["$oid"] not in activeMemberIds:
                    project["members"].remove(member)
        # NOTE: we'll be removing members from project if they're supposed to go inactive
        # thus, we need not to scan members individually for a project
        return projects

    def idMapForProjectIds(self, projects: "list of dict") -> dict:
        idMap = {}
        # 01. get title and map it to _id from projects
        for project in projects:
            idMap[project["_id"]["$oid"]] = project["title"]
        return idMap

    def idMapForMilestoneIds(self, projects: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allMilestoneIds
        allMilestoneIds = []
        for project in projects:
            for milestoneId in project["milestonesList"]:
                allMilestoneIds.append(milestoneId["$oid"])
        # 02. get [{_id, title}, ..] from getTitlesMapByIds
        titlesMapByIds = dbm.getTitlesMapByIds(allMilestoneIds)
        # 03. get title and map it to _id from titlesMapByIds
        for titlesMap in titlesMapByIds:
            idMap[titlesMap["_id"]["$oid"]] = titlesMap["title"]
        return idMap
    
    def idMapForUserIds(self, projects: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for project in projects:
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

    def convertMongoDBObjectsToObjects(self, projects: "list of dict") -> "list of dict":
        for project in projects:
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
        return projects

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            projectIds = []
            # 01. check if user is superuser
            if dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                # 02. 01. if yes, fetch all active projectIds
                projectIds = self.getAllProjectIds()
            else:
                # 02. 02. if no, fetch limited projectIds
                projectIds = self.getLimitedProjectIds(req.params["kartoon-fapi-incoming"]["_id"])
            # 03. fetch active projects from projectIds
            projects = dbpr.getProjectsByIds(projectIds)
            # 04. removeInactiveMilestones from projects
            projects = self.removeInactiveMilestones(projects)
            # 05. removeInactiveMembers from projects
            projects = self.removeInactiveMembers(projects)
            # 06. create idMap from idMapForProjectIds
            idMap = self.idMapForProjectIds(projects)
            # 07. update idMap with idMapForMilestoneIds
            idMap.update(self.idMapForMilestoneIds(projects))
            # 08. update idMap with idMapForUserIds
            idMap.update(self.idMapForUserIds(projects))
            # 09. clean up mongo objects
            projects = self.convertMongoDBObjectsToObjects(projects)
            # 10. attach projects in response
            responseObj["data"]["projects"] = projects
            # 11. attach idMap in response
            responseObj["data"]["idMap"] = idMap
            # 12. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
