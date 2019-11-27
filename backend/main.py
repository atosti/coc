import quandl

import handler as handler

# Fetches your Alpha Vantage API key from the "avApiKey.txt" file in backend
f = open('./backend/avApiKey.txt', 'r')
lines = list(f)
avApiKey = ''.join(lines)
f.close()

# Fetches your US Fundamentals API key from the "ufApiKey.txt" file in backend
f = open('./backend/ufApiKey.txt', 'r')
lines = list(f)
ufApiKey = ''.join(lines)
f.close()

f = open('./backend/quandlApiKey.txt', 'r')
lines = list(f)
quandlApikey = ''.join(lines)\

# Command loop
phrase = ''
print('Enter a command(type \'quit\' or \'exit\' when finished):')
while (phrase != 'quit' and phrase != 'exit'):
    print('$ ', end='') # Signals to the user they're in a command prompt
    phrase = input()
    phrase = phrase.lower()
    handler.commands(phrase, avApiKey, ufApiKey, quandlApikey)
