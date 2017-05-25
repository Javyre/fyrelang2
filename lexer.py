import re
import collections
import sys


class LexerError(Exception):
    def __str__(self):
        try:
            print(current_lexer.gen_msg(self.args[0]), file=sys.stderr)
            
        # Pythonista crashes if any error occur during running of exceptions
        except Exception as e:
            print(e)
        return super().__str__()

class Lexer(object):
    scope_name = ''
    def __init__(self, rules):
        self.rules = self.compile_rules(rules)

    def compile_rules(self, irules):
        orules = []
        for k, r in irules:
            if type(r) is str:
                r = re.compile(r)
            elif not isinstance(r, re.regex):
                print('INVALID RULE TYPE')
                exit(1)
            orules.append((k, r))
        return orules
        
    def getpos(self, pos):
        charnum = linum = 0
        for i, c in enumerate(self.buffer):
            if c == '\n':
                linum += 1
                charnum = 0
                # continue
            else:
                charnum += 1
            if i == pos-1:
                break
            
        return {'linum': linum, 'charnum': charnum}
    
    def gen_msg(self, msg):
        pos = self.getpos(self.charnum)
        pos['linum'] += 1
        posinfo = '{linum}:{charnum}'.format(**pos)
        
        out = []
        
        out.append('ERROR: '+msg+' in `{}`'.format(self.scope_name)+posinfo)
        
        buflines = self.buffer.split('\n')
        linum = pos['linum']-1
        
        numlinesup = linum
        for i in range(min(numlinesup, 3), 0, -1):
            out.append('{:>4d} '.format(linum-i+1)+buflines[linum-i])
            
        out.append('  >> '+buflines[linum])
        out.append('     '+('{}^'.format(' '*pos['charnum'])))
        
        numlinesdown = len(buflines)-linum-1
        for i in range(min(numlinesdown, 3)):
            out.append('{:>4d} '.format(linum+i+1)+buflines[linum+1])

        return '\n'.join(out)
        
    def err(self, msg):
        print(self.gen_msg(msg), file=sys.stderr)
        
    def lex(self, buffer):
        self.buffer = buffer
        self.charnum = 0
        self.linum = 0

    def consume_next(self):
        if self.buffer[self.charnum:] == '':
            return None
        #if self.buffer[self.charnum] == '\n':
        #    self.linum += 1

        for k, r in self.rules:
            m = r.match(self.buffer[self.charnum:])
            if m:
                offset = self.charnum
                self.charnum += len(m.group())
                if k[0] == '=':
                    # consume next !$ symbols
                    sm = None
                    while True:
                        for _k, _r in self.rules:
                            if _k == '!$':
                                _sm = _r.match(self.buffer[self.charnum:])
                                if _sm:
                                    sm = _sm
                                    # print('found spacer after =')
                                    self.charnum += len(sm.group())
                                    break
                        else:
                            break
                    if sm:
                        # return {'k': k, 'v': om.group(), 'coords': (offset,
                        # om.end()+offset)}
                        break
                    else:
                        break
                        # print('continuing...')
                        # continue

                elif k[0] == '+':
                    # return {'k': k, 'v': om.group(), 'coords': (offset,
                    # om.end()+offset)}
                    break
                elif k == '!$':
                    return self.consume_next()
                elif k == '!!':
                    print('Error: unaccepted pattern found! {}:{}'.format(
                        self.charnum - 1, self.linum))
                    print('===\n{}\n===\n'.format(
                        self.buffer[self.charnum - 1:]))
                # break
        else:
            self.err('token not recognized!')
            exit(1)
        return {'k': k, 'v': m.group(), 'coords': (offset, m.end() + offset)}
        
current_lexer = Lexer([('n', r'\n')])
current_lexer.charnum = 6
current_lexer.buffer = '.\n.\n===NO CURRENT LEXER===\n.\n.'
