from memory import Bool
import lexer


class _assert:
    def call(args):
        if len(args) == 1:
            if not args[0].val:
                raise lexer.LexerError('Assertion error')
        if len(args) >= 2:
            for a, b in (args[i:i+2] for i in range(0, len(args), 2)):
                if not a.eq(b).val:
                    raise lexer.LexerError('Assertion error: '
                            '{} != {}'.format(a.str().val, b.str().val))
