import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_update_base_location import validate_update_base_location_schema

from database.user.user import DBUser
from database.location.location import DBLocation

dbu = DBUser()
dbl = DBLocation()

# check if locationId is valid ObjectId
# does this locationId exists
# is this locationId active

class UpdateBaseLocationResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_update_base_location_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def validateLocationId(self, locationId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(locationId)
        except Exception as ex:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
            success = False
            message = "Invalid locationId"
        if success:
            if dbl.countDocumentsById(locationId) != 1:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "location id does not exist"))
                success = False
                message = "Invalid locationId"
        return [success, message]

    """
    REQUEST:
        "locationId": str
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
                # validate locationId
                afterValidationLocationId = self.validateLocationId(requestObj["locationId"])
                if not afterValidationLocationId[0]:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid locationId"))
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationLocationId[1]
                else:
                    # update locationId
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "updating data"))
                    dbu.updateLocationId(req.params["kartoon-fapi-incoming"]["_id"], requestObj["locationId"])
                    responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
