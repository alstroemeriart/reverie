amount = int(input("Enter withdrawal amount: "))

if amount <= 0:
    print("Invalid withdrawal amount")
elif amount <= 10000:
    print("Withdrawal Approved")
elif amount > 10000:
    print("Withdrawal Denied: Amount exceeds daily limit.")

print("Transaction processed")