"""
Trisha Loraine P. Relativo - CS1203
"""

password = input("Enter your password: ")

if len(password) < 8:
    password = input("Enter password again: ")

print("Password check completed")