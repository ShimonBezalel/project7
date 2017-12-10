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
        self.writeInit()

    def setFileName(self, file):
        """
        Sets the name of the current file the object is translating from.
        :param file: a string that represents a file name without the suffix after the dot.
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
            self.asm_file.write(
                '@' + self.findMemory(segment, index) + END_LINE +
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
                    # 'M=M-1' + END_LINE +
                    # 'A=M' + END_LINE +
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
                                    '@' + self.findMemory(segment,
                                                          index) + END_LINE +
                                    'M=D' + END_LINE)

    def findMemory(self, segment, index):
        """
        Returns the memory (variable or number) according to the given segment and index.
        :param segment: a valid memory segment.
        :param index: the index in the memory segment.
        :return: the memory (variable or number) according to the given segment and index.
        """
        if segment in MEMORY:
            return (MEMORY[segment] + END_LINE +
                    'D=M' + END_LINE +
                    '@' + str(index) + END_LINE +
                    'A=D+A')

        elif segment == 'base':
            return index

        elif segment == 'constant':
            return str(index)
        elif segment == 'static':
            return self.vm_file + "." + str(index)  # should be with point
        elif segment == 'temp':
            return str(TEMP_MEM + index)
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
            "D=A"
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
        self.asm_file.write(
            self.wrap_label(label) + END_LINE
        )

    def writeGoto(self, label):
        """
        Write the assembly code that is the translation of the goto command
        :param label: a string representing the label

        """
        # Write goto
        self.asm_file.write(
            "@" + label + END_LINE +
            "0;JMP" + END_LINE
        )

    def writeIf(self, label):
        """
        Write the assembly code that is the translation of the if-goto command
        :param label: a string representing the label

        """
        # Write conditional goto, the condition sit on stack (local?)
        self.asm_file.write(
            "@SP" + END_LINE +
            "D=M" + END_LINE +
            "@" + label + END_LINE +
            "D;JGT" + END_LINE  # Does this need to be a different command?
        )

    def writeCall(self, function_name, num_args):
        """
        Write the assembly code that is the translation of the call command
        :param function_name: string representing the name of the function
        :param num_args: number of arguments the func accepts

        """
        # Save state of calling function f
        return_address = self.func_specification(function_name, self.cur_label)
        # need to push return address somehow
        # self.writePushPop(Command.C_PUSH, MEMORY['base'], MEMORY['local'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['local'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['argument'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['this'])
        self.writePushPop(Command.C_PUSH,   MEMORY['base'],   MEMORY['that'])

        # Reposition segments for called function g
        # reposition ARG to SP - num_args - 5
        # reposition LCL to SP

        # Is the function name enough for the goto function? does it need to
        # be formatted somehow?
        self.writeGoto(function_name)

    def writeReturn(self):
        """
        Write the assembly code that is the translation of the return command

        """
        pass

    def writeFunction(self, function_name, num_args):
        """
        Write the assembly code that is the translation of the given function
        command
        :param function_name: string representing the name of the function
        :param num_args: number of arguments the func accepts

        """
        address = 0
        # Write function deceleration asm code
        self.asm_file.write(
            # do we need to save a state here?
            # Designate memory?

            # write function name as unique label
            ""
        )
        # Generate n pushes into the ARG segment
        for i in range(num_args):
            self.writePushPop(Command.C_PUSH, segment=MEMORY['argument'],
                              index=address + i)

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
