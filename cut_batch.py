from logging import getLogger
from pathlib import Path

import yaml

from transportstreamarchiver.cut import cut

logger = getLogger(__name__)


def convert(value: float) -> str:
    return f"{value//3600:02.0f}:{value % 3600//60:02.0f}:{value % 60:06.3f}"


if __name__ == "__main__":
    config = yaml.safe_load(Path("cut.yml").read_text("utf-8"))
    for each_cut in config["cut"]:
        file_input = Path(config["path"]) / config["name"]
        replaced_name = each_cut["name"].replace(" ", "-")
        file_output = Path(config["path"]) / f"{Path(config['name']).stem}-{replaced_name}.ts"
        string_from = convert(each_cut["from"])
        string_to = convert(each_cut["to"])
        logger.info(file_input)
        logger.info(file_output)
        logger.info(string_from)
        logger.info(string_to)
        cut(file_input, file_output, string_from=string_from, string_to=string_to)
