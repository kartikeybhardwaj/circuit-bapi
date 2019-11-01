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
        # TODO: username and displayname should come from fapi
        req.params["kartoon-fapi-incoming"] = {}
        req.params["kartoon-fapi-incoming"]["_id"] = "5dbc24cb03b2510ecd2f0c60"
        req.params["kartoon-fapi-incoming"]["username"] = "kartikey.bhardwaj"
        req.params["kartoon-fapi-incoming"]["displayname"] = "Kartikey Bhardwaj"
        req.params["kartoon-fapi-incoming"]["employeeid"] = "772780"
        if req.method != "POST":
            print("request params:", req.params)
            print("request media:", req.media)

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
        if req.method != "OPTIONS":
            print("response:", resp.media)
