class StatusResource:

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 211,
            "status": "Yes, this is me, working.",
            "author": "kartoon"
        }
        resp.media = responseObj
