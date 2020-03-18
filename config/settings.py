import pathlib
import yaml

THIS_DIR = pathlib.Path(__file__).parent
config_path = THIS_DIR / 'thremulate.yaml'


def get_config(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    return data


config = get_config(config_path)
