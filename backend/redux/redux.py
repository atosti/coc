import handler as handler

phrase = ''
print('Enter a stock symbol (type \'quit\' to exit): ')
while(phrase != 'quit'):
    print('$', end='')
    phrase = input().lower()
    if phrase != 'quit' and phrase != '':
        handler.commands(phrase)