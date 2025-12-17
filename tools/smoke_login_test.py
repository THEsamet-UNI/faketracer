import traceback

try:
    from app import app
    with app.test_client() as c:
        resp = c.post('/auth/login', data={'email':'doesnotexist@example.com','password':'x'}, follow_redirects=True)
        print('STATUS', resp.status_code)
        data = resp.get_data(as_text=True)
        print(data[:4000])
except Exception:
    traceback.print_exc()
