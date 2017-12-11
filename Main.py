"""
Main for Nand to Tetris project7, HUJI

Runs multiple conversions from .vm (virtual machine language) files to .asm
language files.
Authors: Shimon Heimowitz, Karin Sorokin

"""

import sys
import os
import traceback
from Parser import Parser, Command, Arithmetic
from CodeWriter import CodeWriter

FILE_PATH = 1

FILE_EXTENSION_ASM = '.asm'
FILE_EXTENSION_VM = '.vm'


def main(path):
    """
    Main translater. Checks legality of arguments and operates on directory
    or file accordingly.
    :param path: argument
    """
    vm_files = []
    if not os.path.exists(path):
        print("Error: File or directory does not exist: %s"
              % path)
        return

    elif os.path.isdir(path):  # Directory of files
        vm_files = filter_paths(path)
        dir_path = path
        file_name = os.path.basename(path) + FILE_EXTENSION_ASM
        if not vm_files:  # no vm files found
            print("Error: No files matching %s found in supplied "
                  "directory: %s" % (FILE_EXTENSION_VM, path))
            return

    elif os.path.isfile(path):  # Single file
        if not path.endswith(FILE_EXTENSION_VM):
            print("Error: Mismatched file type.\n\"%s\"suffix is not a valid "
                  "file type. Please supply .vm filename or dir." % path)
            return
        vm_files.append(path)
        dir_path = os.path.dirname(path)
        file_name = os.path.splitext(os.path.basename(path))[0] + \
                    FILE_EXTENSION_ASM

    else:
        print("Error: Unrecognized path: \"%s\"\n"
              "Please supply dir or path/filename.vm")
        return

    try:
        writer = CodeWriter(os.path.join(dir_path, file_name))
        for vm_file in vm_files:
            translate_file(vm_file, writer)
        writer.close()

    except OSError:
        print("Could not open some file.\n "
              "If file exists, check spelling of file path.")
        return

    except Exception as e:
        print("Some exception occurred while parsing.", e)
        traceback.print_exc()
        return


def filter_paths(path):
    """
    Filter vm file paths in case a directory path is supplied
    """
    return ["{}/{}".format(path, f) for f in os.listdir(path) if
            f.endswith(FILE_EXTENSION_VM)]


def translate_file(path, writer):
    """
    Translates from virtual machine language files and creates a relevant .asm
    file.
    :param path: Path of current file to translate
    :param writer: A write to translate all files.
    :return:
    """
    parser = Parser(path)
    parsed_name = os.path.splitext(os.path.basename(path))[0]
    writer.setFileName(parsed_name)
    while parser.hasMoreCommands():
        parser.advance()
        if parser.commandType() == Command.C_ARITHMETIC:
            writer.writeArithmetic(parser.arg1())
        if parser.commandType() in (Command.C_PUSH, Command.C_POP):
            writer.writePushPop(parser.commandType(),
                                parser.arg1(), parser.arg2())
        if parser.commandType() == Command.C_LABEL:
            writer.writeLabel(parser.arg1())

        if parser.commandType() == Command.C_GOTO:
            writer.writeGoto(parser.arg1())

        if parser.commandType() == Command.C_IF:
            writer.writeIf(parser.arg1())

        if parser.commandType() == Command.C_RETURN:
            writer.writeReturn()

        if parser.commandType() == Command.C_CALL:
            writer.writeCall(parser.arg1(), parser.arg2())

        if parser.commandType() == Command.C_FUNCTION:
            writer.writeFunction(parser.arg1(), parser.arg2())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: Wrong number of arguments.\n"
              "Usage: VMTranslator file_name.vm or /existing_dir_path/")
    else:
        main(sys.argv[FILE_PATH])
