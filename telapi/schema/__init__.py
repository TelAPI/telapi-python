import json
import pkg_resources

SCHEMA = json.load(pkg_resources.resource_string(__name__, "telapi.json"))
