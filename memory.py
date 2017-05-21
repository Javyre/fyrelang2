builtins = None
runner = None


def setup(bins, rnr):
    global builtins, runner
    builtins = bins
    runner = rnr


class Memory(object):
    def __init__(self, mem_dict=None):
        self.mem_dict = {}
        if mem_dict is not None:
            self.mem_dict.update(mem_dict)

    def add(self, key, val):
        if not isinstance(val, MemoryObject):
            print('memory item trying to insert isnt'
                  ' memory object!: {} (to: {})'.format(val, key))
            exit(1)
        val.name = key
        self.mem_dict[key] = val

    def getval(self, key):
        try:
            return self.mem_dict[key].getval()
        except KeyError:
            # print('GETTING BUILTIN: %s' % key)
            try:
                out = BuiltInFunction()
                call = getattr(builtins[key], 'call')
                setattr(out, 'call', call)
                return out
            except KeyError:
                print("VARIABLE DOES NOT EXIST IN MEMORY: {}".format(key))
                exit(1)


class MemoryObject(object):
    name = ''
    val = None

    def __init__(self, val):
        self.val = val

    def getval(self):
        return self

    def eq(self, other):
        return Bool(self.val == other.val)

    def neq(self, other):
        return Bool(self.val != other.val)

    def greater(self, other):
        return Bool(self.val > other.val)

    def lesser(self, other):
        return Bool(self.val < other.val)

    def str(self):
        return String(str(self.val))

    def num(self):
        return Num(int(self.val))

    def incompatible_types(self, other):
        print('ERROR: operations between these two'
              ' types not supported! : {} & {}'.format(
                  self.__class___.__name__, other.__class__.__name__
              ))
        exit(1)


class String(MemoryObject):
    def sum(self, other):
        return String(self.val + other.val)

    def mul(self, other):
        if isinstance(other, Num):
            return String(self.val * other.val)
        else:
            self.incompatible_types(other)


class Num(MemoryObject):
    def sum(self, other):
        return Num(self.val + other.val)

    def mul(self, other):
        if isinstance(other, Num):
            return Num(self.val * other.val)
        elif isinstance(other, String):
            return String(other.val * self.val)
        else:
            self.incompatible_types(other)


class Bool(MemoryObject):
    pass


class Register(MemoryObject):
    pass


class Function(MemoryObject):
    def __init__(self, content, args):
        self.content = content
        self.args = args.split()
        self.runner = runner
        # print('%%{}%% %%{}%%'.format(self.content, self.args))

    def call(self, args):
        mem = Memory()
        # print(self.args, [a.val for a in args])
        for i, a in enumerate(args):
            mem.add(self.args[i], a)
        return runner('').exec(self.content, mem)

    def getval(self):
        return self


class BuiltInFunction(Function):
    def __init__(self):
        pass
