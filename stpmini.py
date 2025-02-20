#stpmini.py

from IPython.display import HTML
import numpy as np



def question(n):
    print(f'{n}. ' + ge.QHA[f'q{n}'])


def hint(n):
    print(ge.QHA[f'h{n}'])


def answer(n):
    print(ge.QHA[f'a{n}'])


def pick():
    n = np.random.randint(1, 100)
    question(n)


class Helper:
    @staticmethod
    def get_random_welcome():
        msgs = [
            "It is fun to have you!",
            "A new day, a new lab!",
            "Ready to complete the tasks?",
            "Let's complete the lab tasks...",
            "Marhaba! let's do the hands on",
            "Let's make your day by learning more!",
            "Advancing your AI skills. That's all you need now!",
            "Smile :)  You are working.",
            "You need a mix of hard work and long work. Let's go!",
            ]
        return msgs[int(random.random()*len(msgs))]
    
    @staticmethod
    def send_welcome(pseudo_name):
            message = f'''
            <h4 style='color: brown;'>Welcome!</h4>
            <p>Your pseudo name is: <b style='color: maroon'>{pseudo_name}</b></p>
            <p>{Helper.get_random_welcome()}</p>
            '''
            display(HTML(message))
    
    def already_logged():
        print(f"You are already logged in.", file=sys.stderr, flush=True)
        print(f"Your pseudo name is:{pseudo_name}")
        print("Please continue the exercises!")
        
#---------------------------------------
import pandas as pd
from datetime import datetime
import json
import requests
from IPython.core.magic import register_cell_magic, register_line_magic
from datetime import datetime
import sys, random

