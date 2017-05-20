import re
import collections


class Lexer(object):
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

    def lex(self, buffer):
        self.buffer = buffer
        self.charnum = 0
        self.linum = 0

    def consume_next(self):
        if self.buffer[self.charnum:] == '':
            return None
        if self.buffer[self.charnum] == '\n':
            self.linum += 1

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
            print('Error: token not recognized! {}:{}'.format(
                self.charnum, self.linum))
            exit(1)
        return {'k': k, 'v': m.group(), 'coords': (offset, m.end() + offset)}
