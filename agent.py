import platform
import subprocess
import time
import urllib3


http = urllib3.PoolManager()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/78.0.3904.97 Safa'}


def execute_command(command_issued):

    cmd = subprocess.Popen(command_issued, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE)
    success = cmd.stdout.read().decode("utf-8")
    error = cmd.stderr.read().decode("utf-8")

    if error is not '':
        return error

    return success


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
    computer_name = execute_command('hostname')
    req = http.request('POST', url, fields={'id': 8, 'host_name': 'more'}, headers=headers)
    response = str(req.data.decode('utf-8'))
    print('Response code: ' + str(req.status))
    print('Response: ' + response)


def get_techniques():
    url = 'http://localhost:8000/agent_techniques/5'
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
    result = []
    single_tech_command = []
    url = 'http://localhost:8000/agent_tasks/5'

    req = http.request('GET', url, headers=headers)
    response = str(req.data.decode('utf-8'))
    response_code = req.status
    # print('Response code: ' + str(req.status))
    # print('Response: ' + response)

    if response_code == 200:
        # Separates technique's commands into a list separated by ++
        technique_commands_lists = response.split('++')

        for technique_command_list in technique_commands_lists:
            if technique_command_list is ',' or technique_command_list is '':
                continue

            # single_tech_command: [net time, get date] [ run once ]
            single_tech_command = technique_command_list.split(',')

            # run: [net time, get date]
            for run in single_tech_command:
                if run == '':
                    continue

                result.append(execute_command(run))
            results.append(''.join(result))
            result.clear()

    return results


def send_output():
    results = download_and_run_commands()
    # url = 'http://localhost:8000/agent_tasks/5'
    techs = get_techniques()
    # http://localhost:8000/agent_techniques/5
    url = 'http://localhost:8000/agent_output'

    # Iterates over list of techniques assigned to an agent_tasks while selecting the respective result or output after
    # executing that technique
    for i in range(0, techs.__len__()):
        # try:
        req = http.request('POST', url, fields={'id': 5, techs[i]: results[i]}, headers=headers)
        print('Response code: ' + str(req.status))
        # time.sleep(4)
        # except IndexError:
        #     print('Index error')

    # print(results)
    # print(techs)
    # response = str(req.data.decode('utf-8'))
    # print('Response code: ' + str(req.status))
    # print('Response: ' + response)


# def form():
#     url = 'http://localhost:8000/campaign_delete'
#
#     req = http.request('POST', url, fields={'id': 6}, headers=headers)
#     response = str(req.data.decode('utf-8'))
#     print('Response code: ' + str(req.status))
#     print('Response: ' + response)


if __name__ == '__main__':
    print('Agent running')
    send_output()


