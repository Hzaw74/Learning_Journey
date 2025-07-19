#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(void)
{
    char que[100];

    printf("What do you want to ask: ");

    fgets(que, sizeof(que), stdin);

    // printf("%s\n", que);

    int count;
    
    // printf("How many possibilities: ");
    // scanf("%d", count);

    char poss1[100];
    char poss2[100];
    char poss3[100];

    printf("What is the first possibility: ");
    scanf("%s", poss1);
    
    printf("What is the second possibility: ");
    scanf("%s", poss2);

    printf("What is the third possibility: ");
    scanf("%s", poss3);

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


    printf("For the question of %s, you will most likely to %s.\n", que, answer);

}