#include <stdio.h>

int main(void)
{
    int elements;
    printf("How many elements: ");
    scanf("%d", &elements);
    
    int arr[elements];
    int x;
    
    for(int i = 0; i < elements; i++)
    {
        printf("%d. Enter a number: ", i+1);
        scanf("%d", &x);
        
        arr[i] = x;
    }
    
    for(int j = 0; j < elements; j++)
    {
        printf("%d", arr[j]);
    }
    printf("\n");
}