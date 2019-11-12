import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_user import validate_add_user_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter

dbu = DBUser()
dbc = DBCounter()

class AddSuperuserResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_user_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def prepareDataToBeInserted(self, index: int, requestObj: dict) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["username"] = requestObj["username"]
        dataToBeInserted["displayname"] = requestObj["displayname"]
        dataToBeInserted["isSuperuser"] = True
        dataToBeInserted["baseLocation"] = None
        dataToBeInserted["otherLocations"] = []
        dataToBeInserted["nonAvailability"] = []
        dataToBeInserted["access"] = {
            "projects": []
        }
        dataToBeInserted["meta"] = {
            "addedBy": None,
            "addedOn": datetime.datetime.utcnow(),
            "lastSeen": None
        }
        return dataToBeInserted

    """
    REQUEST:
        "username": str
        "displayname": str
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
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "schema validation failed"))
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            log.info((thisFilename, inspect.currentframe().f_code.co_name, "schema validation successful"))
            try:
                # check if user exists
                userCount = dbu.countDocumentsByUsername(requestObj["username"])
                if userCount == 1:
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "user exists, update to superuser"))
                    # if yes, updateUserToSuperuser
                    dbu.updateUserToSuperuser(requestObj["username"])
                elif userCount == 0:
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "user does not exist, add as superuser"))
                    # if no
                    # 01. get index for new user
                    index = dbc.getNewUserIndex()
                    # 02. increment user counter
                    dbc.incrementUserIndex()
                    # 03. prepare dataToBeInserted
                    dataToBeInserted = self.prepareDataToBeInserted(index, requestObj)
                    # 04. insert dataToBeInserted in users and attach userId in response
                    responseObj["data"]["_id"] = dbu.insertUser(dataToBeInserted)
                # 05. set responseId to success
                responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
