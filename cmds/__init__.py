from os import walk

cmds = {}

print('\n\n----- BEGIN SETUP -----')
f = []
for (dirpath, dirnames, filenames) in walk('./cmds'):
    f.extend(filenames)
    break
for m in f:
  if m[-3:] == '.py':
    m = m[:-3]
    if m not in ['__init__']:
      print('importing:', m)
      exec('from . import %s' % m)
      try:
        func = eval('%s.%s' % (m, m))
      except:
        func = eval('%s._%s' % (m, m))
      cmds.update({m: func})
      
print('----- END SETUP -----\n\n')
# cmds['echo']('testing echo 123...')
