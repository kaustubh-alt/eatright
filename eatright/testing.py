import requests

api_key = 'acc_1e73229f9c912aa'
api_secret = '0b868bd67ada548e59088b5bcbf28ebb'
image_path = r"C:\Programs\intaste\glowminds\staticfiles\mutton-biryani.jpg"

response = requests.post(
    'https://api.imagga.com/v2/tags',
    auth=(api_key, api_secret),
    files={'image': open(image_path, 'rb')})
print(response.json())