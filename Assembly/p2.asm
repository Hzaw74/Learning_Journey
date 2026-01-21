section .data
    prompt_message db 'Please enter a character: $'
    suc_message db 'Successful$'
    err_message db 'Error! Please enter 0-9$'
    new_line db 0Dh, 0Ah
    even db 'Its even number.$'
    odd db 'Its odd number.$'
    result db 0

section .bss
    input resb 1

section .text
    org 0x100

_start:
    mov dx, prompt_message
    mov ah, 09h
    int 21h

    mov ah, 02h
    mov dl, [new_line]
    int 21h
    
    mov dl, [new_line+1]
    int 21h

    mov ah, 01h
    int 21h
    mov [input], al

    cmp byte [input], '0'
    jl invalid

    cmp byte [input], '9'
    jg invalid

    mov ah, 02h
    mov dl, [new_line]
    int 21h
    
    mov dl, [new_line+1]
    int 21h

    mov dx, suc_message
    mov ah, 09h
    int 21h
    ; jmp exit

    mov ah, 02h
    mov dl, [new_line]
    int 21h
    
    mov dl, [new_line+1]
    int 21h

    xor ah, ah
    mov al, [input]
    xor dx, dx
    mov bl, 2
    div bl

    cmp ah, 0
    je even_message
    jne odd_message

odd_message:
    mov dx, odd
    mov ah, 09h
    int 21h
    jmp exit

even_message:
    mov dx, even
    mov ah, 09h
    int 21h
    jmp exit

invalid:
    mov ah, 02h
    mov dl, [new_line]
    int 21h
    
    mov dl, [new_line+1]
    int 21h
    
    mov dx, err_message
    mov ah, 09h
    int 21h
    jmp exit

exit:
    mov ah, 02h
    mov dl, [new_line]
    int 21h
    
    mov dl, [new_line+1]
    int 21h

    mov ah, 4Ch
    int 21h
