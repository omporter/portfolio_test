A cryptocurrency portfolio manager, trade matcher and profit and loss calculator. 

This command line application is written in Python3 and uses Google Sheets as DB. 

For any given cryptocurrency ticker, this app matches buy trades with sell trades. If a buy trade is closed, the buy and sell will be matched to the completed trades sheet where the user can see their history of profit and loss. The application is made to be as tax-efficient as possible by matching the most recent sell trade with the oldest buy trade. This increases the chances of pushing the trade-duration to over 12 months and giving it capital gain status. In addition, this application updates live prices using the coinmarketcap API, and gives the user an up-to-date portfolio based on these latest wrapper prices. 
