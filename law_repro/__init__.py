from pathlib import Path
import sys

import law
import luigi
from law.contrib.singularity import SingularitySandbox

root = Path(__file__).resolve().parent.parent / "app"


class Greet(law.SandboxTask):
    """
    The base task we would like to run where we send
    a greeting to a file from inside a container.
    """

    name = luigi.Parameter()
    sandbox = "singularity::app.sif"

    @property
    def singularity_forward_law(self) -> bool:
        return False

    @property
    def singularity_allow_binds(self) -> bool:
        return True

    def sandbox_env(self, env):
        pythonpath = env.get("PYTHONPATH", "")
        pythonpath = "/usr/local/lib/python3.10/site-packages:" + pythonpath
        print("Attempting to set PYTHONPATH to:", pythonpath)
        return {"PYTHONPATH": pythonpath}

    def run(self):
        # these lines are just here to illustrate
        # that PYTHONPATH isn't coming out as expected
        import os
        print("Inside container, PYTHONPATH is:", os.environ["PYTHONPATH"])

        # this is the real meat of what run would be.
        # greeter is the name of the library that we
        # installed from app/ inside the container
        from greeter import greet
        with open(self.output(), "w") as f:
            sys.stdout = f
            greet(self.name)

    def output(self):
        return law.LocalFileTarget("greeting.txt")


class DevSandbox(SingularitySandbox):
    """
    Simple sandbox that maps host application code
    into install directory inside the container.
    """

    sandbox_type = "singularity_dev"

    def _get_volumes(self):
        volumes = super()._get_volumes()
        if self.task and getattr(self.task, "dev", False):
            volumes[root] = "/opt/app"
            return volumes


class DevTask(law.SandboxTask):
    """
    Base task class that leverages the
    dev sandbox above
    """
    dev = luigi.BoolParameter(default=False)
    sandbox = "singularity_dev::app.sif"


class DevGreet(DevTask, Greet):
    """
    Perform the greeting task but now with the
    option of using dev code at the command line
    """

    pass
