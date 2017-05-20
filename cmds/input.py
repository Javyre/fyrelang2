from memory import String

class _input:
  def call(args):
    if not args:
      out = input()
    if len(args) == 1 and isinstance(args[0], String):
      out = input(args[0].val)
    else:
      print('INVALID ARGS TO: input')
      exit(1)
    return String(out)
    
