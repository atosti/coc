## Circle of Competence

---

Circle of Competence (CoC) is a web-scraping tool designed to analyze stock market symbols according to criteria discussed in Benjamin Graham's __The Intelligent Investor__.

It allows a user to quickly analyze publicly-traded companies, and roughly determine their intrinsic value. As with all investing tools, __**use it at your own risk**__.

## Running it on your system

---

First, have **Python 3+** installed on your system so you can run python files.

1. Clone the repository into a directory of your choosing.
2. Run the `main.py` file. You'll be prompted to enter one or more stock symbols.
3. Enter your symbol(s) along with any desired flags.

   * $ `bgs -x`
   * **Note:** It takes a few seconds per symbol to scrape/process the required data.
4. Look at the results printed to the console.
5. Enter more symbols as desired.
6. Type 'exit' or 'quit' to close the program.

## Usable Flags

---

Note that flags can be combined into strings prepended with a dash, so "-dx" would run both "-d" and "-x".

1. "-d" **Debug Mode**
   * Debug mode, prints all available fetched data for a symbol.
2. "-j" **JSON Output**
   * Generates and prints a JSON string for all the symbols given.
3. "-s" **Silent Mode**
   * Silent mode, hides all console output for each symbol. Best when used in combination with JSON generation.
4. "-x" **Excel Update/Creation**
   * Appends the symbol to a generated excel file, `coc.xlsx`. If the symbol already exists in file, then its row is overwritten with fresh data.

## The Financial Calculations

---

## Understanding The 7 Criterion

---

CoC uses a variety of datapoints for appraising a company according to the 7-point system. Most of these values are fundamentals derived from financial statements and balance sheets, such as: Market Capitalization, P/E Ratio, Assets, Liabilities, etc.

Additionally, there are general indicators listed to assist in determining the strength of a company. These include things such as its price relative to its [Book Value](https://www.investopedia.com/terms/b/bookvalue.asp), or the [Payout Ratio](https://www.investopedia.com/terms/p/payoutratio.asp) of its dividend.

Together, these help illustrate where potential weaknesses in a company may lie. Although CoC can be used to identify long-term strength in a company, it primarily identifies the presence (or absence) of long-term weakness.

## What are the 7 Criterion?

---

Internally, CoC analyzes companies based on the following criteria. An answer of **True** is associated with relative strength, whereas **False** is associated with relative weakness.

1. Does the company have over $700M (USD) in annual sales?
2. Does it have a Current Ratio of at least 2.0?
   * Are the company's underlying assets worth at least twice its short-term debts (those owed in one year)?
3. If it pays a dividend, has it not missed or reduced its dividend payments in the last 5 years?
4. Has it not had an earnings deficit in the last 5 years?
   * Were there any years where it lost money?
5. Does it have earnings growth of at least 2.9% annually for the last 5 years?
   * This equates to approximately 15% total growth over 5 yrs.
6. Does it have cheap assets?
   * Is Market Capitalization < Net Asset Value * 1.5?

     * **Note:** Net Asset Value = (Assets - Liabilities)
     * Essentially, is the value of all its outstanding shares less than 1.5x the assets leftover after paying all its debts.
7. Does it have cheap earnings?
   * Is its Price-to-Earnings Ratio <= 15?
     * Essentially, is it priced no greater than 15x its annual earnings.

### Additional Criteria

1. Analysis
   * A breakdown of which criterion pass/fail and how so. Meant to inform users of a company's risks.
2. Graham Number
   * The [Graham number](https://en.wikipedia.org/wiki/Graham_number) is a calculation to determine a fair value for a company's shares. Purchasing at or below this value is seen as ideal.
   * It is calculated as the sqrt(22.5 * EPS * BVPS).
     * Sometimes CoC returns a negative value for the Graham number. This means that either the EPS, the BVPS, or both are negative.
     * This indicates a need for manually examining the two values further.
3. Dividend Yield
   * Relative to the currently traded price, what percentage of profits are payed out annually by the company.
4. Sector
   * A descriptor of which industry the company does business in.
