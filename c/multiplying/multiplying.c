#include <stdio.h>

int multiply(int x, int y) {
        return x * y;
    }

int main() {
    int num1, num2, result;
    printf("Enter two numbers: ");
    scanf("%d %d", &num1, &num2);
    result = multiply(num1, num2);
    printf("Result is %d\n", result);
    return 0;
}