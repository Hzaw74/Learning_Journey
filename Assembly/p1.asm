org 100h

section .text
_start:
    mov ah, 5
    mov dl, 2

    mov ax, 09h
    mov dx, ah
    int 21h