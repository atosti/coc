import handler as handler

# Fetches your Alpha Vantage API key from the "avApiKey.txt" file in backend
f = open('./backend/avApiKey.txt', "r")
lines = list(f)
avApiKey = ''.join(lines)

# Fetches your US Fundamentals API key from the "ufApiKey.txt" file in backend
f = open('./backend/ufApiKey.txt', "r")
lines = list(f)
ufApiKey = ''.join(lines)

# Command loop
phrase = ''
print('Enter a command(type \'quit\' or \'exit\' when finished):')
while (phrase != 'quit' and phrase != 'exit'):
    print('$ ', end='') # Signals to the user they're in a command prompt
    phrase = input()
    phrase = phrase.lower()
    handler.commands(phrase, avApiKey, ufApiKey)

# FIXME - Test API call to UF for getting company CIK IDs
# https://api.usfundamentals.com/v1/companies/xbrl?format=json&token=ZN6kXxgpXMxFUQGcUOkZGw

# FIXME - Examples below, remove later.

# Make a GET request for testing
# resp = timeSeriesDaily('MSFT', '5min', avApiKey)
# print('VA Response: ' + resp.text)

# resp2 = timeSeriesDailyAdjusted('IP', avApiKey)
# print('tsDailyAdjusted: ' + resp2.text)

# TODO - Figure out Annual earnings (historical if possible)
