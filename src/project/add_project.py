from bson.objectid import ObjectId
import datetime
import re

from database.counter.counter import DBCounter
from database.project.project import DBProject

class AddProjectResource:

    def validateTitle(self, title: str) -> bool:
        success = False
        if isinstance(title, str) and re.match('^[0-9a-zA-Z\-\ ]*$', title) and len(title) > 3:
            success = True
        return success

    def validateVisibility(self, visibility: str) -> bool:
        success = False
        if isinstance(visibility, str) and visibility in ["public", "internal", "private"]:
            success = True
        return success

    def validateProjectMetaId(self, projectMetaId: "str | None", fields: dict) -> bool:
        success = False
        if projectMetaId and isinstance(projectMetaId, str):
            try:
                ObjectId(projectMetaId)
                # TODO: check if this project meta really exists
                # and check if all the fields are as per the meta that exists in db
                success = True
            except Exception as ex:
                pass
        # TODO: return success
        return True

    def on_post(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            requestObj = req.media
            if not self.validateTitle(requestObj.get("title", "")):
                responseObj["responseId"] = 110
                responseObj["message"] = "Invalid title"
            elif not self.validateVisibility(requestObj.get("visibility", "")):
                responseObj["responseId"] = 110
                responseObj["message"] = "Invalid visibility"
            elif not self.validateProjectMetaId(requestObj.get("projectMetaId", "")):
                responseObj["responseId"] = 110
                responseObj["message"] = "Invalid meta"
            else:
                dbc = DBCounter()
                index = dbc.getNewProjectIndex()
                dbc.incrementProjectIndex()
                projectToBeAdded = {}
                projectToBeAdded["index"] = index
                projectToBeAdded["title"] = requestObj["title"]
                projectToBeAdded["isActive"] = True
                projectToBeAdded["description"] = requestObj.get("description", "")
                projectToBeAdded["milestonesList"] = []
                projectToBeAdded["visibility"] = requestObj["visibility"]
                projectToBeAdded["members"] = []
                projectToBeAdded["projectMetaId"] = requestObj["projectMetaId"]
                projectToBeAdded["fields"] = requestObj["fields"]
                projectToBeAdded["meta"] = {
                    "addedBy": req.params["kartoon-fapi-incoming"]["_id"],
                    "addedOn": datetime.datetime.utcnow(),
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
                dbpr = DBProject()
                responseObj["data"]["_id"] = dbpr.insertProject(projectToBeAdded)
                responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
