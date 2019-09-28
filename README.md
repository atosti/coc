## Circle of Competence
A work in progress to analyze stock symbols based on various criteria.
The aim of this project is to quickly analyze a stock with Value Investing
criteria, with the aim of determining a rough intrinsic value.

As with all investing tools, use it at your own risk. ;)

This project uses the APIs available at [US Fundamentals](https://www.usfundamentals.com/) and [Alpha Vantage](https://www.alphavantage.co/).

## To Do List (Core features)
### General tasks
1. Add the ability to save the values to a local file.
    * Consider making an xlsx, so the raw data is human readable.
2. Create quick setup steps for others to use this repository.
3. Add a 'help' command.
4. Create quick setup steps for others to use this repository.
### US Fundamentals 

## Core Analysis Criteria
1. What are the earnings per share?
2. Are annual earnings over $700M? (Is it a large company?)
3. Is it conservatively financed? (Current ratio of 200%)
	* Current ratio = Current assets / current liabilities
4. Dividend history (Have they missed any dividends in the last 20 years?)
5. Have they had no earnings deficit in the last 10 years?
6. How is earnings growth? (At least 2.9% annually for 10 years)
7. Does it have Cheap Assets? (Market cap < (Assets - liabilities) * 1.5
	* A ratio less than 1 is good
8. Does it have Cheap earnings? (P/E ratio < 15)

## Instructions to Run on your system
1. Clone the repository
2. Open the `backend` folder and create two new files.
    * A file called `avApiKey.txt` containing your Alpha Vantage API key.
    * A file called `ufApiKey.txt` containing your US Fundamentals API key.
3. Inside these files, simply paste your API key on a single line.
4. Run `main.py` inside the `backend` folder, it should now read your API keys automatically.

## Commands (to be moved to the wiki later)
1. Exit/Quit
    * Simply exits the program.
2. Tsd
    * Makes a Time Series Daily API call. Requires two parameters:
    A stock symbol, and the time interval.
    `tsd MSFT 5min`
3. Tsda
    * Makes a Time Series Daily Adjusted API call. Requires one parameter:
    A stock symbol
    `tsda MSFT`
4. Help
    * TBD - Will eventually provide a basic use guide inside the prompt.