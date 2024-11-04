# Helper function to color terminal output
def add_color(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m"
    }
    end_color = "\033[0m"
    return f"{colors.get(color, '')}{text}{end_color}"


def print_color(text, color):
    print(add_color(text,color))

