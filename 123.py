from steganocryptopy.steganography import Steganography
result = Steganography.decrypt('key.key','static/img/secret_img.jpg')
print(result)