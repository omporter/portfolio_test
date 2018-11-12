''' ---------------------------------------------------------------- ''' 
''' D O C U M E N T     S T R U C T U R E ''' 



''' 
SECTION 1: SETUP 
SECTION 2: GLOBAL VARIABLES 
SECTION 3: META FUNCTIONS 
SECTION 4: MAIN FUNCTIONS
SECTION 5: BONUS FUNCTIONS 
SECTION 6: MISCELLANIOUS FUNCTIONS 
SECTION 7: WORKSHOP AND EXECUTE
'''







''' ---------------------------------------------------------------- ''' 
''' S E T U P ''' 

import json
import requests
import datetime
import gspread

from oauth2client.service_account import ServiceAccountCredentials



# google sheets api 
''' 
https://github.com/burnash/gspread
https://gspread.readthedocs.io/en/latest/user-guide.html 
''' 

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)
sh = gc.open("test_portfolio")

# coinmarketcap api

url = 'https://api.coinmarketcap.com/v2/ticker/'
response = requests.get(url)
api = json.loads(response.text)







''' ---------------------------------------------------------------- ''' 
''' G L O B A L     V A R I A B L E S ''' 


portfolio_sheet = sh.worksheet('Portfolio')
live_trades_sheet = sh.worksheet('Live Trades')
completed_trades_sheet = sh.worksheet('Completed Trades')
distribution_sheet = sh.worksheet('Distribution')
daily_tracker_sheet = sh.worksheet('Daily Tracker')
dashboard_sheet = sh.worksheet('Dashboard')


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


coin_url_extentions = {
                        'BTC': 'bitcoin',
                        'ETH': 'ethereum', 
                        'LTC': 'litecoin', 
                        'XMR': 'monero',
                        'DASH': 'dash',
                        'BAT': 'basic-attention-token',
                        'EOS': 'eos', 
                        'XLM': 'stellar'
                        }


exchange_names_which_contain_coin_tickers = [
                                              'HitBTC'
                                              # also lookout for 'temp' 
                                            ]

''' ---------------------------------------------------------------- ''' 
''' M E T A   F U N C T I O N S ''' 


# to do 
def start_up_jobs():
    # step 1: update portfolio sheet  
    update_portfolio_sheet()
    # step 2: 
    update_live_trades_live_data()
    # step 3: 
    update_daily_tracker()

# to do 
def new_trade_meta():

    user_input = input('Is it a Buy or Sell Trade?\n1 for Buy\n2 for Sell\n')
    user_input = str(user_input)
    if user_input == '1':
        buy_trade_meta()
    elif user_input == '2':
        sell_trade_meta()
    else:
        print('Invalid Option.')

    reorder_live_trades()
    check_to_add_another_trade()
    update_portfolio_sheet()
    display_bonus_info()

# to do 
def buy_trade_meta():
    ticker = add_buy_trade()
    configure_live_trades_sheet(ticker)

# to do 
def sell_trade_meta():
    ticker = add_sell_trade()
    configure_completed_trades_sheet(ticker) 

# to do 
def display_bonus_info():
    '''
    if no, then: 
    (1) display global p/l for the last day, week, month, and year in USD and BTC 
    (2) (optional) print the daily, weekly, monthly, yearly and all time P/L for each coin that is live 
    (3) print any news to the terminal that is relevant 
    (4) print the current sentiment of the market to terminal
    (5) print to terminal the reminder of my strategy 
    '''
    # step 1:
    display_global_pl()
    # step 2: 
    display_pl_of_current_positions()
    # step 3: 
    display_todays_news()
    # step 4: 
    display_current_sentiment()
    # step 5:
    display_stratagy_reminder()

# complete 
def update_portfolio_sheet():
    clear_portfolio_sheet()
    scan_tickers_from_live_trades_sheet()
    populate_token_name()
    populate_portfolio_prices()
    populate_portfolio_holdings()
    populate_portfolio_btc_totals()
    populate_portfolio_usd_totals()
    populate_grand_total_and_percentage()
    print('Portfolio Sheet Refreshed')






''' ---------------------------------------------------------------- ''' 
''' M A I N    F U N C T I O N S ''' 


''' portfolio''' 
# complete 
def clear_portfolio_sheet():
    cell_list = portfolio_sheet.range('A1:Z1000') # step 1: delete all fields in data sheet
    for cell in cell_list:
        cell.value = ''

    portfolio_sheet.update_cells(cell_list)  # step 2:   set row 1 values A-H as header_list 
    header_list = ['Token', 'Ticker', 'Coin Price BTC', 'Coin Price USD', 'Holdings', 'Total BTC', 'Total USD', 'Percentage of Total Portfolio', '', 'Total Value BTC', 'Total Value USD']
    cell_list = portfolio_sheet.range('A1:K1')
    counter = 0
    for cell in cell_list:
        cell.value = header_list[counter]
        counter += 1

    portfolio_sheet.update_cells(cell_list)

# complete 
def scan_tickers_from_live_trades_sheet():
    ''' get tickers of all live positions in cmc, then paste them in alphabetical order with btc, fiat, ltc, eth and xmr first, followed by alphabetical ordering''' 
    values_list = live_trades_sheet.row_values(2)  # step1: from live trades sheet, scan all of row 2 and append to list of tickers 
    values_list.pop(0)
    # step2: reorder list with (i) btc, (ii) usd, (iii) ltc, (iv) eth, (v) xmr, then rest in alphabetical order. 
    # step3: in portfolio sheet, in column b, from rows 3 to the n (where n is length of tickers list), paste in tickers. 
    cell_list = portfolio_sheet.range('B3:B' + str((len(values_list)) + 2 ))
    counter = 0
    for cell in cell_list:
        cell.value = values_list[counter]
        counter += 1 ##

    portfolio_sheet.update_cells(cell_list)

# complete
def populate_token_name():
    # step 1: select tickers from column b 
    values_list = portfolio_sheet.col_values(2)
    values_list.pop(0)
    values_list.pop(0)
    # step 2: manually map tickers to token names
    # step 3: from list of tickers, generate list of token names 
    token_name_list = []
    for i in values_list:
        if i in coin_url_extentions:
            token_name_list.append(coin_url_extentions[i])
        elif i not in coin_url_extentions:
            token_name_list.append('undefined ticker')

    # step 4: paste token_name_list to column a of portfolio 
    x = (len(token_name_list) + 2)
    cell_list = portfolio_sheet.range('A3:A' + str(x))
    counter = 0
    for cell in cell_list:
        cell.value = token_name_list[counter]
        counter += 1

    portfolio_sheet.update_cells(cell_list)

