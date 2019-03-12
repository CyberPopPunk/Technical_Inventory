# Work inverntory log for HAC equipment
# 12/4/2018

# Save Items to different SQL tables in a db and take inventory easily
# Three main functions: Input Data, View Data, Take Inventory on Equip
#

import ui
import sqlalchemy as sa
from time import sleep

conn = sa.create_engine('sqlite:///tech_inv.db')
inspector = sa.inspect(conn)

def create_table():
	# if table doesn't exist...generates a new SQL table for the db. Tables have 6 columns with the 6th reserved for a generated ID#
	# users specify type if the column is a number (num) or description (word)
	new_table_list = []
	print('What is the new Table name?')
	new_table = input('New Table: ').lower()
	curr_tables = [x.lower() for x in inspector.get_otable_names()]
	if new_table in curr_tables:
		print('Table already exists!')
		return
	else:
		new_table_list.append(new_table)
	for col in range(1,6):
		print('What is in column {}?'.format(col))
		new_table_list.append(input("Column {}: ".format(col)))
		print('What type of input is this?(num, word, boolean)')
		input_type = input("Type: ").lower()
		if input_type == 'number' or input_type == 'num':
			new_table_list.append("INT")
		elif input_type == 'bool' or input_type =='boolean':
			new_table_list.append('')
		else:
			new_table_list.append('VARCHAR(20)')		
	print('Are these values correct? Y/N')
	print(new_table_list)
	if input('Confirm: ').lower() == 'y':
		sql_call = '''CREATE TABLE {}
		({} {},
		{} {},
		{} {},
		{} {},
		{} {},
		id VARCHAR(3) PRIMARY KEY)'''.format(*new_table_list)
		print(sql_call)
		conn.execute(sql_call)
	else:
		print('Let\'s try again\n')
		create_table()

def show_table_info(tb_name):
	table_info = conn.execute('SELECT * FROM {}'.format(tb_name))
	for num, row in enumerate(table_info):
		print('Item {}: {}'.format(num+1, row))
		print('-'*60)
	
def choose_input(list, title, prompt):
	# Prints a numbered list and prompts the user for input based on numerical selection
	# returns choice
	while True:
		print(title)
		for num, index in enumerate(list):
			print('{}. {}'.format(num + 1, index))
		try:
			choice = int(input(prompt))
			if choice > len(list):
				raise ValueError()
			break
		except ValueError or ValueError:
			print('Invalid Entry\n')
	return list[choice - 1] # compensate for list index

def table_select(title):
	tables = conn.table_names()
	selected_table = choose_input(tables, title, '--> ')
	print("\nYou selected {}".format(selected_table))
	return selected_table
	
def input_items(table):
	# takes a table and lists out the available columns
	# prompts for values and inserts them into the table in database
	
	col_info = inspector.get_columns(table) # returns a list of dicts of attributes for each column
	
	cols = []
	new_col_vals = []
	enter_items = True
	#iterate over dicts in list
	for i in range(len(col_info)):
		#for each dict in list of dicts get 'name' from each and add it to cols list
		cols.append(col_info[i].get('name'))
	#clean cols into tuple for SQL INSERT
	cols = tuple(cols)
		
	while enter_items == True:
	
	# Prompt for new values	
		for col in cols:
			if col == 'id':
				continue
			new_val = input('What is the {} of new item? >>>  '.format(col))
			print('\n')
			new_col_vals.append(new_val)
		
		print('Values input: {}'.format(new_col_vals))
		values_avail = '?,'*(len(cols)-2) + '?' #max number of columns minus 1 reserved for ID generation
		print('values avail' + values_avail)
		try:
			new_id = generate_ID()
		except:
			try:
				new_id = generate_ID()
			except:
				print('You\'re one unlucky bastard. You generated the same ID twice that already exists. \nPlease try inputting item again.... \nReturning to Main Menu...')
	
		#add generated ID to input data
		new_col_vals.append(new_id)
	
		#compile SQL insert
		ins = 'INSERT INTO {} {} VALUES {}'.format(table, cols, tuple(new_col_vals))
		print(ins) 
		#conn.execute(ins)
		#print('insert success!\n')
		print('FAKE INSERT A SUCCESS! PLEASE ACTIVATE \'INSERT\' SQL query to store data!')
		while True:
			more = input(('Enter another item? Y/N ')).lower()
			try:
				if len(more) > 1:
					raise ValueError("Input too long")
				if more =='y':
					break
				elif more == 'n':
					print('Returning to Main Menu...\n')
					return
				else:
					print('Invalid Input')
			except ValueError:
				print('Invalid Input! please try again')

				
