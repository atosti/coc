import handler as handler

phrase = ''
print('Enter a symbol (type \'quit\' to exit): ')
while(phrase != 'quit'):
    print('$', end='')
    phrase = input().lower()
    if phrase != 'quit':
        handler.commands(phrase)