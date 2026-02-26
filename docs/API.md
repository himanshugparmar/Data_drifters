# API Documentation

Welcome to our API documentation. Here you will find comprehensive information about how to integrate and use our API effectively. This document is structured to guide you through each available method, providing detailed descriptions, usage examples, and update logs.

## Table of Contents
1. [Method Listings or Index](#method-listings-or-index)
2. [Detailed Method Descriptions](#detailed-method-descriptions)
3. [Examples](#examples)
4. [Change Log](#change-log)

---

## Method Listings or Index

- `add(a, b)` - Adds two numbers.
- `subtract(a, b)` - Subtracts the second number from the first.
- `multiply(a, b)` - Multiplies two numbers.
- `divide(a, b)` - Divides the first number by the second.
- `modulus(a, b)` - Returns the remainder of division of the first number by the second.
- **`floor_divide(a, b)` - Divides the first number by the second and rounds down to the nearest whole number.**

---

## Detailed Method Descriptions

### `add(a, b)`
Adds two numbers and returns the result.
- **Parameters:**
  - `a` (int): The first number.
  - `b` (int): The second number.
- **Returns:**
  - `int`: The sum of `a` and `b`.

### `subtract(a, b)`
Subtracts the second number from the first and returns the result.
- **Parameters:**
  - `a` (int): The first number.
  - `b` (int): The second number.
- **Returns:**
  - `int`: The difference between `a` and `b`.

### `multiply(a, b)`
Multiplies two numbers and returns the result.
- **Parameters:**
  - `a` (int): The first number.
  - `b` (int): The second number.
- **Returns:**
  - `int`: The product of `a` and `b`.

### `divide(a, b)`
Divides the first number by the second and returns the result.
- **Parameters:**
  - `a` (int): The first number.
  - `b` (int): The second number.
- **Returns:**
  - `int`: The quotient of `a` and `b`.

### `modulus(a, b)`
Returns the remainder of division of the first number by the second.
- **Parameters:**
  - `a` (int): The first number.
  - `b` (int): The second number.
- **Returns:**
  - `int`: The remainder when `a` is divided by `b`.

### **`floor_divide(a, b)`**
Divides the first number by the second and rounds down to the nearest whole number.
- **Parameters:**
  - `a` (int): The first number.
  - `b` (int): The second number.
- **Returns:**
  - `int`: The largest integer less than or equal to the division of `a` by `b`.

---

## Examples

### `add(a, b)`
```python
result = add(5, 3)
print(result)  # Output: 8
```

### `subtract(a, b)`
```python
result = subtract(5, 3)
print(result)  # Output: 2
```

### `multiply(a, b)`
```python
result = multiply(5, 3)
print(result)  # Output: 15
```

### `divide(a, b)`
```python
result = divide(5, 3)
print(result)  # Output: 1.666...
```

### `modulus(a, b)`
```python
result = modulus(5, 3)
print(result)  # Output: 2
```

### **`floor_divide(a, b)`**
```python
result = floor_divide(5, 3)
print(result)  # Output: 1
```

---

## Change Log

### Latest Updates
- **2023-XX-XX**: Introduced a new method `modulus(a, b)` for calculating the remainder of division.
- **2023-XX-XX**: Added the `floor_divide(a, b)` method for performing division that rounds down to the nearest whole number.

---

This documentation is intended to provide all necessary details to utilize our API effectively. For any further assistance, please contact our support team.