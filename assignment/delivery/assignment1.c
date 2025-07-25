#include <stdio.h>

float computeCharge(float weight);

int main() {
    float weight;
    float charge;

    do
    {
        printf("Welcome to delivery charge calculator. Enter the weight in kilogram(kg) or enter 0 to exit\n");

        printf("Weight: ");
        scanf("%f", &weight);

        if(weight == 0)
        {
            printf("\n***\nThank you for using the software\n***\n");
        }
        else if(weight < 0)
        {
            printf("\nInvalid weight\n");
            break;
        }
        else if(weight > 25)
        {
            printf("\nWe can only deliver up to 25kg currently. Sorry.\n");
        }
        else if(weight > 0 && weight <= 25)
        {
            charge = computeCharge(weight);
            printf("\n***\nThe delivery fees for %.2fkg is $%.2f\n***\n", weight, charge);
        }
        else
        {
            printf("Invalid input");
        }
        printf("\n");
    } while (weight != 0);
}

float computeCharge(float weight) {
    float cost = 0;
    
    if(weight > 5)
    {
        float extraWeight = weight - 5;
        cost = (extraWeight * 1.5) + 12;
    }
    else if(weight <= 5 && weight >= 3)
    {
        cost = 12;
    }
    else if (weight < 3)
    {
        cost = 8;
    }
    return cost;
}