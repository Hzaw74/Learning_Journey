#include <stdio.h>

int propertyChoice(void); // Declaration for function to choose 2 types of properties
int inputPrice(void); // Declaration for function to get user input for purchase price
float computeBSD(int menu, int price); // Calculate the tax based on property type and purchase price


int main() {
    int menu;

    do {
        menu = propertyChoice();

        // To exit the program if user chooses 3
        if (menu == 3) {
            printf("***\nThank you for using the program.\n***\n");
            return 0;
        }

        int price = inputPrice(); // Get purchase price by calling the input function

        // Calling the BSD calculate function and storing the return value in finalTax
        float finalTax = computeBSD(menu, price);

        printf("***\nThe Buyer's Stamp Duty (BSD) for $%d is $%.2f\n***\n", price, finalTax);
        printf("The total price will be $%.2f\n***\n", finalTax + price);
    } while (menu != 3); // Loop until sentinel value of 3 is entered

    return 0;
}

int propertyChoice(void)
{
    int menu;

    do
    {
        printf("Welcome to Buyer's Stamp Duty (BSD) calculator.\n");
        printf("1. Residential Properties\n");
        printf("2. Non-Residential Properties\n");
        printf("3. Exit\n");
        printf("Choice: ");
        scanf("%d", &menu);

        // Handelling invalid inputs and reprompt
        if(menu < 1 || menu > 3) {
            printf("\nInvalid input. Please enter 1, 2, or 3.\n\n");
        }
    } while (menu < 1 || menu > 3); // Loop until valid input is entered
    
    return menu;
}

int inputPrice(void) {
    int price;

    do {
        printf("Enter the purchase price: ");
        scanf("%d", &price);

        // To catch if the purchase price is 0 or negative
        if(price < 1) {
            printf("***\nInvalid Property Purchase Price. Please try again.\n***\n");
        };
    } while (price < 1); // Loop until a valid purchase price is entered

    return price;
}

float computeBSD(int menu, int price) {   
    float tax = 0;

    // To calculate residential property
    if (menu == 1) {
        if (price > 600000) {
            tax = price * 0.03;
        } else if (price >= 180000) {
            tax = price * 0.02;
        } else {
            tax = price * 0.01;
        }
    } else if (menu == 2) { // To calculate non-residential property
    
        if (price > 600000) {
            tax = price * 0.035;
        } else if (price >= 180000) {
            tax = price * 0.025;
        } else {
            tax = price * 0.015;
        }
    } return tax;
}