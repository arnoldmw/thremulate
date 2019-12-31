# noinspection PyUnresolvedReferences
# from runner import AtomicRunner
from .runner import AtomicRunner


def get_all_techniques_and_params():
    executor = AtomicRunner()
    tech = executor.techniques

    # key = 'T1002'

    tech_list = []
    parameters = []
    default_params = []
    commands = []

    for key in tech:
        if 'input_arguments' in tech[key]['atomic_tests'][0]:
            for p in tech[key]['atomic_tests'][0]['input_arguments'].keys():
                if p is not '':
                    parameters.append(p)

            for ig in tech[key]['atomic_tests'][0]['input_arguments'].keys():
                dp = tech[key]['atomic_tests'][0]['input_arguments'][ig]['default']
                default_params.append(dp)
                # print(tech[key]['atomic_tests'][0]['input_arguments'][ig]['default'])

        for comm in tech[key]['atomic_tests'][0]['executor']['command'].split('\n'):
            if comm is not '':
                commands.append(comm)

        tech_list.append(
            {'id': tech[key]['attack_technique'][1:], 'name': tech[key]['display_name'], 'params': parameters,
             'def_params': default_params, 'commands': commands}
        )
        parameters = []
        default_params = []
        commands = []

    return tech_list


def get_one_technique_and_params(key):
    executor = AtomicRunner()
    tech = executor.techniques

    parameters = []
    default_params = []
    commands = []

    if 'input_arguments' in tech[key]['atomic_tests'][0]:
        for p in tech[key]['atomic_tests'][0]['input_arguments'].keys():
            if p is not '':
                parameters.append(p)

        for ig in tech[key]['atomic_tests'][0]['input_arguments'].keys():
            dp = tech[key]['atomic_tests'][0]['input_arguments'][ig]['default']
            default_params.append(dp)
            # print(tech[key]['atomic_tests'][0]['input_arguments'][ig]['default'])

    for comm in tech[key]['atomic_tests'][0]['executor']['command'].split('\n'):
        if comm is not '':
            commands.append(comm)

    description = tech[key]['atomic_tests'][0]['description']

    return {'id': tech[key]['attack_technique'][1:], 'name': tech[key]['display_name'],'description': description,
            'params': parameters, 'def_params': default_params, 'commands': commands}


def get_all_techniques(agent_platform):
    executor = AtomicRunner()

    tech = executor.techniques

    # if 'windows' in tech[key]['atomic_tests'][0]['supported_platforms']:

    tech_list = []

    for key in tech:
        if agent_platform in tech[key]['atomic_tests'][0]['supported_platforms']:
            tech_list.append({'id': tech[key]['attack_technique'][1:], 'name': tech[key]['display_name']})

    return tech_list


def get_techniques_details():
    executor = AtomicRunner()

    tech = executor.techniques

    tech_list = []

    for key in tech:
        tech_list.append({'id': tech[key]['attack_technique'][1:], 'name': tech[key]['display_name']})

    return tech_list


def assign():
    executor = AtomicRunner()

    tech = executor.techniques

    print('---------------------------------------------')
    for key in tech.keys():
        print(tech[key]['attack_technique'])
        print(tech[key]['display_name'])
        print('---------------------------------------------')
        for at in tech[key]['atomic_tests']:
            # print(at)
            # platforms = tech[key]['atomic_tests'][0]['supported_platforms']
            platforms = at['supported_platforms']

            if 'input_arguments' in at.keys():
                params = at['input_arguments']
                # default_param = at['input_arguments']

                for p in params.keys():
                    default_params = params[p]['default']
                    print('Parameter: ' + p)
                    print('Default parameter value: ' + default_params)

            launcher_name = at['executor']['name']
            elevation_required = at['executor']['elevation_required']
            default_command = at['executor']['command']

            print(platforms)
            print('Launcher Name: ' + launcher_name)
            print('Administrator: ' + str(elevation_required))

            launcher = ''

            if launcher_name == 'command_prompt':
                launcher = 'C:\\Windows\\System32\\cmd.exe /C '

            if launcher_name == 'powershell':
                launcher = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe '

            for com in default_command.split('\n'):
                if com == "":
                    continue

                print('Execute: ' + launcher + com)

            print('---------------------------------------------')

    # # def execute(self, technique_name, position=0, parameters=None):
    # executor.execute("T1124")
    # # executor.execute("T1124", 0, {'computer_name': 'arnpc'})
    # command = executor.command
    # launcher = executor.launcher
    #


def get_commands(list_of_techs):
    executor = AtomicRunner()

    tech = executor.techniques

    # print(tech)

    commands_list = []

    print('---------------------------------------------')
    for key in list_of_techs:
        print(tech[key]['attack_technique'])
        for at in tech[key]['atomic_tests']:
            platforms = at['supported_platforms']

            if 'input_arguments' in at.keys():
                params = at['input_arguments']
                # default_param = at['input_arguments']

                for p in params.keys():
                    default_params = params[p]['default']

            launcher_name = at['executor']['name']
            # elevation_required = at['executor']['elevation_required']
            default_command = at['executor']['command']

            launcher = ''

            if launcher_name == 'command_prompt':
                launcher = 'C:\\Windows\\System32\\cmd.exe /C '

            if launcher_name == 'powershell':
                launcher = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe '

            for com in default_command.split('\n'):
                if com == "":
                    continue

                commands_list.append(launcher + com)
        commands_list.append('++')

    return commands_list


def better_get_commands(technique_list, plat, params):
    executor = AtomicRunner()
    executor.platform = plat
    # def execute(self, technique_name, position=0, parameters=None):
    # {'input_file'}
    # {'input_file'}

    i = 0
    all_commands = []
    for tech in technique_list:
        executor.execute(tech, 0, params[i])
        i = i + 1

        for command in executor.command.split('\n'):
            if command is not '':
                comm = executor.launcher + ' ' + command
                all_commands.append(comm)
        all_commands.append('++')

    return all_commands


if __name__ == '__main__':
    print('run_atomic')
    # one = get_one_technique_and_params('T1002')
    # print(one)

    # executor = AtomicRunner()
    # executor.execute("T1124", 0, {'computer_name': 'arnpc'})
    # command = executor.command
    # launcher = executor.launcher
    m = better_get_commands(['T1002', 'T1082'], 'windows',
                            [{'input_file': 'C:\\pen\\certs', 'output_file': 'C:\\test\\Data.zip'}, None])
    # m = better_get_commands(['T1005', 'T1002'], 'windows')
    print(m)

    # k = get_all_techniques()

    # n = get_all_techniques_and_params()
    # print(n)
