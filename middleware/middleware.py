import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

import json
from constants.secret import FapiToBapiSecret

class Middleware:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_request(self, req, resp):
        """Process the request before routing it.
        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().
        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
                the on_* responder.
        """
        if req.method == "GET" or req.method == "POST":
            log.info((thisFilename, inspect.currentframe().f_code.co_name, req.path, "params", str(req.params)))
        if req.method == "POST":
            log.info((thisFilename, inspect.currentframe().f_code.co_name, req.path, "media", str(req.media)))
        if req.method != "OPTIONS":
            if "kartoon-fapi-incoming" not in req.params:
                resp.media = {
                    "responseId": 103,
                    "message": "Invalid request"
                }
                # exit request
                resp.complete = True
            else:
                req.params["kartoon-fapi-incoming"] = json.loads(req.params["kartoon-fapi-incoming"])
                if req.params["kartoon-fapi-incoming"]["secretKey"] != FapiToBapiSecret:
                    resp.media = {
                        "responseId": 109,
                        "message": "Unauthorized access"
                    }
                    # exit request
                    resp.complete = True

    def process_response(self, req, resp, resource, req_succeeded):
        """Post-processing of the response (after routing).
        Args:
            req: Request object.
            resp: Response object.
            resource: Resource object to which the request was
                routed. May be None if no route was found
                for the request.
            req_succeeded: True if no exceptions were raised while
                the framework processed and routed the request;
                otherwise False.
        """
        if req.method == "POST":
            log.info((thisFilename, inspect.currentframe().f_code.co_name, "media", str(resp.media)))
