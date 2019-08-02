## Circle of Competence
A work in progress to analyze stock symbols based on various criteria.

## To Do List (Core features)
1. Implement python backend for HTTPS calls to Alpha Vantage.
2. Implement TS frontend to show summary of saved Symbol/Exchange pairs.
3. Add simple saving of calculated values to a Postgres DB.
4. Add the ability to save the values to a user profile.
    * Might be unnecessary at first, consider more general approach.
5. Place API key in its own file and read it from there (so it's never pushed here).
6. Create quick setup steps for others to use this repository.
7. Alternately, could write things to a spreadsheet/local file to create a sort of personalized database.

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
2. Open the `backend` folder and create a new `avApiKey.txt` file.
3. Inside this file, simply paste your API key on a single line.
4. Run `main.py` inside the `backend` folder, it should read your API key from the text file automatically.
