"""
Loads the configuration file for the optimizer and the case.
All the configuration files are stored in a TOML file.
"""

import tomllib

from u_obj_loader import UObjLoader, UObjData


class UConfig:
    def __init__(self, case_config, optimizer_config):
        self.random_seed = optimizer_config["random_seed"]
        self.sample_size = optimizer_config["sample_size"]
        self.iterations = optimizer_config["iterations"]
        self.temperature = optimizer_config["temperature"]
        self.sigma = optimizer_config["sigma"]

        # Case-specific
        self.file_name = case_config["file_name"]
        self.path = case_config["obj_path"] + case_config["file_name"] + ".obj"
        self.doors = case_config["doors"]  # [room_i, room_j, *door_length]
        self.front_door = case_config["front_door"]  # edge_i, ratio(pos)


class ULoader:
    __config = None

    @classmethod
    def load_config(cls, config_path="configs.toml"):
        with open(config_path, "rb") as f:
            cls.__config = tomllib.load(f)
        return cls

    @classmethod
    def get_config_and_obj(cls, case_id) -> tuple[UConfig, UObjData]:
        if cls.__config is None:
            raise RuntimeError(
                "Configuration not loaded. Call ULoader.load_config() first."
            )
        case_config = cls.__config["cases"][case_id]
        return (
            UConfig(case_config, cls.__config["optimizer"]),
            UObjLoader.load(
                case_config["obj_path"] + case_config["file_name"] + ".obj"
            ),
        )

    @classmethod
    def get_obj(cls, case_id) -> UObjData:
        if cls.__config is None:
            raise RuntimeError(
                "Configuration not loaded. Call ULoader.load_config() first."
            )
        path = (
            cls.__config["cases"][case_id]["obj_path"]
            + cls.__config["cases"][case_id]["file_name"]
            + ".obj"
        )
        return UObjLoader.load(path)

    @classmethod
    def get_config(cls, case_id) -> UConfig:
        if cls.__config is None:
            raise RuntimeError(
                "Configuration not loaded. Call ULoader.load_config() first."
            )
        case_config = cls.__config["cases"][case_id]
        return UConfig(case_config, cls.__config["optimizer"])


if __name__ == "__main__":
    config = ULoader.load_config().get_config(0)
    print(config.random_seed)
    print(config.sample_size)
    print(config.iterations)
    print(config.temperature)
    print(config.path)
