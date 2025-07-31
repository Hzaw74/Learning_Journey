#include <stdio.h>

struct EMPLOYEE {
    char name[50];
    int id;
    float salary;
};

int main() {
    struct EMPLOYEE employee1 = {"John", 1234, 5000};

    FILE *file = fopen("data.csv", "w");

    if(file != NULL) {
        fprintf(file, );
    }

    return 0;
}