class StatusResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        responseObj = {
            "status": (
                "I'm working, "
                "hell yeah!!"
            ),
            "author": "kartoon"
        }
        resp.media = responseObj