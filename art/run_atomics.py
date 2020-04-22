#      Thremulate executes Network Adversary Post Compromise Activities.
#      Copyright (C) 2020  Mwesigwa Arnold
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

# noinspection PyUnresolvedReferences
# from runner import AtomicRunner
from pathlib import Path

import yaml
from .runner import AtomicRunner

matrix = {'persistence': [1156, 1015, 1182, 1103, 1138, 1131, 1067, 1176, 1042, 1136, 1038,
                          1157, 1133, 1044, 1179, 1062, 1215, 1161, 1159, 1160, 1168, 1162,
                          1031, 1128, 1050, 1137,
                          1034, 1013, 1163, 1164, 1060, 1180, 1101, 1058, 1023, 1165, 1019,
                          1501, 1209, 1100, 1084, 1004],
          'privilege_escalation': [1068, 1183, 1178, 1166, 1169, 1206],
          'impact': [1485, 1486, 1491, 1488, 1487, 1499, 1495, 1490, 1498, 1496, 1494, 1489,
                     1492, 1493],
          'command_and_control': [1043, 1092, 1090, 1094, 1024, 1132, 1001,
                                  1172, 1483, 1008, 1104, 1188, 1026, 1079,
                                  1219, 1105, 1071, 1032, 1095, 1065, 1102],
          'exfiltration': [1020, 1002, 1022, 1030, 1048, 1041, 1011, 1052, 1029],
          'collection': [1123, 1119, 1115, 1074, 1213, 1005, 1039, 1025, 1114, 1056,
                         1185, 1113, 1125],
          'lateral_movement': [1017, 1175, 1210, 1037, 1075, 1097, 1076, 1021, 1091, 1184, 1051,
                               1080, 1077],
          'execution': [1155, 1059, 1173, 1106, 1129, 1203,
                        1061, 1177, 1086, 1053, 1035, 1153, 1072,
                        1154, 1204, 1047, 1028],
          'credential_access': [1098, 1139, 1110, 1003, 1081, 1214, 1212, 1187, 1141, 1208, 1142,
                                1171, 1040, 1174, 1145, 1167, 1111],
          'discovery': [1087, 1010, 1217, 1482, 1083, 1046, 1135, 1201, 1120, 1069, 1057, 1012,
                        1018, 1063, 1082, 1016, 1049, 1033, 1007, 1124],
          'defense_evasion': [1134, 1197, 1009, 1088, 1191, 1146, 1116, 1500, 1223, 1109, 1122,
                              1196, 1207, 1073, 1140, 1089, 1480, 1211, 1181, 1107, 1222, 1006,
                              1144, 1484, 1148, 1158, 1147, 1143, 1054, 1066, 1070, 1202, 1130,
                              1118, 1149, 1152, 1036, 1112, 1170, 1096, 1126, 1027, 1150, 1205,
                              1186, 1093, 1055, 1108, 1121, 1117, 1014, 1085, 1198, 1064, 1218,
                              1216, 1045, 1151, 1221, 1099, 1127, 1078, 1497, 1220]}


def get_one_technique_and_params(key, platform):
    """
    Retrieves the tests and test parameters in a technique.
    :param key: ID of the technique whose tests will be retrieved.
    :param platform: Platform the agent is running on.
    :return: Dictionary with details and tests of a technique.
    """
    tech_path = Path(__file__).parent / 'atomics/{0}/{1}.yaml'.format(key, key)
    with open(tech_path) as f:
        data = yaml.safe_load(f)

    parameters = []
    all_technique_tests = []
    description = ''

    # Looping through atomic tests
    for index, test in enumerate(data['atomic_tests']):

        # Checking for applicable tests for agent platform
        if platform in test['supported_platforms']:

            if 'input_arguments' in test.keys():
                # Obtaining parameter names and default values
                for p in test['input_arguments'].keys():
                    parameters.append({
                        'pname': p,
                        'pvalue': test['input_arguments'][p]['default']})

            # Adding executor and parameter names with default values dictionary
            all_technique_tests.append(
                {'test_id': index, 'test_name': test['name'], 'description': test['description'], 'params': parameters,
                 'at_test': test['executor']
                 })

            parameters = []
        else:
            continue

    return {'id': data['attack_technique'][1:], 'name': data['display_name'], 'description': description,
            'tests': all_technique_tests}


def get_all_techniques(agent_platform):
    """
    Retrieves all the techniques available and groups them basing on their tactic.
    :param agent_platform: Platform the agent is running on.
    :return: List of dictionaries with 'tactics' and their respective 'techniques'
    """
    executor = AtomicRunner()

    tech = executor.techniques

    details_matrix = {'persistence': [],
                      'privilege_escalation': [],
                      'impact': [],
                      'command_and_control': [],
                      'exfiltration': [],
                      'collection': [],
                      'lateral_movement': [],
                      'execution': [],
                      'credential_access': [],
                      'discovery': [],
                      'defense_evasion': []}

    for key in tech:
        for test in tech[key]['atomic_tests']:

            if agent_platform in test['supported_platforms']:
                tech_id = int(tech[key]['attack_technique'][1:])
                if tech_id in matrix['discovery']:
                    details_matrix['discovery'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['defense_evasion']:
                    details_matrix['defense_evasion'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['collection']:
                    details_matrix['collection'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['exfiltration']:
                    details_matrix['exfiltration'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['privilege_escalation']:
                    details_matrix['privilege_escalation'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['command_and_control']:
                    details_matrix['command_and_control'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['credential_access']:
                    details_matrix['credential_access'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['execution']:
                    details_matrix['execution'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['lateral_movement']:
                    details_matrix['lateral_movement'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break
                if tech_id in matrix['persistence']:
                    details_matrix['persistence'].append({'id': tech_id, 'name': tech[key]['display_name']})
                    break

    return details_matrix


def agent_commands(technique_list, plat, params):
    """
    Retrieves agent instructions and passes them to a route.
    :param technique_list: List of techniques assigned to an agent.
    :param plat: Platform the agent is running on.
    :param params: Parameters for test's execution.
    :return: String of agent instructions.
    """
    executor = AtomicRunner()
    executor.platform = plat

    all_commands = []
    for index, tech in enumerate(technique_list):
        executor.execute(tech['tech_id'], tech['test_num'], params[index])
        comm = ''
        for command in executor.command.split('\n'):
            if command is '':
                continue
            elif 'powershell' in executor.launcher:
                comm = comm + command + ';'
            elif 'cmd' in executor.launcher:
                comm = comm + command + ' & '
            elif '/sh' in executor.launcher:
                comm = comm + command + ';'

        if 'powershell' in executor.launcher:
            comm = comm.replace('"', "\'")
            if '|' in comm:
                comm = '\"& {}\"'.format(comm)
                all_commands.append('powershell' + ' -Command ' + comm + '++')
            else:
                comm = '\"{}\"'.format(comm)
                all_commands.append('powershell' + ' -Command ' + comm + '++')

        elif 'cmd' in executor.launcher:
            all_commands.append(comm + '++')

        elif '/sh' in executor.launcher:
            all_commands.append(comm + '++')

    return all_commands


def techniques_for_db():
    """
    Retrieves IDs and Names for techniques from the yaml files.
    :return: A list of dictionaries containing the 'id' and 'name' of a technique.
    """
    executor = AtomicRunner()
    tech = executor.techniques

    data = []
    for key in tech.keys():
        data.append({'id': int(tech[key]['attack_technique'][1:]), 'name': tech[key]['display_name']})

    return data


if __name__ == '__main__':
    print('run_atomic')
