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

class AddUserResource:

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

    def addUser(self, username: str, displayname: str, addedBy: str) -> str:
        log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing user data to insert"))
        # 01. get index for new user
        index = dbc.getNewUserIndex()
        # 02. increment user counter
        dbc.incrementUserIndex()
        # prepare dataToBeInserted
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["username"] = username
        dataToBeInserted["displayname"] = displayname
        dataToBeInserted["isSuperuser"] = False
        dataToBeInserted["baseLocation"] = None
        dataToBeInserted["otherLocations"] = []
        dataToBeInserted["nonAvailability"] = []
        dataToBeInserted["access"] = {
            "projects": []
        }
        dataToBeInserted["meta"] = {
            "addedBy": ObjectId(addedBy) if addedBy else None,
            "addedOn": datetime.datetime.utcnow(),
            "lastSeen": None
        }
        log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting user"))
        return dbu.insertUser(dataToBeInserted)

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
                # 01. check if user exists
                userCount = dbu.countDocumentsByUsername(requestObj["username"])
                if userCount == 1:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "this user already exists"))
                    # 01. 01. if yes
                    responseObj["responseId"] = 108
                    responseObj["message"] = "Already exists"
                elif userCount == 0:
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "user does not exist"))
                    # 01. 02. if no
                    # 01. 03. insert user in users attach userId in response
                    responseObj["data"]["_id"] = self.addUser(
                        requestObj["username"],
                        requestObj["displayname"],
                        req.params["kartoon-fapi-incoming"]["_id"])
                    # 01. 04. set responseId to success
                    responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
