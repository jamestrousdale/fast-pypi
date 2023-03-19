import sys
from pathlib import Path

from pydantic import BaseSettings, Field
from pypiserver.backend import IBackend
from pypiserver.config import RunConfig


class FastPypiSettings(BaseSettings):
    """Settings for the pypi server."""

    data_dir: str = Field(
        description='Disk directory into which the artifacts are stored',
        env='FAST_PYPI_DATA_DIR',
    )

    enable_cache: bool = Field(
        description='Enable caching backend',
        env='FAST_PYPI_ENABLE_CACHE',
        default=True,
    )

    @property
    def data_dir_path(self):
        return Path(self.data_dir)

    @property
    def pypiserver_config(self) -> RunConfig:
        return RunConfig(
            roots=[self.data_dir_path],
            verbosity=1,
            # TODO: Configurable log formats
            log_frmt=(
                "%(asctime)s|%(name)s|%(levelname)s|%(thread)d|%(message)s"
            ),
            log_err_frmt='%(body)s: %(exception)s \n%(traceback)s',
            log_file=None,
            log_stream=sys.stdout,
            hash_algo='SHA256',
            backend_arg='cached-dir' if self.enable_cache else 'simple_dir',
            # Hardcoding fallback disable for now
            disable_fallback=True,
            fallback_url='https://pypi.org/simple/',
            # Allow overwriting, for now
            overwrite=True,
            # TODO: Allow a configurable welcome message
            welcome_msg='Welcome to fast_pypi!',
            # TODO: Configurable cache control
            cache_control=86400,
            # The following arguments need to be provided but aren't used due
            # to the fact that we are reimplementing our own application
            host='',
            port=0,
            authenticate=[],
            password_file='.',
            server_method=None,
            log_req_frmt='',
            log_res_frmt='',
        )

    @property
    def file_backend(self) -> IBackend:
        return self.pypiserver_config.backend
