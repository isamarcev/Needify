import json


def write_to_file(file_name, content):
    with open(f"{file_name}.json", "w") as file:
        json.dump(content, file, indent=4)
