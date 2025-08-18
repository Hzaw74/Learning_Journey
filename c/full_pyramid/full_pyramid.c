#include <stdio.h>

int main(void)
{
    int height, length;
    char space, brick;

    printf("Enter the number of rows: ");
    scanf("%d", &height);

    for (length = 1; length <= height; length++)
    {
        // idk
        for (space = height - 1; space >= length; space--)
        {
            printf(" ");
        }

        for (brick = 1; brick <= length; brick++)
        {
            printf("#");
        }
        printf("\n");
    }
}