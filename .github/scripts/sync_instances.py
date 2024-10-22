import json
import sys


def sync_properties(src_data, tgt_data):
    """Sync properties from src_data to tgt_data."""
    for key, value in src_data.items():
        # Skip special keys that should not be modified
        if key in ["@vocab", "@type", "@id"]:
            continue

        # If the value is a dictionary, recurse
        if isinstance(value, dict):
            tgt_data[key] = sync_properties(value, tgt_data.get(key, {}))

        elif isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                tgt_data[key] = tgt_data.get(key, [{}] * len(value))  # Ensure tgt_data has the same length
                for idx, item in enumerate(value):
                    tgt_data[key][idx] = sync_properties(item, tgt_data[key][idx])
            else:
                # Non-dictionary values
                tgt_data[key] = value

        else:
            # Update the value in the target for other data types
            tgt_data[key] = value

    return tgt_data


def main(src_file, tgt_file):
    # Load source JSON data
    with open(src_file) as f:
        src_data = json.load(f)

    # Load target JSON data
    with open(tgt_file) as f:
        tgt_data = json.load(f)

    print(f'Synced properties from {src_file} to {tgt_file}')

    # Sync properties
    target_data = sync_properties(src_data, tgt_data)

    # Write the updated target data back to the file
    with open(tgt_file, 'w') as f:
        json.dump(target_data, f, indent=4)

    print(f'Successfully synced properties from {src_file} to {tgt_file}')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_instances.py <src_file> <tgt_file>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
