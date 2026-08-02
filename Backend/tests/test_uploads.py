import io

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def make_png_bytes():
    return PNG_MAGIC + b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89" + b"\x00" * 16


def make_gif_bytes():
    return b"GIF89a" + b"\x00" * 20


def make_jpg_bytes():
    return b"\xff\xd8\xff\xe0" + b"\x00" * 20


def test_upload_requires_auth(app):
    resp = app.post("/upload", files={"file": ("pic.png", io.BytesIO(make_png_bytes()), "image/png")})
    assert resp.status_code == 401


def test_upload_rejects_bad_extension(app, signup, auth_headers):
    user = signup("up_a")
    headers = auth_headers(user["token"])
    resp = app.post("/upload", files={"file": ("evil.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")}, headers=headers)
    assert resp.status_code == 400


def test_upload_rejects_fake_image(app, signup, auth_headers):
    user = signup("up_b")
    headers = auth_headers(user["token"])
    resp = app.post("/upload", files={"file": ("fake.png", io.BytesIO(b"this is not an image at all"), "image/png")}, headers=headers)
    assert resp.status_code == 400


def test_upload_rejects_empty_file(app, signup, auth_headers):
    user = signup("up_c")
    headers = auth_headers(user["token"])
    resp = app.post("/upload", files={"file": ("empty.png", io.BytesIO(b""), "image/png")}, headers=headers)
    assert resp.status_code == 400


def test_upload_rejects_oversized_file(app, signup, auth_headers):
    user = signup("up_d")
    headers = auth_headers(user["token"])
    big = PNG_MAGIC + b"\x00" * (6 * 1024 * 1024)
    resp = app.post("/upload", files={"file": ("big.png", io.BytesIO(big), "image/png")}, headers=headers)
    assert resp.status_code == 413


def test_upload_and_serve_roundtrip(app, signup, auth_headers):
    user = signup("up_e")
    headers = auth_headers(user["token"])
    resp = app.post("/upload", files={"file": ("pic.png", io.BytesIO(make_png_bytes()), "image/png")}, headers=headers)
    assert resp.status_code == 200
    image_url = resp.json()["image_url"]
    assert image_url.startswith("/uploads/")

    served = app.get(image_url, params={"token": user["token"]})
    assert served.status_code == 200
    assert served.headers["content-type"] == "image/png"
    assert served.content.startswith(PNG_MAGIC)


def test_serve_image_requires_token(app, signup, auth_headers):
    user = signup("up_f")
    headers = auth_headers(user["token"])
    resp = app.post("/upload", files={"file": ("pic.png", io.BytesIO(make_png_bytes()), "image/png")}, headers=headers)
    image_url = resp.json()["image_url"]

    resp = app.get(image_url)
    assert resp.status_code == 401


def test_serve_unknown_image_404(app, signup, auth_headers):
    user = signup("up_g")
    resp = app.get("/uploads/nonexistent.png", params={"token": user["token"]})
    assert resp.status_code == 404


def test_upload_multiple_types(app, signup, auth_headers):
    user = signup("up_h")
    headers = auth_headers(user["token"])
    for name, data, mime in [
        ("a.gif", make_gif_bytes(), "image/gif"),
        ("b.jpg", make_jpg_bytes(), "image/jpeg"),
        ("c.png", make_png_bytes(), "image/png"),
    ]:
        resp = app.post("/upload", files={"file": (name, io.BytesIO(data), mime)}, headers=headers)
        assert resp.status_code == 200, (name, resp.text)
