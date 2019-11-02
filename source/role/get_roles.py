from database.role.role import DBRole

dbr = DBRole()

class GetRolesResource():

    def idMapForRoleIds(self, roles: "list of dict") -> dict:
        idMap = {}
        # 01. get title and map it to _id from roles
        for role in roles:
            idMap[role["_id"]["$oid"]] = role["title"]
        return idMap

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
            # 03. attach roles in response
            responseObj["data"]["roles"] = roles
            # 04. attach idMap in response
            responseObj["data"]["idMap"] = idMap
            # 05. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
