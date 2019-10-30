from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_locations import validate_add_locations_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.location.location import DBLocation

class AddLocationsResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_locations_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def on_post(self, req, resp):
        requestObj = req.media
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            try:
                dbu = DBUser()
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    dbc = DBCounter()
                    dbl = DBLocation()
                    locations = []
                    extraData = {
                        "isActive": True,
                        "meta": {
                            "addedBy": req.params["kartoon-fapi-incoming"]["_id"],
                            "addedOn": datetime.datetime.utcnow(),
                            "lastUpdatedBy": None,
                            "lastUpdatedOn": None
                        }
                    }
                    for i in range(len(requestObj["names"])):
                        locations.append({})
                        index = dbc.getNewLocationIndex()
                        dbc.incrementLocationIndex()
                        locations[i]["index"] = index
                        locations[i]["name"] = requestObj["names"][i]
                        locations[i].update(extraData)
                    responseObj["data"]["_ids"] = dbl.insertLocations(locations)
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = ex.message
        resp.media = responseObj
