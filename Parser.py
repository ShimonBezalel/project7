"""
Parser for Nand to Tetris project7, HUJI

Parses from VM language to .asm code
Author: Shimon Heimowitz

"""
from enum import Enum, unique


class Command(Enum):
    """
    Enumerator holding values for various vm command types

    """
    C_ARITHMETIC = ""
    C_PUSH = "push"
    C_POP = "pop"
    C_LABEL = "label"
    C_GOTO = "goto"
    C_IF = "if-goto"
    C_FUNCTION = "function"
    C_RETURN = "return"
    C_CALL = "call"
    UNKNOWN = "error"


@unique
class Arithmetic(Enum):
    """
    Enumerator holding values for various vm arithmetic commands

    """

    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"


class Parser:
    """
    Parser class.  Parse one file at a time.

    """

    EMPTY_LINE = ""
    COMMENT = "//"
    NEW_LINE = "\n"
    SPACE = " "

    C_TYPE = 0
    FIRST_ARG = 1
    SECOND_ARG = 2

    def __init__(self, file):
        """
        Opens the input file/stream and gets ready to parse it.
        :param input_file:
        """
        with open(file) as fp:
            self.lines = [line.rstrip(self.NEW_LINE) for line in fp]

        self.clean_lines()
        self.len = self.lines.__len__()

        # Initialize an iterator of the list
        self.lines_iter = iter(self.lines)
        self.first_arg = None
        self.second_arg = None
        self.type = Command.UNKNOWN

    def clean_lines(self):
        """
        Cleans all irrelevant comments and empty lines from the list of lines.
        Lines will only hold real command lines after cleaning.
        """
        for i in range(self.lines.__len__()):
            # remove white space
            # self.lines[i] = self.lines[i].replace(" ", "")

            # convert all comment sections into empty strings
            comment_index = self.lines[i].find(self.COMMENT)
            if comment_index >= 0:  # comment found inline or whole line
                self.lines[i] = self.lines[i][:comment_index]

        # remove all empty lines
        self.lines = [line for line in self.lines if line != self.EMPTY_LINE]

    def hasMoreCommands(self):
        """
        Are there more commands in the input?
        :return: boolean value, True iff there are more commands
        """
        try:
            self.cur = next(self.lines_iter)
        except StopIteration:
            return False
        return True

    def advance(self):
        """
        Reads the next command from the input and makes it the current command.
        Should be called only if hasMoreCommands is true.
        Initially there is no current command.

        """
        pass

    def commandType(self):
        """
        Returns the type of the current VM command.
        C_ARITHMETIC is returned for all the arithmetic commands.
        :return: One of the following: Command.###
        C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION,
        C_RETURN, C_CALL
        """
        args = self.cur.split(self.SPACE)

        if args[self.C_TYPE] == Command.C_PUSH.value:
            self.type = Command.C_PUSH
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = args[self.SECOND_ARG]
            return Command.C_PUSH

        if args[self.C_TYPE] == Command.C_POP.value:
            self.type = Command.C_POP
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = args[self.SECOND_ARG]
            return Command.C_POP

        if args[self.C_TYPE] == Command.C_RETURN.value:
            self.type = Command.C_RETURN
            self.first_arg = None
            self.second_arg = None
            return Command.C_RETURN

        if args[self.C_TYPE] == Command.C_GOTO.value:
            self.type = Command.C_GOTO
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = None
            return Command.C_GOTO

        if args[self.C_TYPE] == Command.C_IF.value:
            self.type = Command.C_IF
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = None
            return Command.C_IF

        if args[self.C_TYPE] == Command.C_LABEL.value:
            self.type = Command.C_LABEL
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = None
            return Command.C_LABEL

        if args[self.C_TYPE] == Command.C_FUNCTION.value:
            self.type = Command.C_FUNCTION
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = args[self.SECOND_ARG]
            return Command.C_FUNCTION

        if args[self.C_TYPE] == Command.C_CALL.value:
            self.type = Command.C_CALL
            self.first_arg = args[self.FIRST_ARG]
            self.second_arg = args[self.SECOND_ARG]
            return Command.C_CALL

        for operand in Arithmetic:
            if self.cur.startswith(operand.value):
                self.type = Command.C_ARITHMETIC
                self.first_arg = operand.value
                return Command.C_ARITHMETIC

        self.type = Command.UNKNOWN
        return Command.UNKNOWN

    def arg1(self):
        """
        Returns the first arg. of the current command.
        In the case of C_ARITHMETIC, the command itself
        (add, sub, etc.) is returned. Should not be called
        if the current command is C_RETURN.
        :return: string
        """
        assert self.type != Command.C_RETURN

        # if self.type == Command.C_ARITHMETIC or self.type == Command.C_PUSH \
        #         or self.type == Command.C_POP:
        return self.first_arg

        # return Command.UNKNOWN.name

    def arg2(self):
        """
        Returns the second argument of the current
        command. Should be called only if the current
        command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        :return:  int
        """

        assert self.type == Command.C_FUNCTION or self.type == Command.C_PUSH \
               or self.type == Command.C_POP or self.type == Command.C_CALL

        return int(self.second_arg)


if __name__ == "__main__":
    pass
