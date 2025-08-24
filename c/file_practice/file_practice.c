#include <stdio.h>

struct Student{
    char name[100];
    int id;
    int grade;
};

int main() {
    struct Student student1 = {"Alice", 30, 6};

    FILE *file;
    file = fopen("student.bin", "wb");

    if (file != NULL) {
        fwrite(&student1, sizeof(struct Student), 1, file);
        fclose(file);
    }

    FILE *file1;
    file1 = fopen("student.bin", "rb");

    if (file1 != NULL) {
        fread(&student1, sizeof(struct Student), 1, file1);

        printf("Name: %s\nID: %d\nGrade: %d\n", student1.name, student1.id, student1.grade);

        fclose(file1);
    }
}