def generate_ID():
	# generates and returns a 4 digit hexdigit (without 0x header) to be used for an ID
	# also searches Database to verify hex doesn't already exist yet
	from random import randint
	new_id = '{:x}'.format(randint(1, 16**4))
	print('New ID: # ' + new_id)
	print('Checking if ID exists')
	#searches all tables in db
	for table in conn.table_names():
		print('Looking through table {}...'.format(table))
		#selecets the ID columns in databse
		selected_IDs = conn.execute('SELECT id FROM {}'.format(table))
		for row in selected_IDs:
			print('Checking {}...'.format(row))
			if row == new_id:
				raise Exception('ID already in use! Please try again')
		print('ID not used in table {}...'.format(table))
	print('ID not in use')
	return new_id
	
	
def inventory():
	import string
	curr_inv_list = []
	
	#turn this into its own function!
	counted_id = None
	print('Please input an ID number, when inventory complete, type \'done\'.')
	while counted_id != 'done':
		while True:
			counted_id = input('ID#: ').lower()
			if all(char in string.hexdigits for char in counted_id) and len(counted_id) <= 4:
				curr_inv_list.append(counted_id)
			elif counted_id == 'done':
				break
			else:
				print('INVALID ID, please re-enter')

	total_ids = []
	total_missing = []
	for table in conn.table_names():
		#print('Checking Table: {}'.format(table))
		table_result = conn.execute('SELECT id FROM {}'.format(table))
		table_ids = [table_id[0] for table_id in table_result]
		#print('Category IDs for {}: {}'.format(table, table_ids))
		inv_results = missing_items(curr_inv_list, table_ids)
		print("______Overview of {} Category______\nMissing Items: {}\nUnknown Items count:{}".format(table, inv_results[0], len(inv_results[1])))
		for item in inv_results[2]:
			curr_inv_list.remove(item)	
		for item in inv_results[0]:
			total_missing.append(item)
	print('Total Items Missing: {}\n__MISSING ITEMS__'.format(len(total_missing)))
	
	#print the info for the missing items
	for table in conn.table_names():
		table_result = conn.execute('SELECT * FROM {}'.format(table))
		for row in table_result:
			if row['id'] in total_missing:
				print(row)
	
			
def missing_items(counted_items_list, expected_items_list):
	# takes two lists as args, counted and expected
	# returns lists of missing items and unknown items
	# missing items are items not in counted list from expected
	# unknown items are items in counted list not in expected
	missing_items = [item for item in expected_items_list if item not in counted_items_list]
	unknown_items = [item for item in counted_items_list if item not in expected_items_list]
	found_items = [item for item in expected_items_list if item in counted_items_list]
	return [missing_items, unknown_items, found_items]
	
def main_menu():
	while True:
		print('\nWelcome to Inventory!')
		print('1. Create Category')
		print('2. Input Items')
		print('3. Show Category Contents')
		print('4. Take Inventory')
		print('5. Exit')
		try:
			choice = int(input("Please select an action: "))
			if choice > 5:
				raise ValueError()
			break
		except ValueError:
			print("Invalid choice\n")	
	if choice == 1:
		create_table()
	elif choice == 2:
		selected_table = table_select('\nWhat category would you like to enter the item in?\n')
		input_items(selected_table)
	elif choice == 3:
		selected_table = table_select('\nWhat category of items would you like to view?\n')
		show_table_info(selected_table)
	elif choice == 4:
		inventory()

def exit_app(sender):
	print('\nGoodbye!')
	exit()

#main_menu()
v = ui.load_view('tech_gui').present('sheet')
