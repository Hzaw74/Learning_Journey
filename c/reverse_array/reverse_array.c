#include <stdio.h>

int main(void)
{
    // int size1 = 5;
    // int size2 = 5;

    int arr1[5] = {1, 2, 3, 4, 5};
    int arr2[5];

    int tem;

    for(int i = 0; i < 5; i++)
    {
        arr1[i] = tem;
        
        for(int j = 5; j > 0; j--)
        {
            arr2[j] = tem; 
        }
    }

    for(int k = 0; k < 5; k++)
    {
        printf("%d\n", arr2[k]);
    }
}