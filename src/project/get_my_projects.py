from database.user.user import DBUser
from database.project.project import DBProject

class GetMyProjectsResource:

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            dbu = DBUser()
            # check if user is superuser
            if dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                # if yes, fetch all projects
                print("user is superuser")
                dbpr = DBProject()
                responseObj["data"] = dbpr.getAllProjects()
            else:
                # if not, fetch projects only where incoming user have access to
                print("user is not superuser")
                # fetch projectIds from user's access list
                # TODO: 
                # accessibleProjectIds = dbu.getAccessibleProjects()
                # responseObj["data"] = accessibleProjectIds
                # print(accessibleProjectIds)
            responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = ex.message
        resp.media = responseObj
