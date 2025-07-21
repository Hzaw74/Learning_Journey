#include <stdio.h>

int main (void)
{
    int n;
    int counter = 1;
    printf("Enter number of rows: ");
    scanf("%d", &n);

    for (int row = 1; row <= n; row++)
    {
        for (int height = 1; height <= row; height++)
        {
            printf("%d", counter++);
        }
        printf("\n");
    }
}