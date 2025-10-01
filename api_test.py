import json
import http.client
import mimetypes
from codecs import encode

# --- Configuration ---
BASE_URL = "localhost"
PORT = 8000
USERNAME = "testuser_gemini"
PASSWORD = "password123"

def make_request(method, endpoint, headers=None, body=None):
    conn = http.client.HTTPConnection(BASE_URL, PORT)
    if headers is None:
        headers = {}
    
    # Convert body to JSON string if it's a dict
    if isinstance(body, dict):
        body = json.dumps(body)
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

    conn.request(method, endpoint, body, headers)
    response = conn.getresponse()
    
    print(f"--- Testing {method} {endpoint} ---")
    print(f"Status: {response.status} {response.reason}")
    
    response_body = response.read().decode('utf-8')
    try:
        # Try to parse as JSON
        response_json = json.loads(response_body)
        print("Response JSON:", json.dumps(response_json, indent=2))
        conn.close()
        return response.status, response_json
    except json.JSONDecodeError:
        # If not JSON, print as text
        print("Response Text:", response_body)
        conn.close()
        return response.status, response_body


def make_form_request(endpoint, fields, files, token):
    conn = http.client.HTTPConnection(BASE_URL, PORT)
    content_type, body = encode_multipart_formdata(fields, files)
    
    headers = {
        'Content-Type': content_type,
        'Authorization': f'Bearer {token}'
    }
    
    conn.request('POST', endpoint, body, headers)
    response = conn.getresponse()
    
    print(f"--- Testing POST {endpoint} (multipart/form-data) ---")
    print(f"Status: {response.status} {response.reason}")
    
    response_body = response.read().decode('utf-8')
    try:
        response_json = json.loads(response_body)
        print("Response JSON:", json.dumps(response_json, indent=2))
        conn.close()
        return response.status, response_json
    except json.JSONDecodeError:
        print("Response Text:", response_body)
        conn.close()
        return response.status, response_body

def encode_multipart_formdata(fields, files):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        L.append(b'--' + boundary.encode())
        L.append(b'Content-Disposition: form-data; name="%s"' % key.encode())
        L.append(b'')
        L.append(value.encode())
    for (key, filename, value) in files:
        L.append(b'--' + boundary.encode())
        L.append(b'Content-Disposition: form-data; name="%s"; filename="%s"' % (key.encode(), filename.encode()))
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        L.append(b'Content-Type: %s' % content_type.encode())
        L.append(b'')
        L.append(value)
    L.append(b'--' + boundary.encode() + b'--')
    L.append(b'')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body


def main():
    # 1. Create User
    status, body = make_request(
        "POST",
        "/api/v1/users/",
        body={"username": USERNAME, "password": PASSWORD}
    )
    if status != 200:
        # Try to login in case user already exists
        print("User creation failed, maybe user exists. Trying to log in.")

    # 2. Get Token
    conn = http.client.HTTPConnection(BASE_URL, PORT)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body_str = f"username={USERNAME}&password={PASSWORD}"
    conn.request("POST", "/api/v1/token", body_str, headers)
    response = conn.getresponse()
    print(f"--- Testing POST /api/v1/token ---")
    print(f"Status: {response.status} {response.reason}")
    token_body = json.loads(response.read().decode('utf-8'))
    print("Response JSON:", json.dumps(token_body, indent=2))
    access_token = token_body.get("access_token")
    if not access_token:
        print("!!! FATAL: Could not get access token. Aborting tests.")
        return
    conn.close()

    auth_header = {"Authorization": f"Bearer {access_token}"}

    # 3. Get User Me
    make_request("GET", "/api/v1/users/me", headers=auth_header)

    # 4. Create Field
    status, field_body = make_request(
        "POST",
        "/api/v1/fields/",
        headers=auth_header,
        body={"name": "API Test Field", "location": "Container"}
    )
    if status != 200:
        print("!!! FATAL: Could not create field. Aborting tests.")
        return
    field_id = field_body.get("id")

    # 5. List Fields
    make_request("GET", "/api/v1/fields/", headers=auth_header)

    # 6. Get Field by ID
    make_request("GET", f"/api/v1/fields/{field_id}", headers=auth_header)

    # 7. Update Field
    make_request(
        "PUT",
        f"/api/v1/fields/{field_id}",
        headers=auth_header,
        body={"name": "API Test Field Updated"}
    )

    # 8. Upload Photos
    with open("dummy_drone.jpg", "w") as f:
        f.write("dummy_drone_content")
    with open("dummy_side.jpg", "w") as f:
        f.write("dummy_side_content")
        
    with open("dummy_drone.jpg", "rb") as f_drone, open("dummy_side.jpg", "rb") as f_side:
        status, upload_body = make_form_request(
            "/api/v1/photogroups/upload",
            fields=[
                ('field_id', str(field_id)),
                ('capture_date', '2025-10-01'),
                ('rice_variety', 'API_TEST_VARIETY')
            ],
            files=[
                ('drone_photo', 'dummy_drone.jpg', f_drone.read()),
                ('side_photo_05m', 'dummy_side.jpg', f_side.read()),
                ('side_photo_3m', 'dummy_side.jpg', f_side.read())
            ],
            token=access_token
        )
    
    task_id = upload_body.get("celery_task_id")
    if not task_id:
        print("!!! ERROR: Did not receive celery_task_id from upload endpoint.")
    else:
        print(f"+++ Analysis task started with ID: {task_id}")
        print("Check 'docker-compose logs worker' and 'docker-compose logs backend' to see the analysis progress.")

    # 9. Delete Field
    make_request("DELETE", f"/api/v1/fields/{field_id}", headers=auth_header)
    print("\n--- All tests finished ---")


if __name__ == "__main__":
    main()
