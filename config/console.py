import os
import platform

from rich.console import Console

class CustomConsole(Console):
    def clear(self):
        """Clear the console in a cross-platform way"""
        cleared = False
        if platform.system() == "Windows":
            if os.system('cls') == 0:
                cleared = True
        if os.system('clear') == 0:
            cleared = True
        # If the system command did not work, try the ANSI sequence
        if not cleared:
            print("\033[H\033[J", end="")

# Create a unique instance of the console
console = CustomConsole()