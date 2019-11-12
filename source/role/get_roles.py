import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from database.role.role import DBRole

dbr = DBRole()

class GetRolesResource():

    def idMapForRoleIds(self, roles: "list of dict") -> dict:
        idMap = {}
        # 01. get title and map it to _id from roles
        for role in roles:
            idMap[role["_id"]["$oid"]] = role["title"]
        return idMap

    def convertMongoDBObjectsToObjects(self, roles: "list of dict") -> "list of dict":
        for role in roles:
            role["_id"] = role["_id"]["$oid"]
            if role["meta"]["addedBy"]:
                role["meta"]["addedBy"] = role["meta"]["addedBy"]["$oid"]
            if role["meta"]["addedOn"]:
                role["meta"]["addedOn"] = role["meta"]["addedOn"]["$date"]
            if role["meta"]["lastUpdatedBy"]:
                role["meta"]["lastUpdatedBy"] = role["meta"]["lastUpdatedBy"]["$oid"]
            if role["meta"]["lastUpdatedOn"]:
                role["meta"]["lastUpdatedOn"] = role["meta"]["lastUpdatedOn"]["$date"]
        return roles

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            # 01. fetch all roles
            roles = dbr.getAllRoles()
            # 02. create idMap from idMapForRoleIds
            idMap = self.idMapForRoleIds(roles)
            # 03. clean up mongo objects
            roles = self.convertMongoDBObjectsToObjects(roles)
            # 04. attach roles in response
            responseObj["data"]["roles"] = roles
            # 05. attach idMap in response
            responseObj["data"]["idMap"] = idMap
            # 06. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
