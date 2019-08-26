## Circle of Competence
A work in progress to analyze stock symbols based on various criteria.
The aim of this project is to quickly analyze a stock with Value Investing
criteria, with the aim of determining a rough intrinsic value.

As with all investing tools, use it at your own risk. ;)

## To Do List (Core features)
1. Add the ability to save the values to a local file.
    * Consider making an xlsx, so the raw data is human readable.
2. Create quick setup steps for others to use this repository.
3. Add a 'help' command.

## Instructions to Run on your system
1. Clone the repository
2. Open the `backend` folder and create a new `avApiKey.txt` file.
3. Inside this file, simply paste your API key on a single line.
4. Run `main.py` inside the `backend` folder, it should read your API key from the text file automatically.

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