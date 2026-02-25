#include <iostream>
#include <string>

using namespace std;

struct Student {
    char name[50];
    int rollNumber;
    int marks[5];
    int totalMarks;
};

int main() {
    Student s;
    
    cout << "Enter student details:\n";
    
    cout << "Name: ";
    cin.getline(s.name, 50);
    
    cout << "Roll Number: ";
    cin >> s.rollNumber;
    
    cout << "Enter marks for 5 subjects:\n";
    
    s.totalMarks = 0;
    for (int i = 0; i < 5; i++) {
        cout << "Subject " << i + 1 << ": ";
        cin >> s.marks[i];
        s.totalMarks += s.marks[i];
    }
    
    cout << "\nStudent details:\n";
    cout << "Name: " << s.name << endl;
    cout << "Roll Number: " << s.rollNumber << endl;
    cout << "Marks:\n";
    
    for (int i = 0; i < 5; i++) {
        cout << "Subject " << i + 1 << ": " << s.marks[i] << endl;
    }
    
    cout << "Total Marks: " << s.totalMarks << endl;
    
    return 0;
    
}