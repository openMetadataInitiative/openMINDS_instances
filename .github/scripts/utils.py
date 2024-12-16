import json


with open('.github/templates/versions-instances.json') as f:
    version_file = json.load(f)
with open('.github/templates/types.json') as f:
    types_file = json.load(f)
with open('.github/templates/properties.json') as f:
    properties_file = json.load(f)

regex_pattern_type = r"https://openminds\.(om-i\.org|ebrains\.eu)/.*/"
regex_pattern_instance = r"^https://openminds\.(om-i\.org|ebrains\.eu)/instances/"
