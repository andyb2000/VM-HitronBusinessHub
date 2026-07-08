from vmhub import VMHub


def test_vmhub_can_be_instantiated() -> None:
    hub = VMHub(host="192.168.0.1", username="admin", password="password")

    assert hub.base == "http://192.168.0.1"
    assert hub.username == "admin"
    assert hub.password == "password"
