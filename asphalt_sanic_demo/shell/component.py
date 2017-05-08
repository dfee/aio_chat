import logging
import sqlite3

from asphalt.core import CLIApplicationComponent
from IPython import get_ipython

from ..component import ApplicationStartMixin
from .shell import Shell

logger = logging.getLogger(__name__)


class ShellComponent(ApplicationStartMixin, CLIApplicationComponent):
    async def run(self, ctx):
        shell = Shell(ctx)
        await shell.run()
        # Reconnect to prevent sqlite3 ProgrammingError
        # https://github.com/ipython/ipython/issues/680#issuecomment-2154854
        hist = get_ipython().history_manager
        hist.db = sqlite3.connect(hist.hist_file, check_same_thread=False)
