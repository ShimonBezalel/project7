// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/07/StackArithmetic/SimpleAdd/SimpleAdd.tst

load my_test.asm,
output-file my_test.out,
compare-to my_test.cmp,
output-list RAM[0]%D2.6.2 RAM[256]%D2.6.2;

set RAM[0] 256,  // initializes the stack pointer 

repeat 60 {      // enough cycles to complete the execution
  ticktock;
}

output;          // the stack pointer and the stack base
