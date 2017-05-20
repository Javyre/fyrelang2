from random import randint
from memory import Num


class random_randint:
    def call(args):
        if len(args) == 1 and isinstance(args[0], Num):
            return Num(randint(args[0].val))

        elif len(args) == 2 \
                and isinstance(args[0], Num) \
                and isinstance(args[1], Num):

            return Num(randint(args[0].val, args[1].val))

        else:
            print('INVALID ARGS TO random_randint')
            exit(1)
