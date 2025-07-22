#include <stdio.h>

int main(void)
{
    int count;

    printf("How many numbers: ");
    scanf("%d", &count);

    int num[count];

    for (int i = 1; i <= count; i++)
    {
        printf("%d.Enter a number: ", i);
        scanf("%d", &num[i]);
    }
    
    printf("The reverse of numbers ");

    for (int j = 1; j <= count; j++)
    {
        printf("%d", num[j]);
    }
    printf(" is ");

    for (int k = count; k > 0; k--)
    {
        printf("%d", num[k]);
    }
    printf("\n");
}