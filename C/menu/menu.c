#include <stdio.h>

double factorial(double x);
int prime(int y);

int main (void)
{
    int menu;

    do
    {    
        printf("\nMenu: \n1. Factorial Calculation\n2. Prime Check\n3. Exit\nChoice: ");
        scanf("%d", &menu);


        switch (menu)
        {
        case 1:
            double num1;
            printf("Enter a number: ");
            scanf("%lf", &num1);

            double result1 = factorial(num1);
            printf("\n***\nFactorial of %.0lf is %.0lf\n***\n", num1, result1);
            break;
        
        case 2:
            int num2;/* code */
            printf("Enter a number: ");
            scanf("%d", &num2);

            int result2 = prime(num2);
            if (result2 == num2)
            {
                printf("\n***\n%d is a prime number\n***\n");
            }
            else
            {
                printf("\n***\n%d is not a prime number\n***\n");
            }
            break;
        case 3:
            printf("\n***\nThank you for using the software\n***\n");
            break;
        default:
            printf("\n***\nInvalid input. Please enter again.\n***\n");
        }
    }
    while (menu != 3);
    {
        return 0;
    }
    
}

double factorial(double x)
{
    if (x == 1 || x == 0)
    {
        return 1;
    }
    else
    {
        return x * factorial(x - 1);
    }
}

int prime(int y)
{
    if (y <= 1)
    {
        return 1;
    }
    else
    {
        for (int z = 2; z < y; z++)
        {
            if (y % z != 0)
            {
                return y;
            }
            else
            {
                return 1;
            }
        }
    }
}