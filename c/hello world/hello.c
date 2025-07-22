#include <stdio.h>

int main() {
    int age;
    printf("What's your age? ");
    scanf("%d", &age);
    if (age > 25) {
        printf("You are old, bitch!\n");
    }
    else
        printf("You are still young, beautiful!\n");
    return 0;
}