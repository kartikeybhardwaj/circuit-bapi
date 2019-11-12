import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from database.user.user import DBUser
from database.project.project import DBProject

dbu = DBUser()
dbpr = DBProject()

class GetMetaProjectsResource:

    def idMapForMetaProjectIds(self, metaProjects: "list of dict") -> "list of dict":
        idMap = {}
        # 01. get title and map it to _id from metaProjects
        for metaproject in metaProjects:
            idMap[metaproject["_id"]["$oid"]] = metaproject["title"]
        return idMap

    def idMapForUserIds(self, metaProjects: "list of dict") -> dict:
        idMap = {}
        # 01. prepare allUserIds
        allUserIds = []
        for metaProject in metaProjects:
            if metaProject["meta"]["addedBy"]:
                allUserIds.append(metaProject["meta"]["addedBy"]["$oid"])
            if metaProject["meta"]["lastUpdatedBy"]:
                allUserIds.append(metaProject["meta"]["lastUpdatedBy"]["$oid"])
        # 02. a user can exist in different metaProjects, get the set of allUserIds
        allUserIds = list(set(allUserIds))
        # 03. get [{_id, username}, ..] from getUsernamesMapByIds
        usernamesMapByIds = dbu.getUsernamesMapByIds(allUserIds)
        # 04. get username and map it to _id from usernamesMapByIds
        for usernamesMap in usernamesMapByIds:
            idMap[usernamesMap["_id"]["$oid"]] = usernamesMap["username"]
        return idMap

    def convertMongoDBObjectsToObjects(self, metaProjects: "list of dict") -> "list of dict":
        for metaProject in metaProjects:
            metaProject["_id"] = metaProject["_id"]["$oid"]
            if metaProject["meta"]["addedBy"]:
                metaProject["meta"]["addedBy"] = metaProject["meta"]["addedBy"]["$oid"]
            if metaProject["meta"]["addedOn"]:
                metaProject["meta"]["addedOn"] = metaProject["meta"]["addedOn"]["$date"]
            if metaProject["meta"]["lastUpdatedBy"]:
                metaProject["meta"]["lastUpdatedBy"] = metaProject["meta"]["lastUpdatedBy"]["$oid"]
            if metaProject["meta"]["lastUpdatedOn"]:
                metaProject["meta"]["lastUpdatedOn"] = metaProject["meta"]["lastUpdatedOn"]["$date"]
        return metaProjects

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
                # 01. get all meta projects
                metaProjects = dbpr.getAllMetaProjects()
                # 02. create idMap from idMapForMetaProjectIds
                idMap = self.idMapForMetaProjectIds(metaProjects)
                # 03. update idMap from idMapForUserIds
                idMap.update(self.idMapForUserIds(metaProjects))
                # 04. clean up mongo objects
                metaProjects = self.convertMongoDBObjectsToObjects(metaProjects)
                # 05. attach projects in response
                responseObj["data"]["metaProjects"] = metaProjects
                # 06. attach idMap in response
                responseObj["data"]["idMap"] = idMap
                # 07. set responseId to success
                responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
