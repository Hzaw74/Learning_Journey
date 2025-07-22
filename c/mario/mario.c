#include <stdio.h>

int main(void) {
    int x;
    printf("How many lines do you want? ");
    scanf("%d", &x);

    for (int length = 1; length <= x; length++) {
        for (int height = 1; height <= length; height++) {
            printf("#");
        }
        printf("\n");
    }
}