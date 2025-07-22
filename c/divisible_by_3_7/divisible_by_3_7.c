#include <stdio.h>

int main (void)
{
    int start;
    int end;

    printf("Enter the start and end numbers: ");
    scanf("%d %d", &start, &end);

    do
    {
        for (int i = start; i <= end; i++)
        {
            if (start == 0)
            {
                start++;
            }

            else if (i % 3 == 0 || i % 7 == 0)
            {
                printf("%d ", i);
            }
        }
        printf("are divisible by 3 or 7\n");
        
        printf("Enter the start and end numbers: ");
        scanf("%d %d", &start, &end);
    }
    while (start == 0 && end == 0);
    {
        return 0;
    }
    
}