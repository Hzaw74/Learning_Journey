#include <stdio.h>

int main(void)
{
    FILE *balance;

    balance = fopen("balance.md", "a");

    if (balance == NULL)
    {
        printf("Failed to open file");
        return 1;
    }

    char input[1000];

    printf("Enter your text: ");
    fgets(input, sizeof(input), stdin);

    fprintf(balance, input);

    fclose(balance);
}