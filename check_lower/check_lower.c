#include <ctype.h>
#include <stdio.h>

int main (void)
{
    char x;
    printf("Enter a character: ");
    scanf("%c", &x);

    if (islower(x))
    {
        printf("Lower Case\n");
    }
    else if (isupper(x))
    {
        printf("Upper Case\n");
    }
    else if (isdigit(x))
    {
        printf("Digit\n");
    }
    else
    {
        printf("Special Character\n");
    }
}