# complete 
def populate_portfolio_prices():
    ''' 
    Takes in all the token names from sheet 'API Data' column A, and adds the following information
    Column B: ticker
    Column C: price_btc
    Column D: price_usd
    ''' 
    # step1: fetch all tickers as a list 
    token_list = portfolio_sheet.col_values(1)
    # step2: make list of api links 
    links = []
    for i in token_list:
        if (i == 'undefined ticker'):
            links.append('undefined_ticker')
        else:
            links.append('https://api.coinmarketcap.com/v1/ticker/' + str(i))

    links.pop(0)
    links.pop(0)
    # step3: make list of data from api links
    main_list = []
    counter_1 = 0
    for each_link in links:
        if (each_link == 'undefined_ticker'): 
            main_list.append('0')
            main_list.append('0')
        elif (each_link != 'undefined_ticker'):
            if counter_1 < len(links):
                local_request = requests.get(each_link)
                local_api = json.loads(local_request.text)
                main_list.append(local_api[0]['price_btc'])
                main_list.append(local_api[0]['price_usd'])
                counter_1 += 1 

    # # step4: print to sheet 
    x = len(token_list)
    local_range = 'C3:D' + (str(x)) 
    cell_list = portfolio_sheet.range(local_range)
    counter_2 = 0
    for cell in cell_list:
        cell.value = main_list[counter_2]
        counter_2 += 1

    portfolio_sheet.update_cells(cell_list)

# complete
def populate_portfolio_holdings():
    values_list = live_trades_sheet.row_values(3)     # get holdings from live trades 
    values_list.pop(0)
    x = len(values_list) + 2     # paste to portfolio holdings column 
    cell_list = portfolio_sheet.range('E3:E' + str(x))
    counter = 0
    for cell in cell_list:
        cell.value = values_list[counter]
        counter += 1

    portfolio_sheet.update_cells(cell_list)

# complete
def populate_portfolio_btc_totals():
    coin_price_btc = portfolio_sheet.col_values(3)
    coin_price_btc.pop(0)
    coin_price_btc.pop(0)
    processed1_coin_price_btc = []
    for i in coin_price_btc:
        processed1_coin_price_btc.append(i.replace("฿", ""))
    
    processed2_coin_price_btc = []
    for i in processed1_coin_price_btc:
        processed2_coin_price_btc.append(i.replace(",", ""))

    coin_price_btc = list(map(float, processed2_coin_price_btc))
    holdings = portfolio_sheet.col_values(5)
    holdings.pop(0)
    holdings.pop(0)
    holdings = list(map(float, holdings))
    total_btc = [a*b for a,b in zip(coin_price_btc,holdings)]
    x = len(total_btc) + 2
    cell_list = portfolio_sheet.range('F3:F' + str(x))
    counter = 0
    for cell in cell_list:
        cell.value = total_btc[counter]
        counter += 1

    portfolio_sheet.update_cells(cell_list)

# complete
def populate_portfolio_usd_totals():
    coin_price_usd = portfolio_sheet.col_values(4)
    coin_price_usd.pop(0)
    coin_price_usd.pop(0)
    a = []
    for i in coin_price_usd:
        a.append(i.replace(",", ""))

    b = []
    for i in a:
        b.append(i.replace("$", ""))

    coin_price_usd = list(map(float, b))
    holdings = portfolio_sheet.col_values(5)
    holdings.pop(0)
    holdings.pop(0)
    holdings = list(map(float, holdings))
    total_usd = [a*b for a,b in zip(coin_price_usd,holdings)]
    x = len(total_usd) + 2
    cell_list = portfolio_sheet.range('G3:G' + str(x))
    counter = 0
    for cell in cell_list:
        cell.value = total_usd[counter]
        counter += 1

    portfolio_sheet.update_cells(cell_list)

# complete 
def populate_grand_total_and_percentage():
    total_btc = portfolio_sheet.col_values(6)     # populates total btc 
    total_btc.pop(0)
    total_btc.pop(0)
    a = []
    for i in total_btc:
        a.append(i.replace("฿", ""))

    total_btc = list(map(float, a))
    total_btc_sum = sum(total_btc)
    portfolio_sheet.update_acell('J3', total_btc_sum)
    total_usd = portfolio_sheet.col_values(7)     # populates total usd 
    total_usd.pop(0)
    total_usd.pop(0)
    b = []
    for i in total_usd:
        b.append(i.replace(",", ""))

    c = []
    for i in b:
        c.append(i.replace("$", ""))

    total_usd = list(map(float, c))
    total_usd_sum = sum(total_usd)
    portfolio_sheet.update_acell('K3', total_usd_sum)
    percentage = []     # step 3) calculate percentages
    for i in total_btc:
        percentage.append(i / total_btc_sum)

    x = len(total_btc) + 2
    cell_list = portfolio_sheet.range('H3:H' + str(x))
    counter = 0
    for cell in cell_list:
        cell.value = percentage[counter]
        counter += 1

    portfolio_sheet.update_cells(cell_list)


''' live trade update ''' 
# complete 
def update_live_trades_live_data():
    '''
        fields to update:
            Live Price BTC
            Live Price USD
            Date Today

            Current Value BTC
            Current Value USD
            Trade Duration (days)
            Capital Gain
            Unrealied P/L BTC
            Unrealised P/L USD
    '''
    # step 1: generate all lists 
    tickers = live_trades_sheet.row_values(2)
    tickers.pop(0)

    amounts = live_trades_sheet.row_values(3)
    amounts.pop(0)
    amounts = list(map(float, amounts))

    btc_prices = portfolio_sheet.col_values(3)
    btc_prices.pop(0)
    btc_prices.pop(0)
    btc_prices = list(map(float, btc_prices))

    usd_prices = portfolio_sheet.col_values(4)
    usd_prices.pop(0)
    usd_prices.pop(0)
    usd_prices = list(map(float, usd_prices))

    total_btc_costs = live_trades_sheet.row_values(6)
    total_btc_costs.pop(0)
    total_btc_costs = list(map(float, total_btc_costs))

    total_usd_costs = live_trades_sheet.row_values(7)
    total_usd_costs.pop(0)
    total_usd_costs = list(map(float, total_usd_costs))


    # step 2: initialise lists ready to paste into appropriate columns

    # dates_today = [] # to do 
    current_btc_values = []
    current_usd_values = []
    # trade_durations = [] # to do 
    # capital_gain_bools = [] # to do 
    unrealised_pl_btc_list = []
    unrealised_pl_usd_list = []

    # step 3: for each ticker, populate these lists. 
    counter = 0
    for i in tickers:
        # btc values 
        btc_value = btc_prices[counter] * amounts[counter]
        current_btc_values.append(btc_value)
        # usd values 
        usd_value = usd_prices[counter] * amounts[counter]
        current_usd_values.append(usd_value)
        # unrealised p/l btc 
        btc_pl = btc_value - total_btc_costs[counter]
        unrealised_pl_btc_list.append(btc_pl)
        # unrealised p/l usd
        usd_pl = usd_value - total_usd_costs[counter]
        unrealised_pl_usd_list.append(usd_pl)
        counter += 1

    # step 4: update rows 9 to 12 
    conc_list = btc_prices + usd_prices + total_btc_costs + total_usd_costs
    x = alphabet[len(btc_prices)]
    cell_list = live_trades_sheet.range('B9:' + str(x) + '12')
    counter = 0
    for cell in cell_list:
        cell.value = conc_list[counter]
        counter += 1

    live_trades_sheet.update_cells(cell_list)
    # step 5: update rows 18 to 19 
    conc_list = unrealised_pl_btc_list + unrealised_pl_usd_list
    x = alphabet[len(btc_prices)]
    cell_list = live_trades_sheet.range('B18:' + str(x) + '19')
    counter = 0
    for cell in cell_list:
        cell.value = conc_list[counter]
        counter += 1

    live_trades_sheet.update_cells(cell_list)

