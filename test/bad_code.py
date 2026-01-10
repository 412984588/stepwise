"""
Test file with intentional security issues for Bandit scanner validation.
This file should trigger Bandit warnings in the security_scan.yml workflow.
"""


def calculate_expression(user_input: str) -> int:
    """
    SECURITY ISSUE: Using eval() with user input.
    Bandit should flag this as B307 (Use of possibly insecure function - eval).
    """
    result = eval(user_input)  # noqa: S307 - Intentional security issue for testing
    return result


def main():
    # This should trigger a Bandit warning
    user_expression = "2+2"
    result = calculate_expression(user_expression)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
