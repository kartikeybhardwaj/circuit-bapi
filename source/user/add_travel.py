import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_travel import validate_add_travel_schema

from database.user.user import DBUser
from database.location.location import DBLocation
from utils.utils import Utils

dbu = DBUser()
dbl = DBLocation()
utils = Utils()

class AddTravelResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_travel_schema)
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
            # check if locationId exists
            if dbl.countDocumentsById(locationId) != 1:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "locationId does not exists"))
                success = False
                message = "Invalid locationId"
        return [success, message]

    def validateTimeline(self, timeline: dict) -> [bool, str]:
        success = True
        message = ""
        tbegin = utils.getDateFromUTCString(timeline["begin"])
        tend = utils.getDateFromUTCString(timeline["end"])
        # end should be greater than begin
        if not tend > tbegin:
            success = False
            message = "Invalid timeline"
        return [success, message]

    """
    REQUEST:
        "locationId": str
        "timeline": dict
            "begin": str
            "end": str
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
            # validate location id
            afterValidationLocationId = self.validateLocationId(requestObj["locationId"])
            if not afterValidationLocationId[0]:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid location id"))
                responseObj["responseId"] = 110
                responseObj["message"] = afterValidationLocationId[1]
            else:
                # validate timeline
                afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
                if not afterValidationTimeline[0]:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid timeline"))
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationTimeline[1]
                else:
                    # validation collision of dates
                    overlappedLocationId = dbu.getCollisionTravelLocationId(req.params["kartoon-fapi-incoming"]["_id"], requestObj["timeline"])
                    if overlappedLocationId:
                        log.warn((thisFilename, inspect.currentframe().f_code.co_name, "timeline overlap"))
                        responseObj["responseId"] = 110
                        responseObj["data"]["locationId"] = overlappedLocationId
                        responseObj["message"] = "There is overlap with another location"
                    else:
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "all validations passed"))
                        try:
                            # insert travel
                            log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                            dbu.insertTravel(req.params["kartoon-fapi-incoming"]["_id"], requestObj["locationId"], requestObj["timeline"])
                            responseObj["responseId"] = 211
                        except Exception as ex:
                            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                            responseObj["message"] = str(ex)
        resp.media = responseObj