# to do 
def reorder_live_trades():
    pass


''' new buy trade ''' 
# complete 
def add_buy_trade():
    ''' adds all the new data based on user input, then returns the ticker for live trade and completed trade functions to process '''

    def create_new_sheet(ticker):
        new_sheet = sh.add_worksheet(title=ticker, rows="1000", cols="1000")
        initial_values = [
                            'BUY', 
                            'Unique ID',
                            'Trade ID',
                            'Completed',
                            'Amount',
                            'Price BTC',
                            'Price USD',
                            'Total BTC',
                            'Total USD',
                            'Date',
                            'Time',
                            'Exchange',
                            'Commission %',
                            'Commission Cost BTC',
                            'Commission Cost USD',
                            'Target',
                            'Stop Loss',
                            'R/R Ratio',
                            'Notes',
                            '',
                            'SELL (matched)',
                            'Unique ID',
                            'Raw Sell ID', 
                            'Trade ID',
                            'Completed',
                            'In Completed Trades',
                            'Amount',
                            'Price BTC',
                            'Price USD',
                            'Total BTC',
                            'Total USD',
                            'Date',
                            'Exchange',
                            'Notes',
                            '',
                            'SELL (raw)',
                            'Unique ID',
                            'Raw Sell ID', 
                            'Completed',
                            'Amount',
                            'Price BTC',
                            'Price USD',
                            'Total BTC',
                            'Total USD',
                            'Date',
                            'Exchange',
                            'Notes'
                            ]

        cell_list = new_sheet.range('A1:A47')
        counter = 0
        for cell in cell_list:
            cell.value = initial_values[counter]
            counter += 1

        new_sheet.update_cells(cell_list)    

    def add_new_ticker_to_live_trades(ticker):
        current_positions = live_trades_sheet.row_values(2)
        current_positions.pop(0)
        last_column = alphabet[len(current_positions) + 1]
        cell = str(last_column) + '2'
        live_trades_sheet.update_acell(cell, ticker)

    def next_trade_id(ticker, current_tickers_sheet):

        nums = current_tickers_sheet.row_values(3)
        nums.pop(0)
        if (len(nums) == 0):
            return str(ticker) + '1'
        else:
            a = []
            for i in nums:
                a.append(i.replace(ticker, ""))

            a = list(map(int, a))
            highest = max(a) + 1

            return str(ticker) + str(highest)

    def complete_task(ticker):
        current_tickers_sheet = sh.worksheet(ticker)
        ''' step 3: define variables to add to sheet ''' 
        trade_id = next_trade_id(ticker, current_tickers_sheet)
        completed = 'LIVE'
        amount = input('Enter Buy Amount\n')
        if (ticker == 'BTC'):
            price_btc = '1'
        else:
            price_btc = input('Enter Price BTC (Live Price is ' + fetch_price_btc(ticker) + ' sats.)\n')
        if (ticker == 'USD'):
            price_usd = '1'
        else: 
            price_usd = input('Enter Price USD (Live Price is $' + fetch_price_usd(ticker) + ' USD.)\n')
        total_btc = float(amount) * float(price_btc)
        total_usd = float(amount) * float(price_usd)
        date = str(datetime.datetime.now())
        time = str(datetime.datetime.now())
        exchange = input('Enter Exchange\n')
        commission = get_exchange_commission(exchange)
        commission_cost_btc = 0.1 * float(total_btc)
        commission_cost_usd = 0 * float(total_usd)
        target = input('Enter Trade Target\n')
        stop_loss = input('Enter Trade Stop Loss\n')
        r_r_ratio = calculate_r_r_ratio()
        notes = input('Enter Any Notes for this Trade\n')
        ''' step 4: add variables to list ready to be iterated over ''' 
        data_list = [trade_id, completed, amount, price_btc, price_usd, total_btc, total_usd, date, time, exchange, commission, commission_cost_btc, commission_cost_usd, target, stop_loss, r_r_ratio, notes]
        ''' step 5: find correct column based on the latest entry '''
        column_count_data = current_tickers_sheet.row_values(3)
        column_count = len(column_count_data)
        ''' step 6: select the column based on the index of the alphabet, then use rows 2 to 18 which are hard coded for the fields ''' 
        current_range = alphabet[column_count].upper() + '3:' + alphabet[column_count].upper() + '19'
        cell_list = current_tickers_sheet.range(current_range)
        ''' step 7: paste in the data_list to the appropriate cells ''' 
        counter = 0
        for cell in cell_list:
            if counter < len(data_list):
                cell.value = data_list[counter]
                counter += 1

        current_tickers_sheet.update_cells(cell_list)


    ticker = input('Enter Ticker\n') # find the ticker for this trade
    if ticker in coin_url_extentions.keys():
        existing_tickers = live_trades_sheet.row_values(2)  #check if this coin has been used before
        existing_tickers.pop(0)
        if any(ticker in s for s in existing_tickers):
            print('History found for this ticker, adding trade to existing sheet')
            complete_task(ticker)
        else:
            print('No history found for this ticker. Creating new sheet.')
            create_new_sheet(ticker)
            add_new_ticker_to_live_trades(ticker)
            complete_task(ticker)
        print('Todays trade successfully added to tickers sheet.')
        return ticker
    else:
        print("Ticker not in 'coin_url_extentions' variable. Add coinmarketcap API extention first before adding this coin.\n\n ")
        new_trade_meta()

