#include <iostream>
#include <string>

using namespace std;

struct Car {
    char brand[20];
    char model[20];
    int year;
    float mileage;
};

float calculateDepreciation(float mileage) {
    if (mileage < 10000)
        return 0.0;
    else if (mileage <= 49999)
        return 10.0;
    else if (mileage <= 99999)
        return 20.0;
    else
        return 30.0;
}

void displayCarDetails(Car car) {
    float depreciation = calculateDepreciation(car.mileage);
    
    cout << "Car Details:\n";
    cout << "Brand: " << car.brand << endl;
    cout << "Model: " << car.model << endl;
    cout << "Year: " << car.year << endl;
    cout << "Mileage: " << car.mileage << endl;
    cout << "Depreciation: " << depreciation << "%" << endl;
}

int main() {
    Car car;
    
    cout << "Enter the brand of the car: ";
    cin.getline(car.brand, 20);
    
    cout << "Enter the model of the car: ";
    cin.getline(car.model, 20);
    
    cout << "Enter the year of the car: ";
    cin >> car.year;
    
    cout << "Enter the mileage of the car: ";
    cin >> car.mileage;
    
    displayCarDetails(car);
    
    return 0;
}