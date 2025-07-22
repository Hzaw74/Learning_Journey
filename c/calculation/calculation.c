#include <stdio.h>

int addition(int x, int y);
int substracton(int x, int y);
int multiply(int x, int y);
float division(int x, int y);
int option(void);

int main (void)
{
    int operation;
    int a, b;

    do
    {
        operation = option();

        printf("Enter two numbers: ");
        scanf("%d %d", &a, &b);

        switch (operation)
        {
        case 1:
            printf("Result: %d\n", addition(a, b));
            break;

        case 2:
            printf("Result: %d\n", substracton(a, b));
            break;
        
        case 3:
            printf("Result: %d\n", multiply(a, b));
            break;
        
        case 4:
            printf("Result: %.2lf\n", division(a, b));
            break;
        
        default:
            break;
        }
    }
    while (operation != 5);
    {
        return 0;
    }
    
}

int option(void)
{       
        int x;
        printf("Choose an operatoin\n1. Addition\n2. Substraction\n3. Mutiplication\n4. Division\n5. Exit\nEnter a number: ");
        scanf("%d", &x);
        return x;
}

int addition(int x, int y)
{
    return x + y;
}

int substracton(int x, int y)
{
    return x - y;
}

int multiply(int x, int y)
{
    return x * y;
}

float division(int x, int y)
{
    return (float)x / y;
}