# complete 
def configure_live_trades_sheet(ticker):

    ''' step 1: open ticker sheet based on the add_todays_trade() function. This WILL be generated by now whether new or existing ticker''' 
    if ticker not in coin_url_extentions.keys():
        print("Ticker not in 'coin_url_extentions' variable. Add coinmarketcap API extention first before adding this coin.\n\n ")
        new_trade_meta()
    else:
        current_tickers_sheet = sh.worksheet(ticker)
        ''' step 2: find columns that are 'LIVE' from relevant ticker sheet, make list of relevant column letters ''' 
        cell_list = current_tickers_sheet.findall("LIVE")
        if (len(cell_list) == 0): # if all buys have been matched with sells and holdings are now 0 
            print('No Live Trades Found. There are no currently no holdings of ' + str(ticker) +  '.') 
            # find the column of ticker in live trades
            all_live_tickers = live_trades_sheet.row_values(2)
            counter = 0
            col_to_remove = ''
            for i in all_live_tickers:
                if (i == ticker):
                    col_to_remove = alphabet[counter]

                counter += 1

            cell_list = live_trades_sheet.range(col_to_remove + '1:' + col_to_remove +'25')
            for cell in cell_list:
                cell.value = ''

            live_trades_sheet.update_cells(cell_list)
            reorder_live_trades()
        else:
            live_cols_list_numbers = []
            for i in cell_list:
                live_cols_list_numbers.append(i.col)

            col_list = []
            for i in live_cols_list_numbers:
                col_list.append(alphabet[i-1])
            ''' step 3: collect all information from multiple columns''' 
            list_of_amounts = []
            list_of_btc_spent=[]
            list_of_usd_spent = []
            for i in col_list:
                ''' amount (on row 4 of ticker sheet) ''' 
                each_amount = current_tickers_sheet.acell(str(i) + '5').value
                list_of_amounts.append(each_amount)
                ''' total btc spent (on row 7 of ticker sheet) ''' 
                each_btc_spent = current_tickers_sheet.acell(str(i) + '8').value
                list_of_btc_spent.append(each_btc_spent)
                ''' total usd spent (on row 8 of ticker sheet) ''' 
                each_usd_spent = current_tickers_sheet.acell(str(i) + '9').value
                list_of_usd_spent.append(each_usd_spent)

            ''' step 4: generate variables based of 'LIVE' data ''' 
            trade_id = 1
            amount = sum([float(i) for i in list_of_amounts])
            total_cost_btc = sum([float(i) for i in list_of_btc_spent])
            total_cost_usd = sum([float(i) for i in list_of_usd_spent])
            average_buy_price_btc = float(total_cost_btc) / float(amount)  # take sum of USD spent and divide it by amount of coins held 
            average_buy_price_usd = float(total_cost_usd) / float(amount)  # take sum of USD spent and divide it by amount of coins held 
            most_recent_buy_date = ''
            live_price_btc = fetch_price_btc(ticker)
            live_price_usd = fetch_price_usd(ticker)
            current_value_btc = float(live_price_btc) * float(amount)
            current_value_usd = float(live_price_usd) * float(amount)
            date_today = str(datetime.datetime.now())
            trade_duration = ''
            capital_gain = '' # boolean, true if over 366 days 
            total_commission_btc = ''
            total_commission_usd = ''
            unrealised_pl_btc = current_value_btc - total_cost_btc
            unrealised_pl_usd = current_value_usd - total_cost_usd
            notes = None
            ''' step 5: place variables in data_list ready to paste ''' 
            data_list = [trade_id, ticker, amount, average_buy_price_btc, average_buy_price_usd, total_cost_btc, total_cost_usd, most_recent_buy_date, live_price_btc, live_price_usd, current_value_btc, current_value_usd, date_today, trade_duration, capital_gain, total_commission_btc, total_commission_usd, unrealised_pl_btc, unrealised_pl_usd, notes] #etc 
            ''' step 6: find appropriate column based on ticker '''
            live_trades_sheet_ticker_cell = live_trades_sheet.find(ticker)
            correct_column_live_trades = alphabet[(live_trades_sheet_ticker_cell.col) - 1]
            ''' step 7: paste new data to sheet ''' 
            cell_list_live_trades = live_trades_sheet.range(str(correct_column_live_trades) + '1:' + str(correct_column_live_trades) + '20')
            counter = 0
            for cell in cell_list_live_trades:
                if counter < len(data_list):
                    cell.value = data_list[counter]
                    counter += 1

            live_trades_sheet.update_cells(cell_list_live_trades)
            print('New trade processed and included in live trades sheet.')

''' new sell trade '''

