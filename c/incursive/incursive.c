#include <stdio.h>

int incursive(int x) {
    if (x == 0)
        return 1;
    else
        return x * incursive(x - 1);
    }

    int main() {
    int n;
    printf("Enter a number: ");
    scanf("%d", &n);
    incursive(n);

    printf("Factorial of %d is %d\n", n, incursive(n));

}