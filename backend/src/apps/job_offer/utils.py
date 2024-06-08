import base64


def decode_b64(data):
    decoded_strings = []

    def recurse(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "b64":
                    decoded_value = base64.b64decode(value).decode("utf-8")
                    decoded_strings.append(decoded_value)
                else:
                    recurse(value)
        elif isinstance(data, list):
            for item in data:
                recurse(item)

    recurse(data)
    return "".join(decoded_strings)