pseudo_name = None
def validate_user(uid, loginid):
    global pseudo_name
    data = {"user_id": uid, 
            "login": loginid, 
            'event_type': "welcome",
            'timestamp': datetime.now().isoformat()}
    print(f"Validating data...{uid, loginid}")
    try:
        response = requests.post(f"{server_url}/validate_user", 
                                 json=data, 
                                 timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        if response.status_code == 400:
            print(f"User ID or Login incorrect: {data['user_id']}, {data['login']}", file=sys.stderr)
        elif response.status_code == 401:
            print(f"Login and User ID do not match: {data['user_id'], data['login']}", file=sys.stderr)
        else:
            print(f"Error validating the user: {data['user_id'], data['login']}", file=sys.stderr)
            print("Please ensure the URL is correct.", file=sys.stderr)
        return False
    pseudo_name = response.json()['pseudo_name']
    print(f"Psuedo is:{pseudo_name}")
    return True

def add_to_dataframe(self):
    self.df.loc[len(self.df)] = list(self.payload.values())
    display(self.df)

def send_to_server(method, data):
    try:
        response = requests.post(
            f"{server_url}/{method}",
            json = data,
            timeout = 5
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending progress: send2server {e}")

def send_cell_execution_event(cp, thein):
    entries = get_ipython().execution_count # [entry for entry in dir() if entry.startswith('_i')]
    payload = {
        'user_id': userid,
        'event_type': 'checkin',
        'cp': cp,
        'timestamp': datetime.now().isoformat(),
        'cell_content': thein,
        'cell_output': [],
        'entries': entries
    }
    send_to_server("track_progress", payload)

def get_user_info(self):
    return {"user_id":self.user_id, "login": self.login, "pseudo_name":self.pseudo_name}
def get_status(self):
    return self.df

def get_program():
    try:
        response = requests.get(
            f"{server_url}/get_program")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error getting progress: {e}")
    return pd.DataFrame(response.json())


#---------------------------------------------------

def track_progress(data):
    if not logged:
        print("You are not logged in. Please log in first by running the login cell.", file=sys.stderr)
        return
    # Assuming tracker is pre-configured globally
    print("In track progress")
    print(In[-1])
    print("---")
    data.show()
    return
    try:
        send_cell_execution_event(In[-1], data)
        
        #data.show()
    except Exception as e:
        print(f"Error sending the progress...{e.args}", file=sys.stderr)
        #spt.send_cell_execution_event(cell, str(e))
#     return result.result

logged = False
server_url = None
userid = loginid = None

def login(user_id, login_id, url):
    global logged, server_url, pseudo_name, userid, loginid
    if logged:
        Helper.already_logged()
        return
    try:
        if user_id is None or login_id is None or url is None:
                raise ValueError("You should provide all three values: userid loginid url")
    except Exception as e:
        print(f"Error:{e}", file=sys.stderr)
        return
    serverr_url = "http://" + url.split(":")[-1] + ":5000"
    pseudo_name = None

    server_url = "https://yahamid.pythonanywhere.com"
    if validate_user(user_id, login_id):
        userid = user_id
        loginid = login_id
        df = pd.DataFrame(columns = ['user_id', 'timestamp', 'cell_content', 'cell_output'])
        Helper.send_welcome(pseudo_name)
        logged = True
    else:
        print("Login error.", file=sys.stderr)

@register_cell_magic
def checkpoint(cp, thein):
    get_ipython().run_cell(thein)
    send_cell_execution_event(cp, thein)
    
import os
import nbformat as nbf
import mdutils

questions = 12

def ktx_to_dict(input_file, keystarter='<'):
    """ parsing keyed text to a python dictionary. """
    answer = dict()

    with open(input_file, 'r+', encoding='utf-8') as f:
        lines = f.readlines()

    k, val = '', ''
    for line in lines:
        if line.startswith(keystarter):
            k = line.replace(keystarter, '').strip()
            val = ''
        else:
            val += line

        if k:
            answer.update({k: val.strip()})

    return answer


def dict_to_ktx(input_dict, output_file, keystarter='<'):
    """ Store a python dictionary to a keyed text"""
    with open(output_file, 'w+') as f:
        for k, val in input_dict.items():
            f.write(f'{keystarter} {k}\n')
            f.write(f'{val}\n\n')


#HEADERS = ktx_to_dict(os.path.join('source', 'headers.ktx'))
#QHA = ktx_to_dict(os.path.join('source', 'exercises.ktx'))


def create_jupyter_notebook(destination_filename='Pandas Lab 3.ipynb'):
    """ Programmatically create jupyter notebook with the questions (and hints and solutions if required)
    saved under source files """

    # Create cells sequence
    nb = nbf.v4.new_notebook()

    nb['cells'] = []

    # - Add header:
    nb['cells'].append(nbf.v4.new_markdown_cell(HEADERS["header"]))
    nb['cells'].append(nbf.v4.new_markdown_cell(HEADERS["sub_header"]))
    nb['cells'].append(nbf.v4.new_markdown_cell(HEADERS["jupyter_instruction"]))

    # - Add initialisation
    nb['cells'].append(nbf.v4.new_code_cell('%run initialise.py'))

    # - Add questions and empty spaces for answers
    for n in range(1, questions + 1):
        nb['cells'].append(nbf.v4.new_markdown_cell(f'#### {n}. ' + QHA[f'q{n}']))
        nb['cells'].append(nbf.v4.new_code_cell(""))

    # Delete file if one with the same name is found
    if os.path.exists(destination_filename):
        os.remove(destination_filename)

    # Write sequence to file
    nbf.write(nb, destination_filename)


def create_jupyter_notebook_random_question(destination_filename='100_Numpy_random.ipynb'):
    """ Programmatically create jupyter notebook with the questions (and hints and solutions if required)
    saved under source files """

    # Create cells sequence
    nb = nbf.v4.new_notebook()

    nb['cells'] = []

    # - Add header:
    nb['cells'].append(nbf.v4.new_markdown_cell(HEADERS["header"]))
    nb['cells'].append(nbf.v4.new_markdown_cell(HEADERS["sub_header"]))
    nb['cells'].append(nbf.v4.new_markdown_cell(HEADERS["jupyter_instruction_rand"]))

    # - Add initialisation
    nb['cells'].append(nbf.v4.new_code_cell('%run initialise.py'))
    nb['cells'].append(nbf.v4.new_code_cell('import numpy as np'))
    nb['cells'].append(nbf.v4.new_code_cell("pick()"))

    # Delete file if one with the same name is found
    if os.path.exists(destination_filename):
        os.remove(destination_filename)

    # Write sequence to file
    nbf.write(nb, destination_filename)


def create_markdown(destination_filename='100_Numpy_exercises', with_hints=False, with_solutions=False):
    # Create file name
    if with_hints:
        destination_filename += '_with_hints'
    if with_solutions:
        destination_filename += '_with_solutions'

    # Initialise file
    mdfile = mdutils.MdUtils(file_name=destination_filename)

    # Add headers
    mdfile.write(HEADERS["header"] + '\n')
    mdfile.write(HEADERS["sub_header"] + '\n')

    # Add questions (and hint or answers if required)
    for n in range(1, questions + 1):
        mdfile.new_header(title=f"{n}. {QHA[f'q{n}']}", level=4, add_table_of_contents="n")
        if with_hints:
            mdfile.write(f"`{QHA[f'h{n}']}`")
        if with_solutions:
            mdfile.insert_code(QHA[f'a{n}'], language='python')

    # Delete file if one with the same name is found
    if os.path.exists(destination_filename):
        os.remove(destination_filename)

    # Write sequence to file
    mdfile.create_md_file()


def create_rst(destination_filename, with_ints=False, with_answers=False):
    # TODO: use rstdoc python library.
    #  also see possible integrations with https://github.com/rougier/numpy-100/pull/38
    pass

    