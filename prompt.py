from simple_term_menu import TerminalMenu

def menu_index(options):
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    return menu_entry_index

def menu(options):
    menu_entry_index = menu_index(options)
    selection = options[menu_entry_index]
    return selection

def dict_menu(dict_options):
    selection = menu(list(dict_options.keys())) # Convert keys to list and make a menu
    selected_function = dict_options.get(selection) # Get the method that corresponds to the selected key
    selected_function() # Invoke the method