#include <stdio.h>
#include <stdbool.h>
#include <string.h>

float total (float arr[]);
float average (float sales[]);
void sortAscending(float arr[]);
void sortDescending(float arr[]);

int main () {
    float sales[12];
    float salesCopy[12];
    int menu;
    bool firstRun = true;
    bool reEnter = false;
    bool exit = false;
    int searchOption;

    printf("Welcome to the monthly sales database\n");

    do {
        if (firstRun || reEnter)
        {
            printf("Enter sales data for 12 months:\n");
            for (int i = 0; i < 12; i++) {
                printf("Month %d: ", i + 1);
                scanf("%f", &sales[i]);
            }

            memcpy(salesCopy, sales, 12 * sizeof(float));

            firstRun = false;
            reEnter = false;
        }
        
        do {
            printf("Choose the operation:\n");
            printf("1. Total sales\n");
            printf("2. Average sales\n");
            printf("3. Search\n");
            printf("4. View sorted list\n");
            printf("5. Re-enter the sales data\n");
            printf("6. Exit\n");
            printf("Choice: ");

            scanf("%d", &menu);

            switch (menu)
            {
            case 1:
                float totalSales = total(sales);
                printf("Total sales for this month is $%.2f\n", totalSales);
                break;

            case 2:
                float averageSales = average(sales);
                printf("Average for total sales is $%.2f\n", averageSales);
                break;

            case 3:
                int searchOption;
                printf("Search Options:\n");
                printf("1. Minimun sale\n");
                printf("2. Maximum sales\n");
                printf("Choice: ");
                scanf("%d", &searchOption);

                switch (searchOption)
                {
                case 1:
                    /* code */
                    break;

                case 2:
                    break;
                
                default:
                    break;
                }
                break;

            case 4:
                
                printf("Choose an option:\n");
                printf("1. Accending list\n");
                printf("2. Decending list\n");
                printf("3. Compare accending list with original list\n");
                printf("Choice: ");
                scanf("%d", &searchOption);

                switch (searchOption)
                {
                case 1:
                    sortAscending(salesCopy);
                    break;
                
                case 2:
                    sortDescending(sales);
                    break;

                case 3:
                    break;

                default:
                    break;
                }

                break;
            
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

    printf("Thank you for using the software.\n");
    return 0;
}

float total (float arr[]) {
    float sum = 0;

    for (int i = 0; i < 12; i++)
    {
        sum += arr[i];
    }

    return sum;
}

float average (float sales[]) {
    
    return total(sales) / 12;
}

void sortAscending(float arr[]) {
    for (int i = 0; i < 11; i++) {
        for (int j = 0; j < 11 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                float temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    printf("Sales in ascending order:\n");
    for (int i = 0; i < 12; i++) {
        printf("Month %d: $%.2f\n", i + 1, arr[i]);
    }
}

void sortDescending(float arr[]) {
    for (int i = 0; i < 11; i++) {
        for (int j = 0; j < 11 - i; j++) {
            if (arr[j] < arr[j + 1]) {
                // Swap
                float temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    printf("Sales in descending order:\n");
    for (int i = 0; i < 12; i++) {
        printf("Month %d: $%.2f\n", i + 1, arr[i]);
    }
}

float searchCompare () {

}