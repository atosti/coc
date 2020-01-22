import handler as handler

phrase = ''
print('Enter a command (type \'q\' to exit): ')
while(phrase != 'q'):
    print('$', end='')
    phrase = input().lower()
    handler.commands(phrase)