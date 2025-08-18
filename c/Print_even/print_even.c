#include <stdio.h>

int main(void)
{
    int start, end;
    printf("Enter two numbers: ");
    scanf("%d %d", &start, &end);
    // printf("%d %d", start, end);

    if (start % 2 == 0)
    {
        for (int x = start; x <= end; x = x + 2)
        {
            printf("%d\n", x);
        }
    }
    else
    {
        start++;
        for (int y = start; y <= end; y = y + 2)
        {
            printf("%d\n", y);
        }
    }
}