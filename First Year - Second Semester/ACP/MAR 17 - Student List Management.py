num_students = int(input("Enter the number of students: "))

students = []
for i in range(num_students):
    name = input(f"Enter name of student {i+1}: ")
    students.append(name)

print("\nCurrent list of students:")
for student in students:
    print(student)

remove_name = input("\nEnter the name of the student to remove: ")

if remove_name in students:
    students.remove(remove_name)
    print(f"{remove_name} has been removed from the list.")

    print("\nFinal list of students:")
    for student in students:
        print(student)
else:
    print("Student not found.")
    remove_name = input("\nEnter again:")