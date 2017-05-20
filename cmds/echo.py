from memory import Num

class echo:
  def call(args):
    s = ''.join([str(e.val) for e in args])
    print(s, flush=True)
    return Num(0)
