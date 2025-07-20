#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(void)
{
    char que[100];

    printf("What do you want to ask: ");

    fgets(que, sizeof(que), stdin);

    char poss1[100];
    char poss2[100];
    char poss3[100];

    printf("What is the first possibility: ");
    fgets(poss1, sizeof(poss1), stdin);
    
    printf("What is the second possibility: ");
    fgets(poss2, sizeof(poss2), stdin);

    printf("What is the third possibility: ");
    fgets(poss3, sizeof(poss3), stdin);

    srand(time(0));

    int chance = (rand() % 3) + 1;

    char answer[100];

    if(chance == 1)
    {
        strcpy(answer, poss1);
    }
    else if(chance == 2)
    {
        strcpy(answer, poss2);
    }
    else
    {
        strcpy(answer, poss3);
    }

    printf("For the question of %s, it will most likely to be %s\n.", que, answer);

}