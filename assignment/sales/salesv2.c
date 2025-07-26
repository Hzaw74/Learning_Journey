#include <stdio.h>
#include <stdbool.h>
#include <string.h>

struct Sale {
    int month;
    float value;
};

float total(struct Sale arr[]);
float average(struct Sale arr[]);
void sortAscending(struct Sale arr[]);
void sortDescending(struct Sale arr[]);

int main() {
    struct Sale salesOG[12];
    struct Sale salesCopy[12];
    int menu;
    bool firstRun = true;
    bool reEnter = false;
    bool exit = false;
    int searchOption;

    printf("Welcome to the monthly sales database\n");

    do {
        if (firstRun || reEnter) {
            printf("Enter sales data for 12 months:\n");
            for (int i = 0; i < 12; i++) {
                printf("Month %d: ", i + 1);
                scanf("%f", &salesOG[i].value);
                salesOG[i].month = i + 1;
                salesCopy[i] = salesOG[i];
            }
            firstRun = false;
            reEnter = false;
        }

        do {
            printf("\nChoose the operation:\n");
            printf("1. Total sales\n");
            printf("2. Average sales\n");
            printf("3. Search\n");
            printf("4. View sorted list\n");
            printf("5. Re-enter the sales data\n");
            printf("6. Exit\n");
            printf("Choice: ");
            scanf("%d", &menu);

            switch (menu) {
                case 1: {
                    float totalSales = total(salesOG);
                    printf("\nTotal sales: $%.2f\n***\n", totalSales);
                    break;
                }

                case 2: {
                    float averageSales = average(salesOG);
                    printf("\nAverage sales: $%.2f\n***\n", averageSales);
                    break;
                }

                case 3: {
                    printf("\nSearch Options:\n");
                    printf("1. Minimum sale\n");
                    printf("2. Maximum sale\n");
                    printf("3. Go back\n");
                    printf("Choice: ");
                    scanf("%d", &searchOption);

                    if (searchOption == 1) {
                        float min = salesOG[0].value;
                        int month = salesOG[0].month;
                        for (int i = 1; i < 12; i++) {
                            if (salesOG[i].value < min) {
                                min = salesOG[i].value;
                                month = salesOG[i].month;
                            }
                        }
                        printf("\nMinimum sale is $%.2f in Month %d\n***\n", min, month);
                    } else if (searchOption == 2) {
                        float max = salesOG[0].value;
                        int month = salesOG[0].month;
                        for (int i = 1; i < 12; i++) {
                            if (salesOG[i].value > max) {
                                max = salesOG[i].value;
                                month = salesOG[i].month;
                            }
                        }
                        printf("\nMaximum sale is $%.2f in Month %d\n***\n", max, month);
                    } else if (searchOption == 3) {
                        continue;
                    } else {
                        printf("Invalid option.\n");
                    }
                    break;
                }

                case 4: {
                    printf("\nSort Options:\n");
                    printf("1. Ascending\n");
                    printf("2. Descending\n");
                    printf("3. Compare Ascending with Original\n");
                    printf("4. Go back\n");
                    printf("Choice: ");
                    scanf("%d", &searchOption);

                    switch (searchOption) {
                        case 1:
                            sortAscending(salesCopy);
                            break;
                        case 2:
                            sortDescending(salesCopy);
                            break;
                        case 3:
                            printf("\nOriginal List:\n");
                            for (int i = 0; i < 12; i++) {
                                printf("Month %d: $%.2f\n", salesOG[i].month, salesOG[i].value);
                            }
                            sortAscending(salesCopy);
                            break;
                        case 4:
                            continue;
                        default:
                            printf("Invalid sort option.\n");
                            break;
                    }
                    break;
                }

                case 5:
                    reEnter = true;
                    break;

                case 6:
                    exit = true;
                    break;

                default:
                    printf("Invalid choice. Please try again.\n");
                    break;
            }
        } while (!exit && !reEnter);
    } while (!exit);

    printf("\nThank you for using the software.\n");
    return 0;
}

float total(struct Sale arr[]) {
    float sum = 0;
    for (int i = 0; i < 12; i++) {
        sum += arr[i].value;
    }
    return sum;
}

float average(struct Sale arr[]) {
    return total(arr) / 12;
}

void sortAscending(struct Sale arr[]) {
    for (int i = 0; i < 11; i++) {
        for (int j = 0; j < 11 - i; j++) {
            if (arr[j].value > arr[j + 1].value) {
                struct Sale temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    printf("\nSales in ascending order:\n");
    for (int i = 0; i < 12; i++) {
        printf("Month %d: $%.2f\n", arr[i].month, arr[i].value);
    }
}

void sortDescending(struct Sale arr[]) {
    for (int i = 0; i < 11; i++) {
        for (int j = 0; j < 11 - i; j++) {
            if (arr[j].value < arr[j + 1].value) {
                struct Sale temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    printf("\nSales in descending order:\n");
    for (int i = 0; i < 12; i++) {
        printf("Month %d: $%.2f\n", arr[i].month, arr[i].value);
    }
}
