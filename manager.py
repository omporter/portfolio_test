import time


from main import new_trade_meta, display_bonus_info
from main import start_up_jobs

user_input = 0

while True:
    start_up_jobs()
    print('\n\nGood Morning, Oliver.')
    time.sleep(2)
    print('The Price of Bitcoin is 6254.56 today.')
    time.sleep(2)
    print('The Outlook for Crypto Markets today is:')
    time.sleep(2)
    print('Bullish: 23%')
    time.sleep(2)
    print('Neutral: 57%')
    time.sleep(2)
    print('Bearish: 33%')
    time.sleep(2)

    user_input = input("Any New Trades to Add Today? \n 1. Y \n 2. N \n\n ...")
    if user_input == 'Y' or 'y' or '1' or 1:
        option_1()
    elif user_input == 'N' or 'n' or '2' or 2:
        option_2()
    elif user_input != 'Y' or 'y' or '1' or 1 or 'N' or 'n' or '2' or '2':
        print('Goodbye...')
        break

    