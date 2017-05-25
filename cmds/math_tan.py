from memory import Num
from math import tan, radians
import lexer

class math_tan:
    def call(args):
        if len(args) == 1:
            return Num(tan(radians(args[0].val)))
        else:
            raise LexerError('numargs not 1')
