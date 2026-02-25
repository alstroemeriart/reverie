username = input("Enter your username: ")
password = input("Enter your password: ")

if username == "admin" and password == "admin123":
    print("Access granted: Administrator")
elif username == "staff" and password == "staff123":
    print("Access granted: Staff")
else:
    print("Access denied")

print("Login attempt recorded")