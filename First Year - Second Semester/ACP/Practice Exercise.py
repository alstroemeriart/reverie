"""
Student Information Processor with Documentation
This program collects a student's information and computes the average of two quiz scores.
Inputs: Last name, first name, middle name, course, quiz 1 score, quiz 2 score
Outputs: Full name, course, average quiz score
"""

# This is for the collection of student information
lastName = input("Enter your last name: ")
firstName = input("Enter your first name: ")
middleName = input("Enter your middle name: ")
course = input("Enter your course: ")

# This is for the collection of quiz scores as integers
quiz1Score = int(input("Enter your quiz 1 score: "))
quiz2Score = int(input("Enter your quiz 2 score: "))

fullName = f"{lastName}, {firstName} {middleName}" # Concatenating the full name in the format "Last Name, First Name Middle Name"

totalQuizScore = quiz1Score + quiz2Score # Calculating the total quiz score by adding quiz 1 and quiz 2 scores
averageQuizScore = totalQuizScore / 2 # Calculating the average quiz score by dividing the total quiz score by 2

print("\nStudent Name: " + fullName)
print("Course: " + course)
print("Average Score: ", format(averageQuizScore, ".2f")) # Rounded to 2 decimal places