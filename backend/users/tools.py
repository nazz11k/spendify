import os
import uuid
import base64


def get_avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    uuid_bytes = uuid.uuid4().bytes
    uuid_b64 = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('ascii')

    return os.path.join('avatars', f'{uuid_b64}{ext}')
