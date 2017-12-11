from Parser import *

END_LINE = '\n'
TEMP_MEM = 5

MEMORY = {'local': 'LCL',
          'argument': 'ARG',
          'this': 'THIS',
          'that': 'THAT',
          }

#
USING_FALSE_ACTION = ['eq', 'gt', 'lt']

#
D_ARG1_M_ARG2 = ('@SP' + END_LINE +
                 'M=M-1' + END_LINE +
                 'A=M' + END_LINE +
                 'D=M' + END_LINE +
                 '@SP' + END_LINE +
                 'A=M-1' + END_LINE)

#
FALSE_ACTION = ('(FALSE)' + END_LINE +
                '@SP' + END_LINE +
                'A=M-1' + END_LINE +
                'M=0' + END_LINE +
                '@currLine' + END_LINE +
                'A=M' + END_LINE +
                '0;JMP' + END_LINE)

#
COMEBACK_LINE = ('D=A' + END_LINE +
                 '@currLine' + END_LINE +
                 'M=D' + END_LINE)

#
ARITHMETIC_C = {'add': (D_ARG1_M_ARG2 +
                        'M=M+D' + END_LINE),
                'sub': (D_ARG1_M_ARG2 +
                        'M=M-D' + END_LINE),
                'neg': ('@SP' + END_LINE +
                        'A=M-1' + END_LINE +
                        'M=-M' + END_LINE),
                'and': (D_ARG1_M_ARG2 +
                        'M = D&M' + END_LINE),
                'or': (D_ARG1_M_ARG2 +
                       'M = D|M' + END_LINE),
                'not': ('@SP' + END_LINE +
                        'A=M-1' + END_LINE +
                        'M=!M' + END_LINE)}

#
JUMP_C = {'eq': 'D;JNE',
          'gt': 'D;JLE',
          'lt': 'D;JGE'}


