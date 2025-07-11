from typing import List

from config.console import console
from rich.table import Table


def display_menu(title: str, choices: List[str]) -> int:
    """Display a numbered menu and return the selected index (1-based).

    Args:
        title (str): The title of the menu to display.
        choices (List[str]): List of menu options to display.

    Returns:
        int: The 1-based index of the selected menu option.

    Note:
        This function will continue to prompt until a valid choice is made.
    """
    console.rule(f"[bold royal_blue1]{title}")
    for idx, item in enumerate(choices, 1):
        console.print(f"[royal_blue1]{idx}.[/royal_blue1] {item}")
    while True:
        try:
            choice = int(console.input("\nYour choice: "))
            if 1 <= choice <= len(choices):
                return choice
            display_error(
                f"Invalid choice. Please choose a number between 1 and {len(choices)}",
                clear=False
            )
        except ValueError:
            display_error(
                f"Please enter a valid number. "
                f"Please choose a number between 1 and {len(choices)}",
                clear=False
            )


def display_error(msg: str, clear: bool = True) -> None:
    """Print an error message in red.

    Args:
        msg (str): The error message to display.
        clear (bool, optional): Whether to clear the console before displaying. 
                               Defaults to True.
    """
    if clear:
        console.clear()
    console.print(f"[bold red]{msg}")


def display_success(msg: str, clear: bool = True) -> None:
    """Print a success message in green.

    Args:
        msg (str): The success message to display.
        clear (bool, optional): Whether to clear the console before displaying. 
                               Defaults to True.
    """
    if clear:
        console.clear()
    console.print(f"[bold green]{msg}")


def display_info(msg: str, clear: bool = True) -> None:
    """Print an info message in yellow.

    Args:
        msg (str): The info message to display.
        clear (bool, optional): Whether to clear the console before displaying. 
                               Defaults to True.
    """
    if clear:
        console.clear()
    console.print(f"[bold yellow]{msg}")


def create_table(title: str, columns: List[str]) -> Table:
    """Create and return a Rich Table with default styling.

    Args:
        title (str): The title of the table.
        columns (List[str]): List of column names to add to the table.

    Returns:
        Table: A Rich Table instance with the specified title and columns.
    """
    table = Table(title=title, header_style="royal_blue1 bold")
    for col in columns:
        table.add_column(col)
    return table
