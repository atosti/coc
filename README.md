## Circle of Competence

This is a webscraping tool designed to analyze stock symbols according to criteria discussed in Benjamin Graham's __The Intelligent Investor__. It allows a user to quickly analyze a publicly-traded company, and roughly determine its intrinsic value.

As with all investing tools, use it at your own risk. ;)

## Running CoC on your system

0. Have Python 3+ installed on your system.
1. Clone the repository
2. Run the `main.py` file.
3. Enter a NYSE stock symbol (or series of symbols) you wish to analyze as well as any accompanying flags.
4. Wait for it to scrape the data (this can take a few seconds per symbol).
5. View the score (out of 7) and output in the console.
6. Repeat the above as necessary.
7. Type 'exit' or 'quit' to quit

### Running the Tests

1. From the main directory run `python -m pytest`.

### Running the formatter

This project uses Black. Simply run `black`. from the base directory.

## Usable Flags

Note that flags can be combined into strings prepended with a dash, so "-dx" would run both "-d" and "-x".

1. "-d" **Debug Mode**
   * Debug mode, prints all available fetched data for a symbol.
2. "-j" **JSON Output**
   * Generates and prints a JSON string for all the symbols given.
3. "-s" **Silent Mode**
   * Silent mode, hides all console output for each symbol. Best when used in combination with JSON generation.
4. "-x" **Excel Update/Creation**
   * Appends the symbol to a generated excel file, `coc.xlsx`. If the symbol already exists in file, then its row is overwritten with fresh data.

## Understanding The 7 Criteria

CoC examines a variety of key datapoints for a symbol, such as Market Capitalization, P/E Ratio, Current Ratio, EPS, EPS Growth, Assets, Liabilities, etc. in order to score a symbol out of 7 points.

It analyzes symbols based on the following criteria, where a value of **True** is viewed as relative strength, and **False** is viewed as relative weakness.

### The 7 Scoring Criteria

1. Does the company have over $700M(USD) in annual sales?
2. Does it have a current ratio of at least 2.0?
   * This determines whether the company's underlying assets are worth at least twice its short-term debts (those owed in one year).
3. If it pays a dividend, has it not missed or reduced its dividend payments in the last 5 years?
4. Has it not had an earnings deficit in the last 5 years?
   * Essentially, were there any years where it lost money?
5. Does it have earnings growth of at least 2.9% annually for the last 5 years?
   * This equates to approx. 15% total growth over 5 yrs.
6. Does it have cheap assets?
   * This is calculated as the following:
     * Is Market Capitalization < Net Asset Value * 1.5?
       * Net Asset Value = (Assets - Liabilities)
   * Essentially, is the value of all its outstanding shares less than 1.5x the assets leftover after paying all its debts.
7. Does it have cheap earnings?
   * This is calculated as the following:
     * Is its Price-to-Earnings Ratio <= 15?
   * Essentially, is it priced no greater than 15x its annual earnings.

### Additional Criteria

1. Analysis
   * A breakdown of which criteria pass/fail and by how much. Meant to better inform users of a company's risks.
1. Graham Number
   * The [Graham number](https://en.wikipedia.org/wiki/Graham_number) is a calculation to determine a fair value for a company's shares. Purchasing at or below this value is seen as ideal.
   * It is calculated as the sqrt(22.5 * EPS * BVPS).
     * Sometimes CoC returns a negative value for the Graham number. This means that either the EPS, the BVPS, or both are negative.
       * This is considered a Weakness in the symbol, and indicates a need for manually examining these two values further.
2. Dividend Yield
   * Relative to the currently traded price, what percentage of profits are payed out annually by the company.
3. Sector
   * A descriptor of which industry the company does business in.