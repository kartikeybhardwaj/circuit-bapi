from database.user.user import DBUser
from database.project.project import DBProject

class GetProjectsResource:

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            dbu = DBUser()
            dbpr = DBProject()
            if dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                projectIds = [pi["_id"]["$oid"] for pi in dbpr.getAllProjectIds()]
            else:
                accessibleProjects = dbu.getAccessibleProjects(req.params["kartoon-fapi-incoming"]["_id"])
                accessibleProjectIds = [api["projectId"]["$oid"] for api in accessibleProjects]
                publicProjects = dbpr.getPublicProjectIds()
                publicProjectIds = [ppi["_id"]["$oid"] for ppi in publicProjects]
                projectIds = list(set(accessibleProjectIds + publicProjectIds))
            responseObj["data"] = dbpr.getProjectsByIds(projectIds)
            responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
