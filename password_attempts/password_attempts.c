#include <stdio.h>

int pin (int x);

int main (void)
{
    int password;

    password = pin(password);

    for (int i = 2; i > 0; i--)
    {
        if (password == 2222)
        {
            printf("Login Successful!\n");
            break;
        }
        else if (password != 2222)
        {
            printf("Wrong Password!\n Only %d times left to try!\n", i);
            pin(password);
        }
    }
}

int pin (int x)
{
    printf("Enter your password: ");
    scanf("%d", &x);
    return x;
}