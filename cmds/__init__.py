from os import walk

cmds = {}

print('\n\n----- BEGIN SETUP -----')

f = []
for (dirpath, dirnames, filenames) in walk('./cmds'):
    f.extend(filenames)
    break
    
f = [m[:-3].strip('_') for m in f if m[-3:] == '.py' and m[:-3] not in ['__init__']]
for m in f:
    print('importing:', m)
    try:
        exec('from . import %s' % m)
    except:
        exec('from . import _%s' % m)
    try:
        try:
            func = eval('%s.%s' % (m, m))
        except:
            func = eval('%s._%s' % (m, m))
    except:
        try:
            func = eval('_%s.%s' % (m, m))
        except:
            func = eval('_%s._%s' % (m, m))
    cmds.update({m: func})

print('----- END SETUP -----\n\n')
# cmds['echo']('testing echo 123...')
