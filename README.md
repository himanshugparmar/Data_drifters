```markdown
# Simple Python Scripts Collection

This repository contains a collection of basic Python scripts demonstrating simple functionality such as calculations, file handling, and text analysis.

---

## Files Overview

## 1. calculator.py

A basic calculator script that performs:

- Addition
- Subtraction
- Multiplication
- Division
- Modulus
- **Floor Division**
- **Square Root**
- **Full Power**

### Functions

- `add(a, b)`
- `subtract(a, b)`
- `multiply(a, b)`
- `divide(a, b)`
- `modulus(a, b)` - Returns the remainder when `a` is divided by `b`.
- **`floor_divide(a, b)`** - Performs floor division on `a` by `b`, returning the largest integer less than or equal to the division result.
- **`sqrt(x)`** - Returns the square root of `x`.
- **`full_power(a, b)`** - Raises `a` to the power of `b`, including handling of complex numbers if necessary.

### Usage Examples

#### Modulus
```python
# Example of using the modulus function
result = modulus(10, 3)
print(result)  # Output: 1
```

#### Floor Division
```python
# Example of using the floor_divide function
result = floor_divide(10, 3)
print(result)  # Output: 3
```

#### Square Root
```python
# Example of using the sqrt function
result = sqrt(16)
print(result)  # Output: 4
```

#### Full Power
```python
# Example of using the full_power function
result = full_power(2, 3)
print(result)  # Output: 8
```

---

## 2. file_writer.py

This script demonstrates how to write to and read from a text file.

### Features

- Creates a file named `example.txt`
- Writes text into the file
- Reads the file content and prints it

### Functions

- `write_file(filename, text)`
- `read_file(filename)`

---

## 3. counter.py

This script analyzes a block of text and counts:

- Number of words
- Number of characters
- Number of lines

### Functions

- `count_words(text)`
- `count_characters(text)`
- `count_lines(text)`

---

## Changelog

### Latest Updates

- Added the `modulus` function to `calculator.py` to perform modulus calculations.
- **Added the `floor_divide` function to `calculator.py` to perform floor division calculations.**
- **Added the `sqrt` function to `calculator.py` for calculating square roots.**
- **Added the `full_power` function to `calculator.py` to handle complex power calculations.**

---

## Purpose

These scripts are intended for:

- Learning basic Python concepts
- Demonstrating functions and file handling
- Simple testing and experimentation

This updated documentation includes the new `sqrt` and `full_power` methods in the `calculator.py` section, providing details about their parameters, return types, and usage examples. The changelog has been updated to reflect these additions, ensuring users are informed of the new functionalities.
```
