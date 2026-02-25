tempValue = float(input("Enter a temperature value: "))
unit = input("What is the unit of the temperature value> (C/F): ").lower()

if unit == "c":
    Fahrenheit = (tempValue * 9/5) + 32
    print(str(Fahrenheit) + " F")
else:
    Celcius = (tempValue - 32) * 5/9
    print(str(Celcius) + " C")

print("That is your converted temperature.")