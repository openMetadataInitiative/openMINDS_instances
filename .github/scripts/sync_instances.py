import json
import re
import sys

from utils import properties_file, regex_pattern_type, regex_pattern_instance, types_file, version_file


def sync_properties(src_data, tgt_data, version):
    """Sync properties from src_data to tgt_data."""
    for key, value in src_data.items():
        try:
            if key == "@vocab":
                tgt_data[key] = version_file[version]["namespaces"]["props"]
                continue
            # Check if @type exists for a given version and add the appropriate namespaces
            elif key == "@type":
                if re.match(regex_pattern_type, src_data[key]):
                    _type = re.sub(regex_pattern_type, "", src_data[key])
                    tgt_data[key] = [_namespace_version for _namespace_version in types_file[_type]["hasNamespace"] if version in _namespace_version["inVersions"]][0]['namespace'] + _type
                else:
                    tgt_data[key] = src_data[key]
                continue
            elif key == "@id":
                if re.match(regex_pattern_instance, src_data[key]):
                    _id = re.sub(regex_pattern_instance, "", src_data[key])
                    tgt_data[key] = version_file[version]["namespaces"]["instances"] + _id
                else:
                    tgt_data[key] = src_data[key]
                continue
        except IndexError:
            print(f"Type {_type} not found in version {version}.")
            return

        # Check if a property exists for a given version, if not remove it
        if key in ["@context", "@type"]:
            continue
        elif key in properties_file:
            try:
                [_namespace_version for _namespace_version in properties_file[key]["hasNamespace"] if version in _namespace_version["inVersions"]][0]
            except IndexError:
                del tgt_data[key]
                print(f"Property skipped: {key} not found in version {version}.")
                continue
        else:
            del tgt_data[key]
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
    with open(src_file) as f:
        src_data = json.load(f)

    # Load target JSON data
    try:
        with open(tgt_file) as f:
            tgt_data = json.load(f)
    except FileNotFoundError:
        tgt_data = {}

    print(f'Synced properties from {src_file} to {tgt_file}')

    # Sync properties
    target_data = sync_properties(src_data, tgt_data, version)

    # Write the updated target data back to the file
    with open(tgt_file, 'w') as f:
        json.dump(target_data, f, indent=2)

    print(f'Successfully synced properties from {src_file} to {tgt_file}')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python sync_instances.py <src_file> <tgt_file> <version>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
