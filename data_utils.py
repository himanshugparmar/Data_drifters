"""
Basic data utilities for list operations.
"""

def get_sum(numbers):
    """Calculate sum of a list of numbers."""
    return sum(numbers)

def get_average(numbers):
    """Calculate average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def get_max(numbers):
    """Find maximum value in a list."""
    if not numbers:
        return None
    return max(numbers)

def get_min(numbers):
    """Find minimum value in a list."""
    if not numbers:
        return None
    return min(numbers)

def main():
    """Demonstrate data utility functions."""
    sample_data = [10, 20, 30, 40, 50]
    
    print("Data Utilities Demo")
    print(f"Sample data: {sample_data}")
    print(f"Sum: {get_sum(sample_data)}")
    print(f"Average: {get_average(sample_data)}")
    print(f"Maximum: {get_max(sample_data)}")
    print(f"Minimum: {get_min(sample_data)}")

if __name__ == "__main__":
    main()
