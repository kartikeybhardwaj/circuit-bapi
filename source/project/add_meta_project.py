from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_add_meta_project import validate_add_meta_project_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.project.project import DBProject

dbu = DBUser()
dbc = DBCounter()
dbpr = DBProject()

class AddMetaProjectResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_meta_project_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def prepareDataToBeInserted(self, index: int, requestObj: dict, userId: str) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["title"] = requestObj["title"]
        dataToBeInserted["description"] = requestObj["description"]
        dataToBeInserted["fields"] = requestObj["fields"]
        dataToBeInserted["meta"] = {
            "addedBy": ObjectId(userId),
            "addedOn": datetime.datetime.utcnow(),
            "lastUpdatedBy": None,
            "lastUpdatedOn": None
        }
        return dataToBeInserted

    """
    REQUEST:
        "title": str
        "description": str
        "fields": dict
    """
    def on_post(self, req, resp):
        requestObj = req.media
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
            try:
                # check if user is superuser
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    # if not
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # if yes
                    # 01. get index for new metaProject
                    index = dbc.getNewMetaProjectIndex()
                    # 02. increment metaProject counter
                    dbc.incrementMetaProjectIndex()
                    # 03. prepare dataToBeInserted
                    dataToBeInserted = self.prepareDataToBeInserted(index, requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                    # 04. insert dataToBeInserted in metaProjects and attach metaProjectId in response
                    responseObj["data"]["_id"] = dbpr.insertMetaProject(dataToBeInserted)
                    # 05. set responseId to success
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
