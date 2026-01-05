section .data
	hello db 'Hello, World!$', 0

section .text
	org 0x100

_start:	
	mov dx, hello
	mov ah, 9
	int 0x21

	; Exit the program
	mov ax, 0x4C00
	int 0x21