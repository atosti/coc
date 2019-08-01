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

## Instructions to Run on your system
1. Clone the repository
2. Open the `backend` folder and create a new `avApiKey.txt` file.
3. Inside this file, simply paste your API key on a single line.
4. Run `main.py` inside the `backend` folder, it should read your API key from the text file automatically.
