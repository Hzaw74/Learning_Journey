section .data
    ; Data Declaration
    array       db 5, 3, 7, 1, 4, 9, 2, 8, 6   ; Array of elements
    array_size  db 9                           ; Size of the array
    target      db 6                           ; Target value to search for

    ; Output Strings ($ marks end of string)
    msg_found     db 'Element found at index: $' 
    msg_not_found db 'Element not found.$'
    
section .text                   ; Code segment starts
org 100h                        ; Origin for .COM file (starts at offset 100h)

_start:
    ; 1. INITIALIZATION
    xor cx, cx                  ; Clear CX register to ensure it is empty
    mov cl, [array_size]        ; Load array size (9) into Loop Counter (CL)
    mov bl, [target]            ; Load target value (6) into BL for comparison
    mov si, array               ; Load address of 'array' into Source Index (SI)

    ; 2. SEARCH LOOP
search_loop:
    cmp cx, 0                   ; Check if counter is 0 (end of array)
    je  not_found               ; If CX is 0, target is not found, jump to exception handling
    
    mov al, [si]                ; Move value at current memory address [SI] to AL
    cmp al, bl                  ; Compare current array value (AL) with target (BL)
    je  found                   ; If Equal (ZF=1), jump to 'found' section
    
    inc si                      ; Increment SI to point to next byte in array
    dec cx                      ; Decrement loop counter
    jmp search_loop             ; Jump back to start of loop to check next item

    ; 3. TARGET FOUND LOGIC 
found:
    ; Print the "Element found..." string
    mov ah, 09h                 ; DOS Interrupt 09h: Print String
    mov dx, msg_found           ; Load address of 'msg_found' string into DX
    int 21h                     ; Execute interrupt to print string

    ; Calculate Index: Current Address (SI) - Start Address (array)
    mov ax, si                  ; Move current pointer address to AX
    sub ax, array               ; Subtract start address to get index offset
    
    ; Convert Index to ASCII for printing
    add al, '0'                 ; Add ASCII '0' (48) to integer to get char
    mov dl, al                  ; Move ASCII character to DL for printing
    mov ah, 02h                 ; DOS Interrupt 02h: Print Character
    int 21h                     ; Execute interrupt to print the number
    
    jmp exit_prog               ; Jump to exit to skip 'not_found' code

    ; 4. EXCEPTION HANDLING (NOT FOUND) 
not_found:
    mov ah, 09h                 ; DOS Interrupt 09h: Print String
    mov dx, msg_not_found       ; Load address of 'msg_not_found' string
    int 21h                     ; Execute interrupt to print error message

    ; 5. TERMINATE PROGRAM
exit_prog:
    mov ax, 4c00h               ; DOS Function 4Ch: Terminate Program
    int 21h                     ; Return control to DOS