"""
Copyright (c) 2014, Evgenii Balai
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY EVGENII BALAI "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL EVGENII BALAI OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
"""

import re
import collections

class Preprocessor:
    """Defines  a class that can be used to preprocess
    a LED program by removing comments and splitting
    it into a list of separate program elements
    """

    def __init__(self, program_file):
        """Read the program file
        """
        with open(program_file) as lf:
            self.lines = lf.readlines()


        self.column = 0
        self.line = 0

    def get_elements(self):
        """ get the list of program elements
        """

        in_comment_state = True
        self.column = 0
        self.line = 0

        while self.line < len(self.lines):
            if()




    def get_cur_char(self) :
        if self.line < len(self.lines) and self.column < len(self.lines[self.line]):
            return self.line[self.line][self.column]
        else:
            return None

    def advance_pointer(self):
        self.column +=1
        while(self.line < len(self.lines) and
                         self.column == len(self.lines[self.line])):
            self.column = 0
            self.line +=1

    def consume_dashes(self):
        while self.get_cur_char() == '-':
            self.advance_pointer()




class InvalidLexemeDeclaration(Exception):
    """
    Defines a class for representing exceptions which are thrown in the event of
    an invalid lexeme declaration in the lexicon file
    """

    def __init__(self, declaration, line_number):
        super(InvalidLexemeDeclaration, self).__init__()
        self.declaration = declaration
        self.line_number = line_number

    def __repr__(self):
        return "The lexicon file contains an invalid " \
               "lexeme declaration: " + str(self.declaration) + " at line" \
                                                                "number " + str(self.line_number) + "."

    def __str__(self):
        return self.__repr__()


class InvalidRegularExpression(Exception):
    """
    Defines a class for representing exceptions which are thrown in the event of
    an invalid regular expression in the lexicon file
    """

    def __init__(self, declaration, line_number):
        super(InvalidRegularExpression, self).__init__()
        self.declaration = declaration
        self.line_number = line_number

    def __repr__(self):
        return "The lexicon file contains an invalid " \
               "regular expression on the right hand side of the declaration: " \
               + str(self.declaration) + " at line" \
                                         " number " + str(self.line_number) + "."

    def __str__(self):
        return self.__repr__()


class RepeatedDeclaration(Exception):
    """
    Defines a class for representing exceptions which are thrown in the event of
    an invalid lexeme declaration given in the lexicon file
    """

    def __init__(self, lexeme_type, line_number):
        super(RepeatedDeclaration, self).__init__()
        self.lexeme_type = lexeme_type
        self.line_number = line_number

    def __repr__(self):
        return "The lexeme type " + self.lexeme_type + " is declared for" \
                                                       " the second time at line " + str(self.line_number) + "."

    def __str__(self):
        return self.__repr__()
