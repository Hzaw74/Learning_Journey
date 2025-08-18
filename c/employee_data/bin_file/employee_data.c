#include <stdio.h>

struct EMPLOYEE {
    char name[50];
    int id;
    float salary;
};

int main () {
    struct EMPLOYEE employee1 = {"John", 1234, 5000};

    FILE *file = fopen("data.bin", "wb");

    if(file != NULL) {
        fwrite(&employee1, sizeof(struct EMPLOYEE), 1, file);

        fclose(file);
    }
    return 0;
}