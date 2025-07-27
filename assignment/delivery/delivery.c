#include <stdio.h>

// Declaring the function to calculate the charge
float computeCharge(float weight);

int main() {
    float weight;
    float charge;

    // Looping everything to reprompt and calculate until sentinel value is entered
    do {
        // Welcome message and prompt the user to input the weight
        printf("Welcome to delivery charge calculator.\nEnter the weight in kilogram(kg).\nEnter 0 or a negative number to exit.\n");

        printf("Weight: ");
        scanf("%f", &weight);

        if(weight < 1) // To exit if the sentinel value (0 or negative number) is entered
        {
            printf("\n***\nThank you for using the software.\n***\n");
        }
        else if(weight > 25) // Catching the value more than 25kg
        {
            printf("\nWe can only deliver up to 25kg currently. Sorry.\n");
        }
        else // Calculate the weight if it is 1kg to 25kg
        {
            charge = computeCharge(weight);
            printf("\n***\nThe delivery fees for %.2fkg is $%.2f\n***\n", weight, charge);
        }
        printf("\n");
    } while (weight > 0); // Exit the program

    return 0;
}

// Calculate the charge based on a valid weight
float computeCharge(float weight) {
    float cost = 0;
    
    if(weight < 3) {
        cost = 8;
    } else if(weight <= 5) {
        cost = 12;
    } else {
        float extraWeight = weight - 5;
        cost = (extraWeight * 1.5) + 12;
    } return cost;
}