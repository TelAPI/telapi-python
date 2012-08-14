import json
import os

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'telapi.json')
SCHEMA = json.load(open(SCHEMA_FILE))
