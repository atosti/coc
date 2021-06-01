from backend.core import handler


def _run():
    print('Enter a stock symbol (type \'quit\' to exit): ')
    while True:
        phrase = input('$').lower()
        if phrase and phrase == 'quit' or phrase == 'exit':
            return
        if phrase:
            handler.commands(phrase)


if __name__ == '__main__':
    _run()
