import argparse
from backend.core import handler, excel
import sys
from multiprocessing import Pool
import functools


def _safe_check(symbol, flags):
    try:
        return handler.check(symbol, flags)
    except:
        return {symbol: None}


def _run(args):
    if args.mode == "batch":
        symbols = []
        for line in sys.stdin:
            for symbol in line.split():
                symbols.append(symbol)

        flags = list("j" "s")
        result = []
        with Pool(5) as p:
            result = p.map(functools.partial(_safe_check, flags=flags), symbols)

        error_symbols = []
        for r in result:
            for symbol, company in r.items():
                # TODO: This doesn't currently capture any error symbols b/c -j flag always returns a company
                if company:
                    excel.update(symbol, company)
                else:
                    error_symbols.append(symbol)
        

        if error_symbols:
            print("Error while processings the following symbols: ")
            print(error_symbols)

    else:
        print("Enter a stock symbol (type 'quit' to exit): ")
        while True:
            phrase = input("$").lower()
            if phrase and phrase in ["quit", "exit"]:
                return
            if phrase:
                handler.commands(phrase)

def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="interactive",
        help="Execution mode (default:interactive, other options: batch).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = process_args()
    _run(args)
