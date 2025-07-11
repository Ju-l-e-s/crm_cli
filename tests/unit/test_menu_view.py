from views.menu_view import get_menu_options


def test_get_menu_options_commercial():
    opts = get_menu_options("commercial")
    labels = [label for label, _ in opts]
    assert labels == ["Clients", "Contracts", "Events", "Log out", "Quit"]


def test_get_menu_options_gestion():
    opts = get_menu_options("gestion")
    labels = [label for label, _ in opts]
    assert labels == ["Clients", "Contracts",
                      "Events", "Collaborators", "Log out", "Quit"]
