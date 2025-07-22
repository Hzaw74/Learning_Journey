#include <ctype.h>
#include <stdio.h>

char user (char y);

int main (void)
{
    char x;

    do
    {
        x = user (x);
        // printf("ASCII: %d\n", x);

        if (islower(x))
        {
            printf("***\nLower Case\n***\n");
        }
        else if (isupper(x))
        {
            printf("***\nUpper Case***\n\n");
        }
        else if (isdigit(x))
        {
            printf("***\nDigit\n***\n");
        }
        else
        {
            printf("***\nSpecial Character\n***\n");
        }
        printf("Type 'A' to exit\n");
    }
    
    while (x != 'A');
    {
        return 1;
    }
}

char user (char y)
{
    printf("Enter a character: ");
    scanf(" %c", &y);
    return y;
}