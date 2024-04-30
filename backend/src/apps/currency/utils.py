import base64


def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read())
        return encoded_string.decode("utf-8")

def save_base64_string(base64_string, output_file):
    with open(output_file, "w") as file:
        file.write(base64_string)

# Пример использования
image_path = "token_image.png"
base64_string = image_to_base64(image_path)
save_base64_string(base64_string, "token_image_output.txt")