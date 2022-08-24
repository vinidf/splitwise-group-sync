from splitwise import Splitwise, Expense
from datetime import datetime, timedelta
from splitwise.user import ExpenseUser
import os

def sync_groups(request):
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    api_key = os.environ.get('API_KEY')
    source_group_id = 'ADD SOURCE GROUP ID HERE'
    destiny_group_id = 'ADD DESTINY GROUP ID HERE'
    destiny_user_id = 'ADD DESTINY USER ID HERE'
    destiny_user_id_2 = 'ADD DESTINY USER 2 ID HERE'

    s_obj = Splitwise(consumer_key, consumer_secret, api_key=api_key)
    week_ago = datetime.now() - timedelta(days=7)

    source_group_expenses = s_obj.getExpenses(updated_after=week_ago, group_id=source_group_id)
    destiny_group_expenses = s_obj.getExpenses(updated_after=week_ago, group_id=destiny_group_id)

    for expense in source_group_expenses:
        destiny_expense_user = next(x for x in expense.getUsers() if x.getId() == destiny_user_id)
        expense_exists_in_destiny_group = any(
            exp.getCost() == destiny_expense_user.getOwedShare()
            and exp.getDescription().strip() == expense.getDescription().strip()
            for exp in destiny_group_expenses)
        if not expense_exists_in_destiny_group:
            print('New expense found!')
            print(f'New expense description: {expense.getDescription()},  value: {destiny_expense_user.getOwedShare()}')
            print(f'Value to be paid: {destiny_expense_user.getOwedShare()}')
            new_expense = Expense()
            new_expense.setCost(destiny_expense_user.getOwedShare())
            new_expense.setDescription(expense.getDescription())
            user1 = ExpenseUser()
            user1.setId(destiny_user_id_2)
            user1.setPaidShare(destiny_expense_user.getOwedShare())
            user1.setOwedShare('0.00')

            user2 = ExpenseUser()
            user2.setId(destiny_user_id)
            user2.setPaidShare('0.00')
            user2.setOwedShare(destiny_expense_user.getOwedShare())

            users = [user1, user2]

            new_expense.setUsers(users)
            new_expense.setGroupId(destiny_group_id)

            new_expense, errors = s_obj.createExpense(new_expense)
            print(new_expense.getId())
    return 'OK'
