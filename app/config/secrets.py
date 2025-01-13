import os
import sys
from loguru import logger
from dotenv import dotenv_values
from phase import GetAllSecretsOptions, Phase


def load():
    _cfg = _config()
    phase_token = _cfg.get("PHASE_TOKEN", "")
    if phase_token:
        print("Loading envvars from phase")
        return _load_from_phase(_cfg)

    print("phase token missing or invalid")
    return False


def to_env(s):
    if sys.version_info[0] == 2:
        return s.encode(sys.getfilesystemencoding() or "utf-8")
    return s


def _config() -> dict:
    _cfg = _config_from_dotenv()
    _cfg = _config_from_osenv(_cfg)
    _cfg = _validate_config(_cfg)
    return _cfg


def _validate_config(_cfg: dict) -> dict:
    if not _cfg.get("PHASE_PROJECT"):
        msg = "PHASE_PROJECT is required"
        logger.error(msg)
        raise Exception(msg)
    if not _cfg.get("PHASE_TOKEN"):
        msg = "PHASE_TOKEN is required"
        logger.error(msg)
        raise Exception(msg)
    if not _cfg.get("PHASE_HOST"):
        msg = "PHASE_HOST is required"
        logger.error(msg)
        raise Exception(msg)
    return _cfg


def _config_from_dotenv() -> dict:
    """Create a config dict for communicating with Phase using the values in the
    .env file

    Returns:
        dict: Our config
    """
    _cfg = {}
    envvars = dotenv_values()
    _cfg["PHASE_PROJECT"] = envvars.get("PHASE_PROJECT")
    _cfg["PHASE_TOKEN"] = envvars.get("PHASE_TOKEN")
    _cfg["PHASE_HOST"] = envvars.get("PHASE_HOST", "https://phase.hacnet.dev")
    if not _cfg.get("PHASE_TOKEN"):
        _cfg["PHASE_TOKEN"] = envvars.get("PHASE_SERVICE_TOKEN")
    return _cfg


def _config_from_osenv(_cfg: dict) -> dict:
    """If we're missing any of the required vars, then let's try adding
    them from the os.environ

    Args:
        _cfg (dict): Description

    Returns:
        dict: Hopefully our complete config
    """
    if not _cfg.get("PHASE_PROJECT"):
        _cfg["PHASE_PROJECT"] = os.environ.get("PHASE_PROJECT")
    if not _cfg.get("PHASE_TOKEN"):
        _cfg["PHASE_TOKEN"] = os.environ.get("PHASE_TOKEN")
    if not _cfg.get("PHASE_TOKEN"):
        _cfg["PHASE_TOKEN"] = os.environ.get("PHASE_SERVICE_TOKEN")
    if not _cfg.get("PHASE_HOST"):
        _cfg["PHASE_HOST"] = os.environ.get("PHASE_HOST", "https://phase.hacnet.dev")
    return _cfg


def _load_from_phase(cfg):
    phase = Phase(
        init=False,
        pss=cfg["PHASE_TOKEN"],
        host=cfg["PHASE_HOST"],
    )
    get_options = GetAllSecretsOptions(
        env_name=os.environ.get("SERVER_ENV"),
        app_name=cfg["PHASE_PROJECT"],
    )
    vars_set = dict()
    secrets = phase.get_all_secrets(get_options)
    for secret in secrets:
        k = secret.key
        v = secret.value
        if os.environ.get(k, None) is None:  # noqa: SIM102
            if k is not None and k is not None:
                key = to_env(k)
                val = to_env(v)
                os.environ[key] = val
                vars_set[key] = val
    return vars_set


load()
