#include <stdio.h>

struct EMPLOYEE {
    char name[50];
    int id;
    float salary;
};

int main() {
    struct EMPLOYEE employee1;

    FILE *file = fopen("data.csv", "r");

    if(file != NULL) {
        fread(&employee1, sizeof(struct EMPLOYEE), 1, file);

        printf("Name: %s, ID: %d, Salary: %.2f\n", employee1.name, employee1.id, employee1.salary);

        fclose(file);
    }
}