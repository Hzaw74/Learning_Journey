#include <stdio.h>

int main (void)
{
    int p1, p2;

    printf("Hello, Wifey <3\nWelcome to my treasure map where the treasure is my heart!\n");
    for (int i = 0; i < 3; i++)
    {
        printf("*");
    }
    printf("\n");
    
    printf("There are three ways you can choose\n(1) Snakes those have't eaten in thounsand years.\n(2) Fire\n(3) Baby tigers\n");

    printf("Which one would you choose? Type a number: ");
    scanf("%d", &p1);

    if (p1 == 1)
    {
        printf("\n\n\nSnakes are dead now. They havn't eaten for a long time!\nYou go on the path and now found that a giant is blocking a narrow path.\n");
        printf("***\n");
        printf("A wizard appears out of nowhere. He offers you two kinds of pills.\n");
        printf("(1) Invisibility pill\n");
        printf("(2) Ability to go through underground\n");
        printf("Which one would you choose to go pass the giant.\nEnter a number: ");
        scanf("%d", &p2);

        if (p2 == 1)
        {
            /* code */
            printf("***\n\n\nEventhough the giant can't see you now, it can still smells you.\n");
            printf("It eats you. Game over!!!\n");
        }
        else
        {
            printf("\n\n\nYou go pass the giant from underground safely.\n");
            printf("***\n");
            printf("You won the game!\nCongratulation, Wifey <3\nI love you so so much!!!\n");
        }
        
    }
    else if (p1 == 2)
    {
        printf("\n\n\nYou are burnt. Game over!!!\n");
    }
    else
    {
        printf("\n\n\nTigers ate you. Game over!!!\n");
    }
}