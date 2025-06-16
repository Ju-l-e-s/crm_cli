from unittest.mock import MagicMock, patch

# display_error / success / info use console correctly
def test_base_display_helpers():
    from views import base as base_view

    mock_console = MagicMock()
    with patch.object(base_view, "console", mock_console):
        base_view.display_error("Err")
        base_view.display_success("Ok")
        base_view.display_info("Info")

    assert mock_console.clear.call_count == 3
    assert mock_console.print.call_count == 3
    mock_console.print.assert_any_call("[bold red]Err")
    mock_console.print.assert_any_call("[bold green]Ok")
    mock_console.print.assert_any_call("[bold yellow]Info")

# display_menu looping behaviour
def test_display_menu_invalid_then_valid(monkeypatch):
    """display_menu should loop until a valid numeric choice is entered."""
    from views import base as base_view

    mock_console = MagicMock()
    mock_console.input.side_effect = ["abc", "5", "2"]
    monkeypatch.setattr(base_view, "console", mock_console)

    with patch("views.base.display_error") as mock_err:
        choice = base_view.display_menu("Title", ["one", "two", "three"])
        assert choice == 2
        assert mock_err.call_count == 2
