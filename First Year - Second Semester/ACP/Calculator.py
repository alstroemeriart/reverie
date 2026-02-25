operation = input("Enter the operation (+, -, *, /, %): ")
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))

if operation == "+":
    add = num1 + num2
    print("Results: " + str(add))
elif operation == "-":
    minus = num1 - num2
    print("Results: " + str(minus))
elif operation == "*":
    multiply = num1 * num2
    print("Results: " + str(multiply))
elif operation == "/":
    divide = num1 / num2
    print("Results: " + str(divide))
elif operation == "%":
    mod = num1 % num2
    print("Results: " + str(mod))
else:
    print("Invalid operation")

print("Calculation complete")