# to do 
def add_sell_trade():

    ''' section 1: function methods ''' 
    def add_to_sheet(data_list):
        values_list = current_tickers_sheet.row_values(24)
        x = alphabet[len(values_list)]
        cell_list = current_tickers_sheet.range(str(x) + '24:' + str(x) + '34')
        counter = 0
        for cell in cell_list:
            cell.value = data_list[counter]
            counter += 1

        current_tickers_sheet.update_cells(cell_list)

    def next_trade_id(ticker):
        nums = current_tickers_sheet.row_values(24)
        nums.pop(0)
        nums = [ x for x in nums if ticker not in x ]
        if (len(nums) == 0):
            return 'temp1'
        else: 
            a = []
            for i in nums:
                a.append(i.replace("temp", ""))

            a = list(map(int, a))
            num = max(a) + 1
            return 'temp' + str(num)

    def close_the_buy(trade_id):
        # changes the most recent live buy trade from 'live' to 'complete' if the sell amount is equal or greater than the buy amount. 
        cell = current_tickers_sheet.find(trade_id)
        column_num = cell.col 
        column = alphabet[column_num - 1]
        current_tickers_sheet.update_acell(str(column) + '4', 'COMPLETE')

    def multiply(amount, price):
        ''' ''' 
        return amount * price

    def make_buys_dict():
        # get list of all the buy columns with 'live' status 
        live_status_columns = []
        all_buy_trade_columns = current_tickers_sheet.row_values(4)
        all_buy_trade_columns.pop(0)
        counter = 1
        for i in all_buy_trade_columns:
            i = str(i)
            if (i == 'LIVE'):
                live_status_columns.append(counter)
        
            counter +=1 

        # get current buy amounts with live status 
        live_buy_amounts = []
        counter = 0
        all_buy_amounts_list = current_tickers_sheet.row_values(5)
        for i in live_status_columns:
            live_buy_amounts.append(all_buy_amounts_list[i])

        live_trade_ids = []
        all_trade_ids = current_tickers_sheet.row_values(3)
        counter = 0
        for i in live_status_columns:
            live_trade_ids.append(all_trade_ids[i])

        dictionary = dict(zip(live_trade_ids, live_buy_amounts))
        return dictionary

    def make_sells_dict():
        # get list of all the buy columns with 'live' status 
        live_status_columns = []
        all_sell_match_trade_columns = current_tickers_sheet.row_values(25)
        all_sell_match_trade_columns.pop(0)
        counter = 1
        for i in all_sell_match_trade_columns:
            i = str(i)
            if (i == 'LIVE'):
                live_status_columns.append(counter)
        
            counter +=1 

        # get current buy amounts with live status 
        live_sell_match_amounts = []
        counter = 0
        x = current_tickers_sheet.row_values(27)
        for i in live_status_columns:
            live_sell_match_amounts.append(x[i])

        live_trade_ids = []
        all_trade_ids = current_tickers_sheet.row_values(24)
        counter = 0
        for i in live_status_columns:
            live_trade_ids.append(all_trade_ids[i])

        dictionary = dict(zip(live_trade_ids, live_sell_match_amounts))
        return dictionary

    def compile_temps(ticker):
        '''buys prioritised in order of date (most recent first)
         sells prioritised in order of amount (lowest amount first) '''
        
        ''' section 1: getting the latest buys prioritised in order of recent first, and sells prioritised in order of amount first ''' 
        buy_dict = make_buys_dict()
        sell_dict = make_sells_dict()
        sorted_sells = sorted(sell_dict.items(), key=lambda kv: kv[1]) # here we reorder the sells dict into a list of tuples in order of size, smallest first 
        temp_sell_ids = []
        sell_amounts = []
        for i in sorted_sells:
            temp_sell_ids.append(i[0])
            sell_amounts.append(i[1])

        sorted_sells = dict(zip(temp_sell_ids, sell_amounts))
        latest_buy_num = 0  # buys prioritised by trade ID, where the larger the trade ID number, the more recent the trade. This seems sound logic until proven otherwise. 
        if (len(buy_dict) is not 0):
            a = []
            for i in buy_dict:
                a.append(i.replace((ticker), ""))

            a = list(map(int, a))
            latest_buy_num = max(a)
        
        prioritised_buy_key = str(ticker) + str(latest_buy_num)
        prioritised_sell_key = temp_sell_ids[0]
        prioritised_buy_value = float(buy_dict[prioritised_buy_key])  # next step: matching 
        

        ''' section 2: iterating over the live temp trades, adding them together and seeing if they match any live buy trades. '''
        total = 0 # where total is the current total of the sum of live temp sells 
        counter = 0
        for i in sell_amounts:
            i = float(i)
            ''' if smaller ''' 
            if prioritised_buy_value > total:
                total += i
                counter += 1
                if len(sell_amounts) == counter: # if all temps have been exhausted check conditions here 
                    ''' if equal ''' 
                    if prioritised_buy_value == total:
                        columns = []  # Update trade ID of all temps just used to the prioritised_buy_key
                        for j in temp_sell_ids:
                            cell = current_tickers_sheet.find(j)
                            columns.append(alphabet[(cell.col) - 1])

                        for j in columns: 
                            current_tickers_sheet.update_acell(str(j) + '24', prioritised_buy_key)
                            current_tickers_sheet.update_acell(str(j) + '25', 'COMPLETE')  #All temps used so far get their completed status updated from 'live' to 'completed' 
                        
                        close_the_buy(prioritised_buy_key) # the first buy itself gets its completed status updated from 'live' to 'completed' (easiest way is just to do this for each iteration even though its less efficient)
                        total = 0 # resetting counter and total to run the function again recursively 
                        counter = 0
                        if (len(make_sells_dict()) != 0): # if there are no temps left, then it won't recursively trigger. 
                            compile_temps(ticker) # recursively calling the function again to mop up and straggler temps 
                    elif (prioritised_buy_value < total):
                        remainder = total - prioritised_buy_value # fetching the remainder of the last temp minus the overhang compared to the prioritised buy 
                        columns = []  # Update trade ID of all temps just used to the prioritised_buy_key
                        for j in temp_sell_ids:
                            cell = current_tickers_sheet.find(j)
                            columns.append(alphabet[(cell.col) - 1])

                        for j in columns: 
                            current_tickers_sheet.update_acell(str(j) + '24', prioritised_buy_key)
                            current_tickers_sheet.update_acell(str(j) + '25', 'COMPLETE')  # All temps used so far get their completed status updated from 'live' to 'completed' 
                            close_the_buy(prioritised_buy_key) # The first buy itself gets its completed status updated from 'live' to 'completed' (easiest way is just to do this for each iteration even though its less efficient)

                        update_last_temp_amount = i - remainder  # find the most recent sell amount in the iteration and subtract the remainder from it. This is an additional step compared to if prioritised_buy_trade == value 
                        current_tickers_sheet.update_acell(str(columns[counter -1]) + '27', update_last_temp_amount) # then change this amount in the sheet under the most recent sell iteration 
                        current_tickers_sheet.update_acell(str(columns[counter -1]) + '30', float(current_tickers_sheet.acell(str(columns[counter -1]) + '27').value) * float(current_tickers_sheet.acell(str(columns[counter -1]) + '28').value)) # then change this amount in the sheet under the most recent sell iteration 
                        current_tickers_sheet.update_acell(str(columns[counter -1]) + '31', float(current_tickers_sheet.acell(str(columns[counter -1]) + '27').value) * float(current_tickers_sheet.acell(str(columns[counter -1]) + '29').value)) # long winded way of changing the amounts of the most recent sell iteration 
                        cell_list = current_tickers_sheet.range(str(columns[counter -1] + '24:' + str(columns[counter -1]) + '34')) # fetching the values of the most recent temp to copy to the split copy 
                        values = []
                        for cell in cell_list:
                            values.append(cell.value)

                        # then create a new temp with the remainder using the data from the most recent sell iteration. 
                        values[0] = next_trade_id(ticker) # altering the values so its a unique temp sell 
                        values[1] = 'LIVE'
                        values[2] = 'False'
                        values[3] = str(remainder)
                        values[6] = str(float(values[3]) * remainder)
                        values[7] = str(float(values[4]) * remainder)
                        values[10] = 'split'
                        num_of_cols = len(current_tickers_sheet.row_values(24)) # finding the next available column 
                        next_available_col = alphabet[num_of_cols]
                        cell_list = current_tickers_sheet.range(next_available_col + '24:' + next_available_col + '34') # pasting the values into the next column at appropriate rows
                        counter = 0
                        for cell in cell_list:
                            cell.value = values[counter]
                            counter += 1

                        current_tickers_sheet.update_cells(cell_list)
                        total = 0
                        counter = 0
                        if (len(make_sells_dict()) != 0): # checks to see if there are any temps left. If there are none it will throw an error. 
                            compile_temps(ticker) # recursively calling the function now all the date is down, and resetting totals and counter variables 
            

                        ''' final to do: clear any column data that who's amounts contain 'e-17', 'e-16' or 'e-15' as this is a python error ''' 

            
            # # find all the temps again. If any are found, run again. 
            # sell_dict = make_sells_dict()
            # sorted_sells = sorted(sell_dict.items(), key=lambda kv: kv[1]) # here we reorder the sells dict into a list of tuples in order of size, smallest first 
            # temp_sell_ids = []
            # sell_amounts = []
            # for i in sorted_sells:
            #     temp_sell_ids.append(i[0])
            #     sell_amounts.append(i[1])

            # sorted_sells = dict(zip(temp_sell_ids, sell_amounts))
            # if len(sorted_sells) is not 0:
            #     extra_conditions(i)


    def split_sell(ticker, dictionary, amount, price_btc, price_usd, exchange, notes):
        trade_id = next_trade_id(ticker)
        completed = 'LIVE'
        in_completed_trades = 'False'
        total_btc = float(amount) * float(price_btc)
        total_usd = float(amount) * float(price_usd)
        date = str(datetime.datetime.now())
        price_btc = float(price_btc)
        price_usd = float(price_usd)
        amount = float(amount)
        live_buys = (list(dictionary.values()))[::-1]
        most_recent_buy = float(live_buys[0])
        if len(live_buys) > 1: 
            second_recent_buy = float(live_buys[1])
            sum_of_two_recent_buys = most_recent_buy + second_recent_buy

        if (amount < most_recent_buy):
            data_list = [trade_id, completed, in_completed_trades, amount, price_btc, price_usd, total_btc, total_usd, date, exchange, notes]
            add_to_sheet(data_list)
        elif (amount == most_recent_buy):
            completed = 'COMPLETE'
            trade_id = ((list(dictionary.keys()))[::-1])[0]  #  we're (i) taking the dictionary keys and putting them in a list, (ii) reversing the list, (iii) taking the first index of that list to get our latest buy trade ID 
            data_list = [trade_id, completed, in_completed_trades, amount, price_btc, price_usd, total_btc, total_usd, date, exchange, notes]
            add_to_sheet(data_list)
            close_the_buy(trade_id)
        elif (amount > most_recent_buy) and (amount < sum_of_two_recent_buys):
            trade_id_1 = ((list(dictionary.keys()))[::-1])[0]
            amount_2 = amount - most_recent_buy
            amount_1 = amount - amount_2
            list_1 = [trade_id_1, 'COMPLETE', in_completed_trades, amount_1, price_btc, price_usd, multiply(amount_1, price_btc), multiply(amount_1, price_usd), date, exchange, notes]
            add_to_sheet(list_1)
            trade_id_2 = next_trade_id(ticker)
            list_2 = [trade_id_2, 'LIVE', in_completed_trades, amount_2, price_btc, price_usd, multiply(amount_2, price_btc), multiply(amount_2, price_usd), date, exchange, notes]
            add_to_sheet(list_2)
            close_the_buy(trade_id_1)
        elif (amount == sum_of_two_recent_buys):
            trade_id_1 = ((list(dictionary.keys()))[::-1])[0]
            amount_2 = amount - most_recent_buy
            amount_1 = amount - amount_2
            list_1 = [trade_id_1, 'COMPLETE', in_completed_trades, amount_1, price_btc, price_usd, multiply(amount_1, price_btc), multiply(amount_1, price_usd), date, exchange, notes]
            add_to_sheet(list_1)
            trade_id_2 = ((list(dictionary.keys()))[::-1])[1]
            list_2 = [trade_id_2, 'COMPLETE', in_completed_trades, amount_2, price_btc, price_usd, multiply(amount_2, price_btc), multiply(amount_2, price_usd), date, exchange, notes]
            add_to_sheet(list_2)
            close_the_buy(trade_id_1)
            close_the_buy(trade_id_2)
        elif (amount > sum_of_two_recent_buys):
            trade_id_1 = ((list(dictionary.keys()))[::-1])[0] 
            amount_2_wrong = amount - most_recent_buy 
            amount_1 = amount - amount_2_wrong 
            amount_3 = amount_2_wrong - second_recent_buy
            amount_2 = amount - amount_3 - amount_1
            list_1 = [trade_id_1, 'COMPLETE', in_completed_trades, amount_1, price_btc, price_usd, multiply(amount_1, price_btc), multiply(amount_1, price_usd), date, exchange, notes]
            add_to_sheet(list_1)
            trade_id_2 = ((list(dictionary.keys()))[::-1])[1]
            list_2 = [trade_id_2, 'COMPLETE', in_completed_trades, amount_2, price_btc, price_usd, multiply(amount_2, price_btc), multiply(amount_2, price_usd), date, exchange, notes]
            add_to_sheet(list_2)
            trade_id_3 = next_trade_id(ticker)
            print(trade_id_3)
            list_3 = [trade_id_3, 'LIVE', in_completed_trades, amount_3, price_btc, price_usd, multiply(amount_3, price_btc), multiply(amount_3, price_usd), date, exchange, notes]
            close_the_buy(trade_id_1)
            close_the_buy(trade_id_2)
            if amount_3 > 0:
                split_sell(ticker, make_buys_dict(), amount_3, price_btc, price_usd, exchange, notes)
            else:
                add_to_sheet(list_3)
        else:
            print('Error calculating sell amount to recent buy amounts')

    ''' section 2: function variables ''' 
    ticker = input('Enter Ticker\n').upper()
    if ticker in coin_url_extentions.keys():
        current_tickers_sheet = sh.worksheet(ticker)
        amount = input('Enter Amount\n')
        if (ticker == 'BTC'):
            price_btc = '1'
        else:
            price_btc = input('Enter Price BTC (Live Price is ' + fetch_price_btc(ticker) + ' sats.)\n')
        if (ticker == 'USD'):
            price_usd = '1'
        else: 
            price_usd = input('Enter Price USD (Live Price is $' + fetch_price_usd(ticker) + ' USD.)\n')
        exchange = input('Enter Exchange\n')
        notes = input('Enter Notes\n')
        ''' section 3: execution''' 
        user_input = input('Would you like to match this sell to a specific buy trade?\n (1) (Default) Match with the most recent trade.\n (2) Match with a specific trade ID code. \n')
        user_input = str(user_input)
        if (user_input == '1'):
            split_sell(ticker, make_buys_dict(), amount, price_btc, price_usd, exchange, notes)
        elif (user_input == '2'):
            buy_trade_id = input('Enter the buy trade ID to match\n') 
        else:
            print('Sorry, you need to choose (1) or (2). \n Please try again.')
            add_sell_trade()

        if (len(make_sells_dict()) != 0):
            compile_temps(ticker)
        
        return ticker
    else:
        print("\nTicker not in 'coin_url_extentions' variable. Add coinmarketcap API extention first before adding this coin.\n ")
        new_trade_meta()


    ''' to do:
    1) sort trade_id problem 
    2) trades to be stored in an additional global trade history sheet 
    3) sell trades to take into account any live temp sell trades current open first before processing their own. 


     '''

