from config.console import console

def display_menu(title, choices):
    """Display a numbered menu and return the selected index (1-based)."""
    console.rule(f"[bold royal_blue1]{title}")
    for idx, item in enumerate(choices, 1):
        console.print(f"[royal_blue1]{idx}.[/royal_blue1] {item}")
    while True:
        try:
            choice = int(console.input("\nYour choice: "))
            if 1 <= choice <= len(choices):
                return choice
            display_error(f"Invalid choice. Please choose a number between 1 and {len(choices)}", clear=False)
        except ValueError:
            display_error(f"Please enter a valid number. Please choose a number between 1 and {len(choices)}", clear=False)

def display_error(msg, clear=True):
    """Print an error message in red."""
    if clear:
        console.clear()
    console.print(f"[bold red]{msg}")

def display_success(msg, clear=True):
    """Print a success message in green."""
    if clear:
        console.clear()
    console.print(f"[bold green]{msg}")

def display_info(msg, clear=True):
    """Print an info message in yellow."""
    if clear:
        console.clear()
    console.print(f"[bold yellow]{msg}")


def create_table(title: str, columns: list[str]):
    """Return a Rich Table with default violet header style."""
    from rich.table import Table

    table = Table(title=title, header_style="royal_blue1 bold")
    for col in columns:
        table.add_column(col)
    return table