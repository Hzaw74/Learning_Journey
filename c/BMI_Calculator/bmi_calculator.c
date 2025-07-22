#include <stdio.h>

float metric (int x, int y);
float imperial (int a, int b);


int main (void)
{
    int height, weight, unit;
    float bmi;

    printf("1. Metric (kg, m)\n2. Imperial (lb, inches)\nEnter 1 or 2: ");
    scanf("%d", &unit);

    printf("Weight: ");
    scanf("%d", &weight);

    printf("Height: ");
    scanf("%d", &height);

    if (unit == 1)
    {
        bmi = metric (weight, height);
    }

    else
    {
        bmi = imperial (weight, height);
    }

    if (bmi < 18.5)
    {
        printf("Underweight\n");
    }

    else if (bmi < 25)
    {
        printf("Normal weight\n");
    }

    else if(bmi <= bmi)
    {
        printf("Overweight\n");
    }
    else
    {
        printf("Obese\n");
    }
}

float metric (int x, int y)
{
    float z = x / (y * y);
    return z;
}

float imperial (int a, int b)
{
    float c = 703 * (a / (b * b));
    return c;
}