# to do 
def configure_completed_trades_sheet(ticker):


    # complete
    def add_to_sheet(data_list):
        print(data_list)
        print(len(data_list))
        values_list = completed_trades_sheet.col_values(1)
        if (len(values_list) == 1):
            cell_list = completed_trades_sheet.range('A2:AB2')
            counter = 0
            for cell in cell_list:
                cell.value = data_list[counter]
                counter += 1

            completed_trades_sheet.update_cells(cell_list)
        else:
            counter = 0
            next_available_row = len(values_list)
            cell_list = completed_trades_sheet.range('A' + str(next_available_row) + ':AB' + str(next_available_row))
            print(cell_list)
            counter = 0
            for cell in cell_list:
                cell.value = data_list[counter]
                counter += 1

            completed_trades_sheet.update_cells(cell_list)

    # complete
    def initialise_sheet():
        new_sheet = sh.add_worksheet(title="Completed Trades", rows="1000", cols="1000")
        row_1 = [
                    'Trade ID', 
                    'Unique Buy IDs', 
                    'Unique Sell IDs',
                    'Type',
                    'Coin',
                    'P/L BTC',
                    'P/L USD',
                    'Amount',
                    'Total Cost BTC',
                    'Total Cost USD',
                    'Total Sale BTC',
                    'Total Sale USD',
                    'Average Buy Price BTC',
                    'Average Buy Price USD',
                    'Average Sell Price BTC',
                    'Average Sell Price USD',
                    'Most Recent Buy Date',
                    'First Sell Date',
                    'Trade Duration',
                    'Capital Gain? (Canada)',
                    'Buy Commission BTC',
                    'Buy Commission USD',
                    'Sell Commission BTC',
                    'Sell Comission USD',
                    'Total Commission Cost BTC',
                    'Total Commission Cost USD',
                    'Exchanges Used',
                    'Notes'
                ]

        counter = 0
        cell_list = new_sheet.range('A1:AB1')
        for cell in cell_list:
            cell.value = row_1[counter]
            counter += 1

        new_sheet.update_cells(cell_list)

    # complete
    def fetch_columns_of_id(trade_id):
        ''' returns a list of two lists, first list is buy columns (for row 3-19 of ticker sheet), second list is sell columns (row 24 to 34 of tickers sheet) '''
        buy_columns = []
        sell_columns = []
        buy_section = current_tickers_sheet.row_values(3)
        counter = 0
        for i in buy_section:
            if i == trade_id:
                buy_columns.append(alphabet[counter])

            counter += 1

        sell_section = current_tickers_sheet.row_values(24)
        counter = 0
        for i in sell_section:
            if i == trade_id:
                sell_columns.append(alphabet[counter])

            counter += 1

        buy_and_sell_columns = []
        buy_and_sell_columns.append(buy_columns)
        buy_and_sell_columns.append(sell_columns)
        return buy_and_sell_columns

    # complete
    def fetch_buy_id(trade_id, buy_columns):
        buy_ids = []
        for i in buy_columns:
            data = current_tickers_sheet.acell(str(i) + '2').value
            buy_ids.append(data)

        return buy_ids

    # complete
    def fetch_raw_sell_id(trade_id, sell_columns):
        sell_ids = []
        for i in sell_columns:
            data = current_tickers_sheet.acell(str(i) + '23').value
            sell_ids.append(data)

        return sell_ids

    # complete
    def get_amount(trade_id, is_unique, buy_cols):
        ''' this function should run a check to make sure the sum of the sell amounts equals the buy amount to avoid fuck ups later'''
        # for now we'll run it assuming its right and add the check later 
        if (is_unique == True):
            val = current_tickers_sheet.acell(str(buy_cols[0]) + '5').value
            return val
        elif (is_unique == False):
            total = 0
            for i in buy_cols:
                val = current_tickers_sheet.acell(str(i) + '5').value
                total += float(val)

            return str(total)
        else:
            print('Error, is_unique variable neither true or false.')

    # complete
    def calculate_total_cost(trade_id, is_unique, pair, buy_cols):
        ''' again, there should be some additional checks here to make sure the totals are the same as the amounts * the prices ''' 
        if (pair == 'BTC'):
            row = '8'
        elif (pair == 'USD'):
            row = '9'
        else:
            print('Error, pair entered is neither BTC or USD')
            stop_program()

        if (is_unique == True):
            val = current_tickers_sheet.acell(str(buy_cols[0]) + row).value
            return val
        elif (is_unique == False):
            total = 0
            for i in buy_cols:
                val = current_tickers_sheet.acell(str(i) + row).value
                total += float(val)

            return str(total)
        else:
            print('Error, is_unique is neither True or False')
            stop_program()

    # complete
    def calculate_total_sale(trade_id, is_unique, pair, sell_cols):
        ''' again, there should be some additional checks here to make sure the totals are the same as the amounts * the prices ''' 
        if (pair == 'BTC'):
            row = '30'
        elif (pair == 'USD'):
            row = '31'
        else:
            print('Error, pair entered is neither BTC or USD')
            stop_program()

        if (is_unique == True):
            val = current_tickers_sheet.acell(str(sell_cols[0]) + row).value
            return val
        elif (is_unique == False):
            total = 0
            for i in sell_cols:
                val = current_tickers_sheet.acell(str(i) + row).value
                total += float(val)

            return str(total)
        else:
            print('Error, is_unique is neither True or False')
            stop_program()

    def fetch_recent_buy_date(trade_id, is_unique, buy_cols):
        return 1

    def fetch_first_sell_date(trade_id, is_unique, sell_cols):
        return 1

    def calculate_trade_duration(most_recent_buy_date, first_sell_date, buy_cols, sell_cols):
        return 1

    def calculate_capital_gain(trade_duration):
        return 1

    def calculate_buy_commission():
        return 1

    def calculate_sell_commission():
        return 1

    def fetch_exchanges_used(trade_id, is_unique, buy_cols, sell_cols):
        list_of_exchanges = ['Binance', 'Bittrex', 'Coinbase']
        return list_of_exchanges

    def fetch_notes(trade_id, is_unique, buy_cols, sell_cols):
        return 'notes'

    def execute(list_of_ids, is_unique):
        if is_unique == True:
            print('Executing Instances of Trade IDs that Appear Once')
        elif is_unique == False:
            print('Executing Instances of Trade IDs that Appear Multiple Times')
        else:
            print('Error, is_unique neither True or False.')
        for i in list_of_ids:
            buy_cols = (fetch_columns_of_id(i))[0]
            sell_cols = (fetch_columns_of_id(i))[1]
            trade_id = i
            unique_buy_id = fetch_buy_id(i, buy_cols)
            unique_sell_id = fetch_raw_sell_id(i, sell_cols)
            trade_type = 'long'
            coin = ticker
            amount = get_amount(trade_id, is_unique, buy_cols)
            most_recent_buy_date = fetch_recent_buy_date(trade_id, is_unique, buy_cols)
            first_sell_date = fetch_first_sell_date(trade_id, is_unique, sell_cols)
            trade_duration = calculate_trade_duration(most_recent_buy_date, first_sell_date, buy_cols, sell_cols)
            capital_gain = calculate_capital_gain(trade_duration)
            buy_commission_btc = calculate_buy_commission()
            buy_commission_usd = calculate_buy_commission()
            sell_commission_btc = calculate_sell_commission()
            sell_commission_usd = calculate_sell_commission()
            total_commission_btc = buy_commission_btc + sell_commission_btc
            total_commission_usd = buy_commission_usd + sell_commission_usd
            total_cost_btc = float(calculate_total_cost(trade_id, is_unique, 'BTC', buy_cols)) - buy_commission_btc
            total_cost_usd = float(calculate_total_cost(trade_id, is_unique, 'USD', buy_cols)) - buy_commission_usd
            total_sale_btc = float(calculate_total_sale(trade_id, is_unique, 'BTC', sell_cols)) - sell_commission_btc
            total_sale_usd = float(calculate_total_sale(trade_id, is_unique, 'USD', sell_cols)) - sell_commission_usd
            p_l_btc = total_sale_btc - total_cost_btc
            p_l_usd = total_sale_usd - total_cost_usd
            average_buy_price_btc = float(total_cost_btc) / float(amount)
            average_buy_price_usd = float(total_cost_usd) / float(amount)
            average_sell_price_btc = float(total_sale_btc) / float(amount)
            average_sell_price_usd = float(total_sale_usd) / float(amount)
            exchanges_used = fetch_exchanges_used(trade_id, is_unique, buy_cols, sell_cols)
            notes = fetch_notes(trade_id, is_unique, buy_cols, sell_cols)
            data_list = [
                        str(unique_buy_id),
                        str(unique_sell_id),
                        trade_id,
                        trade_type,
                        coin,
                        p_l_btc,
                        p_l_usd,
                        amount,
                        total_cost_btc,
                        total_cost_usd,
                        total_sale_btc,
                        total_sale_usd,
                        average_buy_price_btc,
                        average_buy_price_usd,
                        average_sell_price_btc,
                        average_sell_price_usd,
                        most_recent_buy_date,
                        first_sell_date,
                        trade_duration,
                        capital_gain,
                        buy_commission_btc,
                        buy_commission_usd,
                        sell_commission_btc,
                        sell_commission_usd,
                        total_commission_btc,
                        total_commission_usd,
                        str(exchanges_used),
                        str(notes)
                        ]

            success = add_to_sheet(data_list)
            if (success == True):
                print('Successfully added ' + str(i) + ' to completed trades.' ) # can also add other info here such as 'this amount, at this time, at this p/l'

    current_tickers_sheet = sh.worksheet(ticker)
    values_list = current_tickers_sheet.row_values(26)
    not_processed_cols = [] # make a list columns that have in_completed_trades status as false
    counter = 1
    for i in values_list:
        if i == 'False':
            not_processed_cols.append(counter)
        
        counter += 1

    a = []  
    for i in not_processed_cols:
        values_list = current_tickers_sheet.col_values(i)
        a.append(values_list[23])

    singular_ids = list(set([i for i in a if a.count(i)==1])) # get ids that appear only once 
    multiple_ids = list(set([i for i in a if a.count(i)>1])) # get ids that appear more than once 
    execute(singular_ids, False)
    execute(multiple_ids, True)
    # configure_live_trades_sheet(ticker)
    ''' 
    to do: 
    1. completed trade sheet should be flipped so it runs downwards vertically, not horizontally as it will get full up fast. 
    '''




