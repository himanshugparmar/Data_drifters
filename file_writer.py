# file_writer.py

def write_file(filename, text):
    with open(filename, "w") as f:
        f.write(text)
    print("File written successfully")


def read_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read()
        print("File content:")
        print(content)
    except FileNotFoundError:
        print("File not found")

def full_power(a, b):
    """Raise a to the power of b"""
    return a ** b

def single_modulus(a, b):
    """Return remainder of a divided by b"""
    if b == 0:
        return "Error: Modulus by zero"
    return a % b


if __name__ == "__main__":
    filename = "example.txt"

    write_file(filename, "Hello, this is a test file.\nPython is simple.")
    read_file(filename)
