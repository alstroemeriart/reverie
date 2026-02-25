temperature = float(input("Temperature in Celsius: "))

if temperature < 36:
    print("Low Temperature")
elif temperature <= 37.5:
    print("Normal Temperature")
else:
    print("High Temperature")

print("Temperature check complete")
