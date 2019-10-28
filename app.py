import falcon
from falcon_cors import CORS

from src.extras.status import StatusResource
from src.extras.creator import CreatorResource
from src.extras.destroyer import DestroyerResource

cors = CORS(allow_origins_list = ["http://localhost:4200"],
            allow_all_headers = True,
            allow_all_methods = True)

api = falcon.API(middleware = [
    cors.middleware
])

api.add_route("/", StatusResource())
api.add_route("/creator", CreatorResource())
api.add_route("/destroyer", DestroyerResource())
