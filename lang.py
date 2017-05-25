#! /usr/bin/env python3
import shlex
import io
import cmds
import lexer
import functools

from memory import Memory,  \
                   MemoryObject, \
                   Function, \
                   Num, \
                   String, \
                   Bool, \
                   Register, \
                   List
import memory


lex_rules = [
    ('!$', r' '),
    ('!$', r'\\\n'),
    ('+ARROWR', r'\-\>'),
    ('+ARROWL', r'\<\-'),
    ('+IFNOT', r'ifnot'),
    ('+IF', r'if'),
    # ('=FUN', r'fun'),
    ('+LOOP', r'loop'),
    # ('+TIMES', r'times'),
    # ('+WHILE', r'while'),
    ('+TRUE', r'true'),
    ('+FALSE', r'false'),
    ('=CAST', r'\$\$[a-zA-Z_]+'),
    ('=STR', r'"([^\"]|\\"|\\\\)*"'),
    ('=IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('=NUM', r'[0-9]+'),
    ('!$', r'#[^\n]+'),
    ('+QUEST', r'\?'),
    ('+AT', r'\@'),
    
    ('+DOLLAR', r'\$'),
    ('+AMP', r'\&'),
    
    ('+LOPEN', r'\(\:'),
    ('+LCLOSE', r'\:\)'),
    
    ('+LP', r'\('),
    ('+RP', r'\)'),
    
    ('+LB', r'\['),
    ('+RB', r'\]'),
    
    ('+SEMIC', r'\;'),
    ('+COLON', r'\:'),
    ('+NEWLINE', r'\n'),
    ('+EQEQ', r'\=\='),
    ('+NEQ', r'\!\='),
    ('+GREATER', r'\>'),
    ('+LESSER', r'\<'),
    ('+EQUALS', r'\='),
    
    ('+ADD', r'\+'),
    ('+SUB', r'\-'),
    ('+MUL', r'\*'),
    ('+DIV', r'\/'),
    ('+MOD', r'\%'),
    
    ('!!', r'.'),
]

builtins = cmds.cmds


class BuiltInFunction(Function):
    def __init__(self):
        pass


class Program(object):
    def __init__(self, filename):
        self.filename = filename
        self.mem = Memory()
        self.set_lexer(lexer.Lexer(lex_rules))
        
    def set_lexer(self, l):
        self.lexer = l
        lexer.current_lexer = l

    def reduce_tokens(self, buf):
        def red(x, y):
            if type(x) is tuple:
                return getattr(x[0], x[1])(y)
            if type(y) is str:
                # if y == 's':
                #  return x.str()
                ops = {
                    '+': 'sum',
                    '-': 'sub',
                    
                    '*': 'mul',
                    '/': 'div',
                    
                    '%': 'mod',
                    
                    '=': 'eq',
                    '!': 'neq',

                    '>': 'greater',
                    '<': 'lesser',
                }
                return (x, ops[y])
            else:
                print('WEIRDER ERROR')
                exit(1)
        buf = functools.reduce(red, buf)
        return buf

    def get_next_symbol(self, mem):
        buf = []
        while True:
            val = False
            op = False
            last_pos = self.lexer.charnum
            e = self.lexer.consume_next()
            if not e and buf:
                if type(buf[-1]) is str:
                    print('UNEXPECTED EOF')
                    exit(1)
                elif isinstance(buf[-1], MemoryObject):
                    break
            # === Values ===
            val = True
            # print('k:{k},v:{v}'.format(**e))
            if e['k'] == '=IDENTIFIER':
                # print('GETTING: {v} from memory'.format(**e))
                if buf and isinstance(buf[-1], MemoryObject):
                    buf.append(MemoryObject('DUMMY'))
                else:
                    buf.append(mem.getval(e['v']))
                    if isinstance(buf[-1], Function):
                        func = buf.pop(-1)

                        e = self.lexer.consume_next()
                        if e['k'] == '+LB':
                            call_args = []
                            s = self.get_next_symbol(mem)
                            while s is not None:
                                call_args.append(s)
                                s = self.get_next_symbol(mem)

                            e = self.lexer.consume_next()
                            if e['k'] != '+RB':
                                self.lexer.err(
                                    'Syntax error: no closing bracket for '
                                    'args list!')
                                exit(1)

                            buf.append(func.call(call_args))
                        else:
                            # rewind
                            self.lexer.charnum = e['coords'][0]
                            buf.append(func)

            elif e['k'] == '=STR':
                buf.append(String(e['v'].strip('"')))
            elif e['k'] == '=NUM':
                buf.append(Num(int(e['v'])))
            elif e['k'] in ('+TRUE', '+FALSE'):
                buf.append(Bool(e['k'] == '+TRUE'))

            elif e['k'] == '+QUEST':
                # checker = buf.pop(-1)
                checker = self.reduce_tokens(buf)
                buf = []
                if isinstance(checker, MemoryObject):
                    t = self.get_next_symbol(mem)
                    f = self.get_next_symbol(mem)
                    buf.append(t if checker.val else f)
                else:
                    print('TERNARY NOT AFTER MEMORYOBJECT')
                    exit(1)
            elif e['k'] == '+LOPEN':
                list_content = []
                e = self.lexer.consume_next()
                while e['k'] != '+LCLOSE':
                    self.lexer.charnum = e['coords'][0]
                    le = self.get_next_symbol(mem)
                    list_content.append(le)
                    e = self.lexer.consume_next()
                buf.append(List(list_content))
            elif e['k'] == '+COLON':
                lo = buf.pop(-1)
                if isinstance(lo, List):
                    buf.append(lo.getitem(self.get_next_symbol(mem).val))
                else:
                    buf.append(lo)
                    self.lexer.charnum = last_pos
                    break
            # === Scope in / Scope out ===
            elif e['k'] == '+DOLLAR':
                buf.append(self.get_next_symbol(mem))
            elif e['k'] == '+AMP':
                break
            else:
                val = False
                
            # === Negation ===
            #if ((len(buf) == 2 or not isinstance(buf[-3], MemoryObject)) \
            #    and buf[-2] == '-' and val):
            #    if len(buf) == 2
            if (len(buf) == 2 and buf[-2] == '-') or\
                (len(buf) > 2 and not isinstance(buf[-3], MemoryObject) and buf[-2] == '-'):
                    mo = buf.pop(-1)
                    buf.pop(-1)
                    buf.append(mo.neg())

            # === Operations ===
            op = True
            if e['k'] == '+ADD':
                buf.append('+')
            elif e['k'] == '+SUB':
                buf.append('-')
            elif e['k'] == '+MUL':
                buf.append('*')
            elif e['k'] == '+DIV':
                buf.append('/')
            elif e['k'] == '+MOD':
                buf.append('%')
            elif e['k'] == '+EQEQ':
                buf.append('=')
            elif e['k'] == '+NEQ':
                buf.append('!')
            elif e['k'] == '+GREATER':
                buf.append('>')
            elif e['k'] == '+LESSER':
                buf.append('<')
            # elif e['k'] == '=CAST':
            #  if e['v'][2:] == 'str':
            #    buf.append('s')
            #  else:
            #    print('INVALID CAST TARGET TYPE: `{}`'.format(e['v'][2:]))
            #    exit(1)
            else:
                op = False

            # === casting ===
            if val:
                before = self.lexer.charnum
                cast = self.lexer.consume_next()
                if cast:
                    if cast['k'] == '=CAST':
                        original = buf.pop(-1)
                        docast = {
                            'str': original.str,
                            'num': original.num,
                            'list': original.list,
                        }
                        casted = docast[cast['v'][2:]]()
                        buf.append(casted)
                    else:
                        # rewind
                        self.lexer.charnum = cast['coords'][0]
                else:
                    self.lexer.charnum = before
            
            

            # === when to break ===
            if not op and not val:
                # rewind
                self.lexer.charnum = e['coords'][0]
                if buf and (type(buf[-1]) is not str):
                    break

                # print('RETURNING NONE: {v}'.format(**e))
                return None

            # double operations are impossible (except for negations)
            # double values are just lists
            if len(buf) > 1:

                if (op and (type(buf[-2]) is str and buf[-1] != '-')) \
                        or (val and isinstance(buf[-2], MemoryObject)):
                    # rewinid
                    # self.lexer.charnum = e['coords'][0]
                    self.lexer.charnum = last_pos
                    buf.pop(-1)
                    break

        buf = self.reduce_tokens(buf)
        if type(buf) is tuple:
            self.lexer.err('BUF IS TUPLE: {}'.format(buf))
        if buf:
            return buf
        else:
            self.lexer.err('BUF IS NONE: {}'.format(buf))
            exit(1)

    def exec(self, line, mem, scope_name=None):
        def get_scope_name(section_name):
            pos = self.lexer.getpos(self.lexer.charnum)
            pos['linum'] += 1
            return section_name+' at {linum}:{charnum}'.format(**pos)
        
        if scope_name:
            sname = scope_name
        else:
            sname = ''
        
        # print('--- line ---')
        # line = line.strip('\n')
        old_lexer = self.lexer
        self.set_lexer(lexer.Lexer(lex_rules))
        self.lexer.lex(line)
        self.lexer.scope_name = sname
        toks = []
        def_name = ''
        content = ''
        args = ''
        call_args = []
        call_name = ''
        last_e = None
        e = None
        while True:
            last_e = e
            e = self.lexer.consume_next()
            if e:
                toks.append(e)
                # print('toksbuf: %s' % ([t['v'] for t in toks]))
                # print('{k:<20s} {v}'.format(**e))

                # === HANDLERS ===

                # NEWLINE and SEMIC terminate expr
                if e['k'] in ('+NEWLINE', '+SEMIC'):
                    toks = []
                    continue

                if e['k'] == '+EQUALS':
                    mem.add(toks[-2]['v'], self.get_next_symbol(mem))
                    continue

                # === OPENING TOKENS ===
                # @<reg_name>
                if e['k'] == '+AT':
                    reg_name = self.lexer.consume_next()['v']
                    content = mem.getval(reg_name).val
                    continue

                # ()
                elif e['k'] == '+LP':
                    content = ''
                    depth = 0
                    e = self.lexer.consume_next()
                    while True:
                        if e['k'] == '+LP':
                            depth += 1
                        if e['k'] == '+RP':
                            if not depth:
                                break
                            else:
                                depth -= 1
                        content += ' ' + e['v']
                        e = self.lexer.consume_next()
                    continue

                # reg <regname> ;
                elif e['v'] == 'reg':
                    reg_name = self.lexer.consume_next()['v']
                    mem.add(reg_name, Register(content.strip(), 
                                      scope_name=get_scope_name('reg')))
                    continue

                elif e['v'] == 'do':

                    e = self.lexer.consume_next()
                    while e['k'] not in ('+SEMIC', '+NEWLINE'):
                        target = e
                        arrow = self.lexer.consume_next()
                        val = self.get_next_symbol(mem)
                        if arrow['k'] == '+ARROWL' and \
                                target['k'] == '=IDENTIFIER':

                            mem.add(target['v'], val)
                        else:
                            print('INVALID DO ARGUMENTS')
                            exit(1)
                        e = self.lexer.consume_next()
                    # rewind
                    self.lexer.charnum = e['coords'][0]

                    self.exec(content, mem, scope_name=get_scope_name('do'))

                # fun ... ;
                elif e['v'] == 'fun':
                    args = ''
                    def_name = self.lexer.consume_next()['v']

                    e = self.lexer.consume_next()
                    while e['k'] not in ('+SEMIC', '+NEWLINE'):
                        args += ' ' + e['v']
                        e = self.lexer.consume_next()
                        
                    # rewind
                    self.lexer.charnum = e['coords'][0]
                        
                    mem.add(def_name, Function(content.strip(), args, 
                                               scope_name=get_scope_name('fun')))
                    toks = []
                    continue

                # loop <mod> ... ;
                elif e['k'] == '+LOOP':
                    scope_name = get_scope_name('loop')
                    
                    mod = self.lexer.consume_next()['v']
                    if mod == 'times':
                        iterations = self.get_next_symbol(mem).val
                        arrow = self.lexer.consume_next()
                        if arrow['k'] != '+ARROWR':
                            # rewind
                            self.lexer.charnum = arrow['coords'][0]
                            counter = '_'
                        else:
                            counter = self.lexer.consume_next()['v']

                        for i in range(iterations):
                            mem.add(counter, Num(i))
                            self.exec(content, mem, scope_name=scope_name)
                        continue
                    elif mod == 'while':
                        checker = ''
                        checker_sname = get_scope_name('while checker')

                        e = self.lexer.consume_next()
                        while e['k'] not in ('+SEMIC', '+NEWLINE'):
                            checker += ' ' + e['v']
                            e = self.lexer.consume_next()
                        # rewind
                        self.lexer.charnum = e['coords'][0]

                        # checker = self.get_next_symbol(mem).val
                        checker += ';'
                        checker = 'ret ' + checker
                        while Program('').exec(checker, mem,
                                               scope_name=checker_sname
                                               ).val is True:
                            self.exec(content, mem, scope_name=scope_name)
                        continue
                    elif mod == 'each':
                        iterator = self.get_next_symbol(mem)
                        last_pos = self.lexer.charnum
                        arrow = self.lexer.consume_next()

                        if arrow['k'] != '+ARROWR':
                            # rewind
                            self.lexer.charnum = last_pos
                            counter = '_'
                        else:
                            counter = self.lexer.consume_next()['v']

                        for v in iterator.val:
                            mem.add(counter, v)
                            self.exec(content, mem, scope_name=scope_name)
                        continue
                    else:
                        print('INVALID MOD FOR LOOP: {}'.format(mod))
                        exit(1)

                # if ... ;
                elif e['k'] == '+IF':
                    do = self.get_next_symbol(mem).val
                    last_if = do
                    if do:
                        self.exec(content, mem, scope_name=get_scope_name('if'))
                    continue

                # ifnot ... ;
                elif e['k'] == '+IFNOT':
                    scope_name = get_scope_name('ifnot')
                    before = self.lexer.charnum
                    e = self.lexer.consume_next()
                    if e and e['v'] == 'but':

                        do = self.get_next_symbol(mem).val
                        last_last_if = last_if
                        last_if = do
                        if do and not last_last_if:
                            self.exec(content, mem, scope_name=scope_name)
                        continue
                    else:
                        # rewind
                        self.lexer.charnum = before
                        if not last_if:
                            self.exec(content, mem, scope_name=scope_name)
                        continue

                # ret ... ;
                elif e['v'] == 'ret':
                    return self.get_next_symbol(mem)

                # []
                elif e['k'] == '+LB':
                    call_args = []
                    #call_name = last_e['v']
                    call_name = toks.pop(-2)['v']

                    s = self.get_next_symbol(mem)
                    while s is not None:
                        call_args.append(s)
                        s = self.get_next_symbol(mem)
                    # print(call_args)

                    e = self.lexer.consume_next()
                    if e['k'] != '+RB':
                        self.lexer.err('Syntax error: '
                                       'no closing bracket for args list!')
                        exit(1)

                    mem.getval(call_name).call(call_args)
                    continue
            else:
                break
        self.set_lexer(old_lexer)

    @staticmethod
    def eval_line(line, mem):
        cmd, *args = shlex.split(line)
        cmds.cmds[cmd](*args)

    def run(self, mem=None):
        if not mem:
            mem = self.mem

        with io.open(self.filename, 'r') as f:
            self.exec(''.join([l for l in f]), mem, scope_name='Main')


memory.setup(cmds.cmds, Program)

if __name__ == '__main__':
    import sys
    try:
        prgpath = sys.argv[1]
    except IndexError:
        print('NOT ENOUGH ARGUMENTS TO INTERPRETER')
        exit(1)
    else:
        Program(prgpath).run()
