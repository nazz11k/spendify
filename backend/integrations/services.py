import requests
from django.conf import settings
from rest_framework.exceptions import APIException


class AIServiceError(APIException):
    status_code = 503
    default_detail = 'AI Service unavailable'
    default_code = 'service_unavailable'


def scan_receipt(image_file):
    url = settings.RECEIPT_EXTRACTOR_API_URL

    try:
        files = {'file': (image_file.name, image_file, image_file.content_type)}
        response = requests.post(url, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result['data']
            else:
                raise AIServiceError(f"AI Error: {result.get('error')}")
        else:
            raise AIServiceError(f"AI Service returned status {response.status_code}")

    except requests.exceptions.RequestException as e:
        raise AIServiceError(f"Connection failed: {str(e)}")
