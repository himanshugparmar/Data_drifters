# calculator.py

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def divide_2(a, b):
    if b == 0:
        return "Error: Division by zero"
    return (a / b) / 2

if __name__ == "__main__":
    x = 10
    y = 5

    print("Add:", add(x, y))
    print("Subtract:", subtract(x, y))
    print("Multiply:", multiply(x, y))
    print("Divide:", divide(x, y))
    print("webhook")
