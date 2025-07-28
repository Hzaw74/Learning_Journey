#include <stdio.h>
#include <stdbool.h>
#include <string.h>

struct Sale {
    int month;
    float value;
};

float total(struct Sale arr[]); // Declaration for the function to calculate total sales
float average(struct Sale arr[]); // Declaration for the function to calculate average sales
void searchBySale(struct Sale arr[]); // Declaraton for the function to find the months with user requested sales value
void sortAscending(struct Sale arr[]); // Declaration for the function to sort the data in ascending order
void sortDescending(struct Sale arr[]); // Declaration for the function to sort the data in descending order

int main() {
    struct Sale salesOG[12]; // Original sales value for 12 months
    struct Sale salesCopy[12]; // A copy to use in sorting, to protect the original data

    int menu;
    bool firstRun = true; // To run once at first time and only first time
    bool reEnter = false; // Initializing the boolean value to false, will update this if user wants to reenter the sales value
    bool exit = false; // Initializing the boolean value to false, will update this if user wants to exit the program
    int searchOption;

    printf("Welcome to the monthly sales database\n");

    do {
        if (firstRun || reEnter) { // To run at first time or if the user chooses to reenter the sales value
            printf("Enter sales data for 12 months:\n");
            for (int i = 0; i < 12; i++) {
                printf("Month %d: ", i + 1);
                scanf("%f", &salesOG[i].value);
                salesOG[i].month = i + 1; // Assign month number (1 to 12)
                salesCopy[i] = salesOG[i]; // To copy each month sales from original to a copy
            }
            firstRun = false; // Updating to indicate that already ran for the first time
            reEnter = false; // Resetting the reenter value
        }

        // Main menu
        do {
            printf("\nChoose a operation:\n");
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
                
                // Search for month with minimum, maximum, or a specific sales value
                case 3: {
                    printf("\nSearch Options:\n");
                    printf("1. Minimum sale\n");
                    printf("2. Maximum sale\n");
                    printf("3. Search month by sales value\n");
                    printf("4. Go back\n");
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
                            searchBySale(salesOG);
                    } else if (searchOption == 4) {
                        continue; // Skip to next iteration to go back to main menu
                    } else {
                        printf("Invalid option.\n");
                    }
                    break;
                }

                case 4: {
                    printf("\nSort Options:\n");
                    printf("1. Ascending\n");
                    printf("2. Descending\n");
                    printf("3. Compare Ascending list with Original\n");
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
                            continue; // Skip to next iteration to go back to main menu
                        default:
                            printf("Invalid sort option.\n");
                            break;
                    }
                    break;
                }

                case 5:
                    reEnter = true; // Updating the boolean to true to reenter sales data
                    break;

                case 6:
                    exit = true; // Updating the boolean to true to exit the program/ loop
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

// Calculates the total sales from an array of Sale structs
float total(struct Sale arr[]) {
    float sum = 0;
    for (int i = 0; i < 12; i++) {
        sum += arr[i].value;
    }
    return sum;
}

// Calculates the average sales
float average(struct Sale arr[]) {
    return total(arr) / 12;
}

// Search month by sales
void searchBySale(struct Sale arr[]) {
    float searchValue;
    bool found = false;
    bool searchFirstRun = true;

    printf("Enter the value to search for: ");
    scanf("%f", &searchValue);

    for(int i = 0; i < 12; i++) {
        if(arr[i].value == searchValue) {
            if(searchFirstRun) {
                printf("\nMonth(s) with sales value $%.2f:\n", searchValue);
                searchFirstRun = false;
            }
            printf("Month: %d\n", arr[i].month);
            found = true;
        }
    }

    if (!found) {
        printf("\n***\nNo month found with sale value $%.2f\n***\n", searchValue);
    }
}

// Sorts sales data in ascending order by value using Bubble Sort
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

// Sorts sales data in descending order by value using Bubble Sort
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