''' ---------------------------------------------------------------------- ''' 
''' M I S C E L L A N I O U S    F U N C T I O N S  '''


# complete
def check_to_add_another_trade():
    response = input('Do you want to add another trade?\n 1. Yes \n 2. No\n' )
    response = str(response).upper()
    if response == '2':
        print('response is no, no new trade to be added')
    elif response == '1':
        print('response is yes, new trade to be added')
        new_trade_meta()

# complete 
def fetch_price_btc(ticker):
    
    
    result = get_url_extention(ticker)
    link = 'https://api.coinmarketcap.com/v1/ticker/' + str(result)
    local_request = requests.get(link)
    local_api = json.loads(local_request.text)
    price = local_api[0]['price_btc']
    return price 

# complete 
def fetch_price_usd(ticker):
    
    
    result = get_url_extention(ticker)
    link = 'https://api.coinmarketcap.com/v1/ticker/' + str(result)
    local_request = requests.get(link)
    local_api = json.loads(local_request.text)
    price = local_api[0]['price_usd']
    return price 

# to do 
def get_url_extention(ticker):

    if ticker in coin_url_extentions:
        return coin_url_extentions[ticker]
    elif ticker not in coin_url_extentions:
        return 'undefined ticker'
    else:
        return 'error in translating ticker to url extention'

