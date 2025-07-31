#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

int main() {
    struct Person person1;

    FILE *file = fopen("data.bin", "rb");

    if (file != NULL) {
        fread(&person1, sizeof(struct Person), 1, file);
    
        printf("Name: %s, Age: %d\n", person1.name, person1.age);

        fclose(file);
    }
    return 0;
}