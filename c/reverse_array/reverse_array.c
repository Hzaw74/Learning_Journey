#include <stdio.h>

int main(void)
{
    int count;
    printf("How many numbers: ");
    scanf("%d", &count);

    int num[count];
    for(int k = 0; k < count; k++)
    {
        printf("%d. Enter a number: ");
        scanf("%d", num[k]);
    }

    reverse(num[count], count);

    printf("")
}

void reverse(int arr[], int n)
{
    int tmp;
    for(int i = 0, j = n -1; j > i; i++, j++)
    {
        tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
    }
}