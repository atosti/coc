import analyzer as analyzer

def commands(phrase):
    args = phrase.split(' ')
    cmd = args[0]
    if cmd == 'check':
        symbol = ''
        if len(args) > 1:
            symbol = args[1]
        analyzer.check(symbol)
    elif cmd =='q':
        print('Quitting...')
    else:
        print('Invalid command: ' + cmd)
    return