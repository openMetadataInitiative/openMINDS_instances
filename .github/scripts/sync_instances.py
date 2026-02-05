import json
import re
import sys


def load_json(path):
    with open(path) as f:
        json_file = json.load(f)
    return json_file

VERSION_FILE = load_json('.github/versions.json')
TYPES_FILE = load_json('.github/types.json')
PROPERTIES_FILE = load_json('.github/properties.json')
REGEX_PATTERN_TYPE = r"https://openminds\.(om-i\.org|ebrains\.eu)/.*/"
REGEX_PATTERN_INSTANCE = r"^https://openminds\.(om-i\.org|ebrains\.eu)/instances/"

def sync_properties(src_data, tgt_data, version):
    """Sync properties from src_data to tgt_data."""
    for key, value in src_data.items():
        if key == "@context":
            tgt_data["@context"] = { "@vocab": VERSION_FILE[version]["namespaces"]["props"] }
            continue

        # Check if @type exists for a given version and add the appropriate namespace
        elif key == "@type":
            if re.match(REGEX_PATTERN_TYPE, src_data[key]):
                schema_type_name = re.sub(REGEX_PATTERN_TYPE, "", src_data[key])
                if schema_type_name not in TYPES_FILE or version not in TYPES_FILE[schema_type_name]['isPartOfVersion']:
                    print(f"Type {schema_type_name} not found in version {version}.")
                    return

                for ns in TYPES_FILE[schema_type_name]["hasNamespace"]:
                    if version in ns["inVersions"]:
                        tgt_data[key] = ns["namespace"] + schema_type_name
                        break
                else:
                    print(f"No namespace found for type {schema_type_name} in version {version}.")
                    return
            else:
                tgt_data[key] = src_data[key]
            continue
        elif key == "@id":
            if re.match(REGEX_PATTERN_INSTANCE, src_data[key]):
                _id = re.sub(REGEX_PATTERN_INSTANCE, "", src_data[key])
                tgt_data[key] = VERSION_FILE[version]["namespaces"]["instances"] + _id
            else:
                tgt_data[key] = src_data[key]
            continue

        if key in ["@context", "@type"]:
            continue
        elif key in PROPERTIES_FILE:
            versions_used_in = PROPERTIES_FILE[key]["usedIn"]
            if version not in versions_used_in:
                print(f"Property skipped: {key} not used in version {version}.")
                continue
            elif tgt_data["@type"] not in versions_used_in[version]:
                print(f"Property skipped: {key} not used with the @type {tgt_data['@type']} in version {version}.")
                continue
        else:
            print(f"Property skipped: {key} not found.")
            continue

        # If the value is a dictionary, recurse
        if isinstance(value, dict):
            tgt_data[key] = sync_properties(value, tgt_data.get(key, {}), version)

        elif isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                # Add the list if it does not exist in tgt_data
                # Modify the list if its original length is equal to the new one
                if key not in tgt_data:
                    tgt_data[key] = []

                if len(tgt_data[key]) == 0 or len(tgt_data[key]) == len(value):
                    tgt_data[key] = []
                    for idx, item in enumerate(value):
                        tgt_data[key].append({})
                        tgt_data[key][idx] = sync_properties(item, tgt_data[key][idx], version)
            else:
                # Non-dictionary values
                tgt_data[key] = value
        else:
            # Update the value in the target for other data types
            tgt_data[key] = value

    return tgt_data

def main(src_file, tgt_file, version):
    # Load source JSON data
    src_data = load_json(src_file)

    # Load target JSON data if it exists
    try:
        tgt_data = load_json(tgt_file)
    except FileNotFoundError:
        tgt_data = {}

    print(f'Synced properties from {src_file} to {tgt_file}')

    # Sync properties
    target_data = sync_properties(src_data, tgt_data, version)

    # Write the updated target data back to the target file
    with open(tgt_file, 'w') as f:
        json.dump(target_data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n\n")
    print(f'Successfully synced properties from {src_file} to {tgt_file}')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python sync_instances.py <src_file> <tgt_file> <version>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
