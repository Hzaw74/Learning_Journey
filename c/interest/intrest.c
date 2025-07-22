#include <stdio.h>

double cal_principle(double x, double y, int z);
void display_result(double a);

int main (void)
{
    double principle, rate;
    int time;

    printf("Enter principle, rate and time: ");
    scanf("%lf %lf %d", &principle, &rate, &time);

    double interest = cal_principle (principle, rate, time);
    display_result(interest);
}

double cal_principle(double x, double y, int z)
{
    return x * y / 100;
}

void display_result(double a)
{
    printf("Interest: %.2f\n", a);
}