name = 'Oliver'
time_of_day = 'Morning'

while True:
    print('Good ' + str(time_of_day) + ', ' + str(name) +  '.')
    user_input = input("Add A New Trade? \n 1. Yes \n 2. No \n")
    user_input = str(user_input)
    if user_input == '1':
        from main import new_trade_meta
        new_trade_meta()
    elif user_input == '2':
        print('User Input is 2. No Trade to Add.')
        from main import display_bonus_info, update_portfolio_sheet, stop_loss_alerts
        update_portfolio_sheet()
        stop_loss_alerts()
        display_bonus_info()
    elif user_input != 'Y' or 'y' or '1' or 1 or 'N' or 'n' or '2' or '2':
        print('Please Enter 1 for New Trade or 2 to check features.')
        break

    