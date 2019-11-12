import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_role import validate_add_role_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.role.role import DBRole

dbu = DBUser()
dbc = DBCounter()
dbr = DBRole()

class AddRoleResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_role_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def alreadyHasThisRole(self, title: str) -> bool:
        success = False
        if dbr.countDocumentsByTitle(title) > 0:
            success = True
        return success

    def prepareDataToBeInserted(self, index: int, requestObj: dict, userId: str) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["title"] = requestObj["title"]
        dataToBeInserted["description"] = requestObj["description"]
        dataToBeInserted["canModifyUsersRole"] = requestObj["canModifyUsersRole"]
        dataToBeInserted["canModifyLocations"] = requestObj["canModifyLocations"]
        dataToBeInserted["canModifyProjects"] = requestObj["canModifyProjects"]
        dataToBeInserted["canModifyMilestones"] = requestObj["canModifyMilestones"]
        dataToBeInserted["canModifyPulses"] = requestObj["canModifyPulses"]
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
        "canModifyUsersRole": bool
        "canModifyLocations": bool
        "canModifyProjects": bool
        "canModifyMilestones": bool
        "canModifyPulses": bool
    """
    def on_post(self, req, resp):
        requestObj = req.media
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "schema validation failed"))
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            log.info((thisFilename, inspect.currentframe().f_code.co_name, "schema validation successful"))
            try:
                # check if user is superuser
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "user is not superuser"))
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                elif self.alreadyHasThisRole(requestObj["title"]):
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "already has role by this title"))
                    # check if this role already exists by title
                    responseObj["responseId"] = 108
                    responseObj["message"] = "Already exists"
                else:
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to insert"))
                    # 01. get index for new role
                    index = dbc.getNewRoleIndex()
                    # 02. increment role counter
                    dbc.incrementRoleIndex()
                    # 03. prepare dataToBeInserted
                    dataToBeInserted = self.prepareDataToBeInserted(index, requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                    # 04. insert dataToBeInserted in roles and attach roleId in response
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                    responseObj["data"]["_id"] = dbr.insertRole(dataToBeInserted)
                    # 05. set responseId to success
                    responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
