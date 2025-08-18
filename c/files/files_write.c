#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

int main() {
    struct Person person1 = {"Alice", 30};

    FILE *file = fopen("data.bin", "wb");

    if (file != NULL) {
        fwrite(&person1, sizeof(struct Person), 1, file);

        fclose(file);
    }
    return 0;
}