class CodeWriter:
    """
     An object that gets an out put file and each time the suitable function for a command is used
     translates the command to assembler, and write it to the output file.
    """

    def __init__(self, file):
        """
        Initialize a CodeWriter object.
        :param file: the file the object will write the translation to.
        """
        self.asm_file = open(file, 'w')
        self.num_LTR = 0
        self.num_RA = 0
        self.writeInit()

        # Some initialization of function name. this may be extra
        self.cur_func = "Main.main"

    def setFileName(self, file):
        """
        Sets the name of the current file the object is translating from.
        :param file: a string that represents a file name without the suffix
        after the dot.
        """
        self.vm_file = file

    def writeArithmetic(self, command):
        """
        Writes the assembly code that is the translation of the given arithmetic command.
        :param command: the arithmetic command that will be executed on the stack.
        """
        if command in USING_FALSE_ACTION:

            self.asm_file.write('@LTR_' + str(self.num_LTR) + END_LINE +
                                COMEBACK_LINE +
                                D_ARG1_M_ARG2 +
                                'D=M-D' + END_LINE +
                                '@FALSE' + END_LINE)

            self.asm_file.write(JUMP_C[command] + END_LINE +
                                '@SP' + END_LINE +
                                'A=M-1' + END_LINE +
                                'M=1' + END_LINE +
                                'M=-M' + END_LINE +
                                '(LTR_' + str(self.num_LTR) + ')' + END_LINE)
            self.num_LTR += 1
        else:
            self.asm_file.write(ARITHMETIC_C[command])

    def writePushPop(self, command, segment, index):
        """
        Writes the assembly code that is the translation of the given command,
        where command is either C_PUSH or C_POP.
        :param command: its C_PUSH or C_POP type command.
        :param segment: the memory segment name.
        :param index: the index in the given segment.
        """
        if command == Command.C_PUSH:
            value_line = 'D=A' if segment == 'constant' else 'D=M'
            self.asm_file.write('@' + self.findMemory(segment, index) + END_LINE +
                                value_line + END_LINE +
                                '@SP' + END_LINE +
                                'A=M' + END_LINE +
                                'M=D' + END_LINE +
                                '@SP' + END_LINE +
                                'M=M+1' + END_LINE)

        elif command == Command.C_POP and segment != 'constant':
            if segment in MEMORY:
                self.asm_file.write(
                    '@' + self.findMemory(segment, index) + END_LINE +
                    'D=A' + END_LINE +
                    '@R13' + END_LINE +
                    'M=D' + END_LINE +
                    '@SP' + END_LINE +
                    'AM=M-1' + END_LINE +
                    'D=M' + END_LINE +
                    '@R13' + END_LINE +
                    'A=M' + END_LINE +
                    'M=D' + END_LINE)

            else:
                self.asm_file.write('@SP' + END_LINE +
                                    'AM=M-1' + END_LINE +
                                    # 'M=M-1' + END_LINE +
                                    # 'A=M' + END_LINE +
                                    'D=M' + END_LINE +
                                    '@' + self.findMemory(segment, index) + END_LINE +
                                    'M=D' + END_LINE)

    def findMemory(self, segment, index):
        """
        Returns the memory (variable or number) according to the given segment and index.
        :param segment: a valid memory segment.
        :param index: the index in the memory segment.
        :return: the memory (variable or number) according to the given segment and index.
        """
        # adds the segment address to the index and go to there
        if segment in MEMORY:
            return (MEMORY[segment] + END_LINE +
                    'D=M' + END_LINE +
                    '@' + str(index) + END_LINE +
                    'A=D+A')
        # returns the index, usually in this case - segment 0
        elif segment == 'base':
            return index
        # if the index>0 return it otherwise return -index and than make the number negative
        # by A=-A
        elif segment == 'constant':
            return (str(-index) + END_LINE + 'A=-A') if index < 0 else str(index)
        # return file_input.index
        elif segment == 'static':
            return self.vm_file + "." + str(index)
        # in the temp segment that starts at place 5 in the memory, so 5 added to the given index
        elif segment == 'temp':
            return str(TEMP_MEM + index)
        # when the segment=pointer, if 1 returns 'that' else returns 'false'
        else:
            if index:
                return 'THAT'
            else:
                return 'THIS'

    def close(self):
        """
        Adding some suffix commands and closing the output file.
        """
        self.asm_file.write('@END' + END_LINE +
                            '0;JMP' + END_LINE)
        if self.num_LTR > 0:
            self.asm_file.write(FALSE_ACTION)
        self.asm_file.write('(END)' + END_LINE)
        self.asm_file.close()

    def writeInit(self):
        """
        Write the assembly code tht effects the VM init, also called the
        bootstrap code. This goes in the beginning of output file

        """
        # Set SP to 256
        self.asm_file.write(
            "@256" + END_LINE +
            "D=A" + END_LINE +
            "@SP" + END_LINE +
            "M=D" + END_LINE
        )
        # Call Sys.init and Main.main within
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label):
        """
        Write the assembly code that is the translation of the label command
        :param label: a string representing the label

        """
        # Write a label deceleration
        unique_label = self.cur_func + "$" + label
        self.asm_file.write(
            self.wrap_label(unique_label) + END_LINE
        )

    def writeGoto(self, label, function=False):
        """
        Write the assembly code that is the translation of the goto command
        :param label: a string representing the label

        """
        # Generate agreed upon unique label
        unique_label = self.pad_label(label=label, function=function)

        # Write goto
        self.asm_file.write(
            "@" + unique_label + END_LINE +
            "0;JMP" + END_LINE
        )

    def writeIf(self, label):
        """
        Write the assembly code that is the translation of the if-goto command
        :param label: a string representing the label

        """
        # Generate agreed upon unique label
        unique_label = self.pad_label(label)

        # Write conditional goto, the condition sit on stack (local?)
        self.asm_file.write(
            "@SP" + END_LINE +
            "AM=M-1" + END_LINE +
            "D=M" + END_LINE +
            # "D=M" + END_LINE +
            "@" + unique_label + END_LINE +
            "D;JLT" + END_LINE  # If True (-1) then it is less than 0 and
            # must jump
        )

    def writeCall(self, function_name, num_args):
        """
        Write the assembly code that is the translation of the call command
        :param function_name: string representing the name of the function
        :param num_args: number of arguments the func accepts

        """
        # Save state of calling function f
        # return_address = self.func_specification(function_name, self.cur_label)
        # need to push return address somehow
        # self.writePushPop(Command.C_PUSH, MEMORY['base'], MEMORY['local'])

        # pushing all the current values of the method to the stack
        return_adress = "returnAddress_" + str(self.num_RA)
        self.writePushPop(Command.C_PUSH, MEMORY['base'], return_adress)
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['local'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['argument'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['this'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['that'])

        # reposition LCL to SP, ARG to SP - num_args - 5
        self.asm_file.write('@SP' + END_LINE +
                            'D=M' + END_LINE +
                            '@LCL' + END_LINE +
                            'M=D' + END_LINE +
                            '@5' + END_LINE +
                            'D=D-A' + END_LINE +
                            '@' + str(num_args) + END_LINE +
                            'D=D-A' + END_LINE +
                            '@ARG' + END_LINE +
                            'M=D' + END_LINE)

        self.writeGoto(function_name, True)
        self.asm_file.write(self.wrap_label(return_adress))
        self.num_RA += 1


    def writeReturn(self):
        """
        Write the assembly code that is the translation of the return command

        """
        self.asm_file.write('@LCL' + END_LINE + # frame = LCL
                            'D=M' + END_LINE +
                            '@frame' + END_LINE +
                            'M=D' + END_LINE +
                            '@5' + END_LINE + # retAddr = *(frame-5)
                            'A=D-A' + END_LINE +
                            'D=M' + END_LINE +
                            '@retAddr' + END_LINE +
                            'M=D' + END_LINE
                            # '@SP' + END_LINE + # *ARG = pop
                            # 'AM=M-1' + END_LINE +
                            # 'D=M' + END_LINE +
                            # '@ARG' + END_LINE +
                            # 'A=M' + END_LINE +
                            # 'M=D' + END_LINE)
                            )
        self.writePushPop(Command.C_POP, MEMORY['argument'], 0) # *ARG = pop
        self.asm_file.write('@ARG' + END_LINE +  # SP = ARG + 1
                            'D=M+1' + END_LINE +
                            '@SP' + END_LINE +
                            'M=D' + END_LINE)

        # restores the caller's THAT, THIS, ARG, LCL
        for seg in ['THAT', 'THIS', 'ARG', 'LCL']: # make sure it works correctly
            self.fromFrameToVal(seg)

        self.writeGoto('retAddr')

    def fromFrameToVal(self, val):
        self.asm_file.write('@frame' + END_LINE +
                            'AM=M-1' + END_LINE +
                            'D=M' + END_LINE +
                            '@' + val + END_LINE +
                            'M=D' + END_LINE)


    def writeFunction(self, function_name, num_args):
        """
        Write the assembly code that is the translation of the given function
        command
        :param function_name: string representing the name of the function
        :param num_args: number of arguments the func accepts

        """
        self.cur_func = function_name
        # address = 0
        # # Write function deceleration asm code
        # self.asm_file.write(
        #     # do we need to save a state here?
        #     # Designate memory?
        #
        #     # write function name as unique label
        #     ""
        # )

        self.asm_file.write(self.wrap_label(self.pad_label()))

        # Generate n pushes into the ARG segment
        for i in range(num_args):
            self.asm_file.write('@SP' + END_LINE +
                                'A=M' + END_LINE +
                                'M=0' + END_LINE +
                                '@SP' + END_LINE +
                                'M=M+1' + END_LINE)

    @staticmethod
    def func_specification(function_name, label):
        """
        Generates a unique function symbol for the asm code in the format:
        f$b where f is the function name and b is the label symbol within VM
        function code.
        These full specifications must be used in goto and ifgoto usage
        :param function_name:
        :param label:
        :return: "f$b"
        """
        return function_name + "$" + label

    @staticmethod
    def wrap_label(label_name):
        """
        Wraps f in (f) generating a suggestion to asm to save code segment as f
        :param label_name:
        :return:
        """
        return "(" + label_name + ")"

    def pad_label(self, label="", function=True):
        """

        :param label:
        :return:
        """
        if function:
            return self.vm_file + "." + self.cur_func
        return self.vm_file + "." + self.cur_func + "$" + label
