#include <stdio.h>

int propertyChoice(void);
int computePrice(void);
float computeBSD(int menu, int price);


int main() {
    int menu;

    do {
        menu = propertyChoice();

        if (menu == 3)
        {
            printf("***\nThank you for using the program.\n***\n");
            return 0;
        }

        int price = computePrice();

        if (price == 0) {
            printf("***\nInvalid Property Purchase Price. Please try again.\n***\n");
            continue;
        }

        float finalTax = computeBSD(menu, price);

        printf("***\nThe Buyer's Stamp Duty (BSD) for $%d is $%.2f\n***\n", price, finalTax);
        printf("The total price will be $%.2f\n***\n", finalTax + price);
    } while (menu != 3);

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

        if(menu < 1 || menu > 3)
        {
            printf("\nInvalid input. Please enter 1, 2, or 3.\n\n");
        }
    } while (menu < 1 || menu > 3);
    
    return menu;
}

int computePrice(void) {
    int price;

    printf("Enter the purchase price: ");
    scanf("%d", &price);

    if(price < 1)
    {
        return 0;
    }

    return price;
}

float computeBSD(int menu, int price) {   
    float tax = 0;

    if (menu == 1) {
        if (price > 600000) {
            tax = price * 0.03;
        } else if (price >= 180000 && price <= 600000) {
            tax = price * 0.02;
        } else if (price < 180000) {
            tax = price * 0.01;
        }
        else {
            printf("Invalid input\n");
        }
    } else if (menu == 2) {
    
        if (price > 600000) {
            tax = price * 0.035;
        } else if (price >= 180000) {
            tax = price * 0.025;
        } else if (price < 180000) {
            tax = price * 0.015;
        }
    }

    return tax;
}