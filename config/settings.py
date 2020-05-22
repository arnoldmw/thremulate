#      Thremulate executes Network Adversary Post Compromise Behavior.
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

import pathlib
import yaml

THIS_DIR = pathlib.Path(__file__).parent
config_path = THIS_DIR / 'thremulate.yaml'


def get_config(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    return data


config = get_config(config_path)
