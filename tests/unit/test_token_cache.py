from controllers.services.token_cache import save_token, load_token, delete_token


def test_save_and_load_token(tmp_path):
    path = tmp_path / "token.jwt"
    token = "test.jwt.token"

    save_token(token, path)
    loaded = load_token(path)

    assert loaded == token


def test_load_token_file_not_found(tmp_path):
    path = tmp_path / "token.jwt"
    token = load_token(path)
    assert token is None


def test_load_token_empty_file(tmp_path):
    path = tmp_path / "token.jwt"
    path.write_text("")
    token = load_token(path)
    assert token is None


def test_delete_token_existing_file(tmp_path):
    path = tmp_path / "token.jwt"
    path.write_text("to_delete")

    delete_token(path)
    assert not path.exists()


def test_delete_token_file_not_found(tmp_path):
    path = tmp_path / "token.jwt"
    assert not path.exists()
