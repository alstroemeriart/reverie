#include <iostream>
#include <string>
#include <cmath>

using namespace std;

struct Person {
    string name;
    int age;
};

int main() {
    int n;
    cout << "Enter the number of people: ";
    cin >> n;
    cin.ignore();

    Person people[100];
    int sum = 0;

    for (int i = 0; i < n; i++) {
        cout << "Enter name of person " << i + 1 << ": ";
        getline(cin, people[i].name);
        cout << "Enter age of person " << i + 1 << ": ";
        cin >> people[i].age;
        cin.ignore();
        sum += people[i].age;
    }

    double avgFloatDivision = static_cast<double> (sum) / n;

    cout << "\nThe average age of the people is " << round(avgFloatDivision) << endl;

    return 0;
}
