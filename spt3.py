#stpminiv2.py

from IPython.display import HTML, display
from IPython.utils.capture import capture_output
from IPython.core.magic import register_cell_magic
from datetime import datetime
import sys, random
import pandas as pd
import json
import requests
from zoneinfo import ZoneInfo
import os

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
    def send_welcome(code_name):
            message = f'''
            <h4 style='color: brown;'>Welcome!</h4>
            <p>Your code name is: <b style='color: maroon'>{code_name}</b></p>
            <p>{Helper.get_random_welcome()}</p>
            '''
            display(HTML(message))
    
    def already_logged():
        print(f"You are already logged in.", file=sys.stderr, flush=True)
        print(f"Your code name is:{code_name}")
        print("Please continue the exercises!")
        print("If you want to change user, please restart the kernel and run the login cell again.", file=sys.stderr, flush=True)
        
#---------------------------------------


code_name = None
def validate_user(uid, login_id, nbid="None"):
    global code_name
    data = {"user_id": uid, 
            "login_id": login_id, 
            'event': "login",
            "notebook_id": nbid,
            'entries': get_ipython().execution_count,
            'timestamp': datetime.now(ZoneInfo('Asia/Dubai')).isoformat(),
            'version': '0.3'}
    print(f"Validating data for...{login_id}")
    try:
        response = requests.post(f"{server_url}/validate_user", 
                                 json=data, 
                                 timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        if response.status_code == 400:
            print(f"User ID or Login incorrect: {data['user_id']}, {data['login_id']}", file=sys.stderr)
        elif response.status_code == 401:
            print(f"Login and User ID do not match: {data['user_id'], data['login_id']}", file=sys.stderr)
        elif response.status_code == 409:
            print(f"Conflict error: {response.text}" , file=sys.stderr)
        else:
            print(f"Error validating the user: {data['user_id'], data['login_id']}", file=sys.stderr)
            #print("Please ensure the URL is correct.", file=sys.stderr)
            print("Error:", e)
        return False
    code_name = response.json()['code_name']
    return True

def add_to_dataframe(self):
    self.df_course_data.loc[len(self.df_course_data)] = list(self.payload.values())
    display(self.df_course_data)

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

def send_cell_execution_event(cp, thein, captured=None):
    entries = get_ipython().execution_count # [entry for entry in dir() if entry.startswith('_i')]
    
    data = (captured.stdout.strip() + "\n" + captured.stderr.strip()) if captured else ""
    #print("Sending checkpoint data to server...", data)
    payload = {
        'user_id': code_name,
        'event': 'checkin',
        'cp': cp,
        'timestamp': datetime.now().isoformat(),
        'content': thein,
        'output': data,
        'entries': entries
    }
    #print("Payload prepared:", payload)
    send_to_server("track_progress", payload)

def get_user_info(self):
    return {"user_id":self.user_id, "login": self.login, "code_name":self.code_name}
def get_status(self):
    return self.df_course_data

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


def load_credentials(nbid, debug = False, env_path='.env'):
    """
    Loads credentials from a .env file using dotenv if available,
    otherwise falls back to manual parsing.
    
    Parameters:
        env_path (str): Path to the .env file.
    
    Returns:
        dict: Dictionary of loaded credentials.
    """
    if logged:
        Helper.already_logged()
        return
    credentials = {}

    try:
        # Try to import dotenv
        import dotenv
        dotenv.load_dotenv(dotenv_path=env_path)

        '''
        # Collect all environment variables defined in the file
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key = line.strip().split('=', 1)[0]
                    credentials[key] = os.getenv(key)
        '''
        # Alternatively, if you know the specific keys you want 
    except ImportError:
        print("⚠️ python-dotenv not available, using manual fallback")

        # Manual parsing fallback
        try:
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                        credentials[key] = value
        except FileNotFoundError:
            print(f"❌ .env file not found at path: {env_path}")

    userid = os.getenv('USERID')
    userid = int(userid) if userid and userid.isdigit() else None
    loginid = os.getenv('LOGINID')
    if userid is None or loginid is None:
        print("❌ USERID or LOGINID not found in environment variables.")
        return None
        
    print("✅ Loaded credentials using python-dotenv")
    login(userid, loginid, nbid, debug)
    #return credentials  

def login(user_id, login_id, nbid="None", debug=False):
    global logged, server_url, code_name, userid, loginid
    code_name = None

    try:
        if user_id is None or login_id is None:
                raise ValueError("You should provide both userid and loginid to continue.")
    except Exception as e:
        print(f"Error:{e}", file=sys.stderr)
        return
    
    if debug:
        server_url = "http://" + "localhost" + ":5000"
        print("Server URL:", server_url)
    else: 
        server_url = "https://yahamid.pythonanywhere.com"
    
    if validate_user(user_id, login_id, nbid):
        userid = user_id
        loginid = login_id
        df_course_data = pd.DataFrame(columns = ['code_name', 'timestamp', 'cell_content', 'cell_output'])
        Helper.send_welcome(code_name)
        logged = True
    else:
        print("Login error.", file=sys.stderr)

'''
def register_checkpoint_magic():
    try:
        from IPython.core.magic import register_cell_magic
        ip = get_ipython()
        if register_cell_magic and ip:
            @register_cell_magic
            def checkpoint(cp, thein):
                get_ipython().run_cell(thein)
                send_cell_execution_event(cp, thein)
            print("Cell magic 'checkpoint' registered.")
        else:
            print("Not in Jupyter environment. Cell magic not registered.", file=sys.stderr)
    except (ImportError, NameError):
        print("IPython not available. Cell magic not registered.", file=sys.stderr)

'''

@register_cell_magic
def checkpoint(cp, thein):
    if not logged:
        print("You are not logged in. Please log in first by running the login cell.", file=sys.stderr)
        return
    with capture_output() as captured:
        get_ipython().run_cell(thein)
    # captured.stdout contains printed output
    # captured.stderr contains error output
    # captured.outputs contains rich outputs (displayed objects)
    
    if captured.outputs:
        for output in captured.outputs:
            #print(dir(output))
            print(output.data['text/plain'])

    if captured.stdout:
        print(captured.stdout)

    if captured.stderr:
        print("Error Output:", file=sys.stderr)
        print(captured.stderr)
    #print(captured.stderr)
    # You can now send captured.stdout or captured.outputs to your server or save them
    #get_ipython().run_cell(thein)
    
    send_cell_execution_event(cp, thein.strip(), captured)
 
