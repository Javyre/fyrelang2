from memory import Num, List


class echo:
    def call(args):
        s = ''.join([e.getstr() for e in args])
        print(s, flush=True)
        return Num(0)
