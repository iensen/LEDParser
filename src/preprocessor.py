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
import os
from genparser.src.astgen.parsing.lexer import *
from genparser.src.astgen.parsing.parser import *
special_lexemes = ["var", "vars", "def","ddef","iff"]


class Preprocessor:
    """Defines  a class that can be used to preprocess
    a LED program by removing comments and splitting
    it into a list of separate program elements
    """

    def __init__(self, program_file):
        """Read the program file
        """
        with open(program_file) as lf:
            self.contents = lf.read()


        self.column = 0
        self.line = 0
        lexicon_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"genparser","src","astgen","tests","led","lexicon")
        grammar_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"genparser","src","astgen","tests","led","grammar_1")
        self.lexer = Lexer(lexicon_file,False)
        self.parser = Parser(grammar_file, self.lexer.lexicon_dict.keys())

    def get_elements(self):
        """ get the list of program elements
        """

        in_comment_state = True
        #self.column = 0
        #self.line = 0
        begin_region_regex = re.compile(r"\\-+")
        end_region_regex = re.compile(r"-+\\")
        done = False
        elements = []
        cur_contents = self.contents
        cur_line = 1
        while not done:
            # search for the start of the next program region
            region_start_comment = re.search(r"/-+",cur_contents)
            if region_start_comment is None :
                done = True
                continue

            # find matching end
            region_end_comment = re.search(r"-+/",cur_contents)

            if region_end_comment.start() is None:
                raise UnmatchedRegionComment(cur_line)

            cur_line += cur_contents[:region_start_comment.start()].count('\n')

            region = cur_contents[region_start_comment.end()+1:region_end_comment.start()]
            elements.extend(self.get_elements_from_region(region))
            cur_line += cur_contents[:region_end_comment.start()].count('\n')
            cur_contents =  cur_contents[region_end_comment.end()+1:]

        return elements



    @staticmethod
    def all_spaces_left(lexing_sequence):
        for c in lexing_sequence:
            if c[0] != 'spaces':
                return False
        return True

    def find_guard_if_idx(lexing_sequence, then_idx):
        idx = then_idx
        while idx > 0 and lexing_sequence[idx][0] != 'then':
            idx -=1
        return idx

    def find_element_start_idx(lexing_sequence, spec_sym_idx):
        if(lexing_sequence[spec_sym_idx][0] in  ['def','iff']):
            # we found a constant, function or relation definition
            # need to go back through [guard][id][ params]
            # first, check if there are params

            spec_sym_idx -= 1
            if(spec_sym_idx >= 0 and lexing_sequence[spec_sym_idx][0] =="rparen"):
                # find matching openparen
                closed_paren_count = 1
                while spec_sym_idx -1 >=0 and closed_paren_count > 0 :
                    spec_sym_idx -=1
                    if lexing_sequence[spec_sym_idx][0] =="rparen":
                        closed_paren_count+=1
                    if lexing_sequence[spec_sym_idx][0] =="lparen":
                        closed_paren_count-=1

                if closed_paren_count !=0:
                    return -1

                spec_sym_idx -=2

                # is there a guard?
                if(spec_sym_idx>=0 and lexing_sequence[spec_sym_idx][0] == "then"):
                    return Preprocessor.find_guard_if_idx(lexing_sequence,spec_sym_idx)
                else:
                    return spec_sym_idx+1
            else:
                return spec_sym_idx

        elif lexing_sequence[spec_sym_idx][0] == 'ddef':
            # found a type definition
            return spec_sym_idx -1
        elif lexing_sequence[spec_sym_idx][0] in ['var', 'vars']:
            return spec_sym_idx


                #skip

    def get_elements_from_region(self, region):
            # obtain lexing sequence from the region
            lexing_sequence = self.lexer.get_lexing_sequence(region)
            lexing_sequence = [l for l in lexing_sequence if l[0] != 'spaces']
            done = False
            elements = []
            while not done:
                i = self.find_first_special_lexeme_idx(lexing_sequence)
                if i == -1:
                  if not Preprocessor.all_spaces_left(lexing_sequence):
                     raise InvalidProgramElement(region,self.line)
                  else:
                     break
                next_i = self.find_first_special_lexeme_idx(lexing_sequence[i+1:])
                if next_i is None:
                    ast = self.parser.get_ast(lexing_sequence,False)
                    if ast is None:
                        raise InvalidProgramElement(region,self.line)
                    elements.append(ast.children[0])
                    break
                else:
                     elem_last_idx = Preprocessor.find_element_start_idx(lexing_sequence,next_i+i+1)-1
                     if( elem_last_idx<0):
                        raise InvalidProgramElement(Preprocessor.get_text_from_lexemes(lexing_sequence),self.line)
                     ast = self.parser.get_ast(lexing_sequence[:elem_last_idx+1], False)
                     if ast is None:
                        raise InvalidProgramElement(region,self.line)
                     elements.append(ast.children[0])
                     lexing_sequence = lexing_sequence[elem_last_idx+1:]

            return elements

    def find_first_special_lexeme_idx(self, lexing_sequence):
        for i in range(len(lexing_sequence)):
            if(lexing_sequence[i][0] in special_lexemes):
                return i

        return None

    @staticmethod
    def get_text_from_lexemes(lexing_sequence):
        text =""
        for l in lexing_sequence:
            text += l[1]+" "
        return text



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




class UnmatchedRegionComment(Exception):
    """
    Defines a class for representing exceptions which are thrown in the event of
    an invalid lexeme declaration in the lexicon file
    """

    def __init__(self, line_number):
        super(UnmatchedRegionComment, self).__init__()
        self.line_number = line_number

    def __repr__(self):
        return "The program file contains an unmatched " \
               "program region starting from line" \
                                                                "number " + str(self.line_number) + "."

    def __str__(self):
        return self.__repr__()


class InvalidProgramElement(Exception):
    """
    Defines a class for representing exceptions which are thrown in the event of
    a (syntactically) invalid program element in the program file
    """

    def __init__(self, contents, line_number):
        super(InvalidProgramElement, self).__init__()
        self.contents = contents
        self.line_number = line_number

    def __repr__(self):
        return "The program file contains an invalid program element " \
            + self.contents +" in the  " \
               " region starting from line" \
                 "number " + str(self.line_number) + "."

    def __str__(self):
        return self.__repr__()
