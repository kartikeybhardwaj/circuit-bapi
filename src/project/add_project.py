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
                dataToBeInserted = {}
                dataToBeInserted["index"] = index
                dataToBeInserted["title"] = requestObj["title"]
                dataToBeInserted["isActive"] = True
                dataToBeInserted["description"] = requestObj.get("description", "")
                dataToBeInserted["milestonesList"] = []
                dataToBeInserted["visibility"] = requestObj["visibility"]
                dataToBeInserted["members"] = []
                dataToBeInserted["projectMetaId"] = requestObj["projectMetaId"]
                dataToBeInserted["fields"] = requestObj["fields"]
                dataToBeInserted["meta"] = {
                    "addedBy": req.params["kartoon-fapi-incoming"]["_id"],
                    "addedOn": datetime.datetime.utcnow(),
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
                dbpr = DBProject()
                responseObj["data"]["_id"] = dbpr.insertProject(dataToBeInserted)
                responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = ex.message
        resp.media = responseObj