# to do 
def get_exchange_commission(exchange):
    if exchange == 'binance' or 'Binance':
        return 0.075
    else:
        return 0.25
    # update later with all relevant prices 

# to do 
def calculate_r_r_ratio():
    ''' '''
    return 0

# to do 
def delete_ticker_from_live_trade_if_holdings_are_zero(ticker):
    ''' in the event of a sell trade setting total holdings to 0, in addition to adding trade to completed trade, 
        the live trades also needs to remove the ticker so as not to confuse the portfolio page '''
    pass 

def stop_program():
    print('Stopping Programme')

''' --------------------------------------------------------- ''' 
''' B O N U S    F E A T U R E S''' 

# to do 
def update_daily_tracker():
    pass

# to do 
def display_global_pl():
    pass

# to do 
def display_pl_of_current_positions():
    pass

# to do 
def display_todays_news():
    pass

# to do 
def display_current_sentiment():
    pass

# to do 
def display_stratagy_reminder():
    pass


def delete_all_data():
    pass






''' --------------------------------------------------------- ''' 
''' W O R K S H O P     A N D       E X E C U T E ''' 


''' 
To Do: 

1) When adding new sell, check the sell amount doesn't exceed the live buy amounts minus the live sell amounts 
2) Portfolio Seems to Load twice when should only do once. 
3) create a 'delete all data' function. This should clear (i) the portfolio sheet, (ii) the live trades sheet, 
    (iii) each ticker sheet 
4) Once everything is done, remove the 'Press 1 for Buy, 2 for Sell' when adding a new trade. Based on the users input of a
    positive or negative amount, the trade should be automatically identified as a buy or sell. 
5) Total BTC and Total USD in each tickers sheet will need to include the commission to the totals. 
6) In each ticker sheet, there could be a 'reason for sell' row with options (i) stop loss hit, (ii) target hit, (iii) altseason conditions not met 
7) Alerts that sends email when set. Alerts should be set in the main menu. 
8) Add a 'processed and added to completed trades' boolean in each tickers sheet. This will make sure all matches trades are processed. 
9) See if there's a google sheets library that allows you to change the UI of a sheet. If so, (i) change the text alignment to left on all tickers sheets.
    next, (ii) change any fields with 'COMPLETED' and 'LIVE' to different highlights. (iii) Change the currency to dollar and BTC in all sheets, 
    next (iv) reorder the tickers sheets to be after all the main sheets and in alphabetical order, 
10) If nothing is entered for notes, set default to 'No Notes Entered'
11) Extend alphabet variable so it goes up to ZZ (do this programmatically will be a good interview test)
12) It might be an idea to add some checks in place that data equals each other to avoid major fuck ups later. For example, when adding a trade
    to completed trades, when checking the amount, a function should check whether the buy amount matches with the sell amount. 
'''

# new_trade_meta()
configure_completed_trades_sheet('XLM')

