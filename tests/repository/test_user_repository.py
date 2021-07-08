from saltapi.repository.user_repository import UserRepository
from tests.markers import nodatabase

TEST_DATA_PATH = "repository/user_repository.yaml"


@nodatabase
def test_get_user_returns_correct_user(dbconnection, testdata):
    expected = testdata(TEST_DATA_PATH)["get_user"]
    user_repository = UserRepository(dbconnection)
    user = user_repository.get(expected["id"])

    assert user.id == expected["id"]
    assert user.username == expected["username"]
    assert user.given_name == expected["given_name"]
    assert user.email is not None

