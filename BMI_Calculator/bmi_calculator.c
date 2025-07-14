#include <stdio.h>

// int unit_convert(int x)

int main (void)
{
    int height, weight;
    float bmi;

    printf("Height: ");
    scanf("%d", &height);

    printf("Weight: ");
    scanf("%d", &weight);

    bmi = weight / (height * height);
    printf("Your BMI is %.2lf\n.", bmi);

    if (bmi < 18.5)
    {
        printf("Underweight");
    }

    else if (bmi < 25)
    {
        printf("Normal weight");
    }

}