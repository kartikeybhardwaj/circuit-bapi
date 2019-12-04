# for windows

from app import api
from waitress import serve

serve(api, port=3200)