Quick dummy example illustrating some `law` workflow questions, and in particular acting as a repro for some issues in implementing a custom sandbox class.
`app` is the library that we want to install inside the container, while `law_repo` contains the `law` tasks for running the container and executing the app code inside of it.

## Run instructions
To run, first build the application container:

```console
apptainer build app.sif apptainer.def
```

### Issue #1: Using container python interpreter
First we can try to run the base task _without_ our custom sandbox class.

```console
law run law_repro.Greet --local-scheduler --name Thom
```

This should raise an issue that looks like:

```console
DEBUG: Checking if Greet(name=Thom) is complete
INFO: Informed scheduler that task   Greet_Thom_af59ec2587   has status   PENDING
INFO: Done scheduling tasks
INFO: Running Worker with 1 processes
DEBUG: Asking scheduler for work...
DEBUG: Pending tasks: 1
INFO: [pid 2788032] Worker Worker(salt=2417965045, workers=1, host=dgx1, username=alec.gunny, pid=2788032) running   Greet(name=Thom)
Attempting to set PYTHONPATH to: /usr/local/lib/python3.10/site-packages:

=============================== entering sandbox ===============================
task   : Greet_Thom_af59ec2587
sandbox: singularity::app.sif
================================================================================

/home/alec.gunny/.bashrc: line 30: bind: warning: line editing not enabled
/home/alec.gunny/miniconda3/lib/python3.9/site-packages/requests/__init__.py:102: RequestsDependencyWarning: urllib3 (1.26.9) or chardet (5.2.0)/charset_normalizer (2.0.12) doesn't match a supported version!
  warnings.warn("urllib3 ({}) or chardet ({})/charset_normalizer ({}) doesn't match a supported "
DEBUG: Checking if Greet(name=Thom) is complete
INFO: Informed scheduler that task   Greet_Thom_af59ec2587   has status   PENDING
INFO: Done scheduling tasks
INFO: Running Worker with 1 processes
DEBUG: Pending tasks: 0
INFO: [pid 2788123] Worker Worker(salt=2417965045, workers=1, host=dgx1, username=alec.gunny, pid=2788032) running   Greet(name=Thom)
ERROR: [pid 2788123] Worker Worker(salt=2417965045, workers=1, host=dgx1, username=alec.gunny, pid=2788032) failed    Greet(name=Thom)
Traceback (most recent call last):
  File "/law_forward/py/luigi/worker.py", line 203, in run
    new_deps = self._run_get_new_deps()
  File "/law_forward/py/luigi/worker.py", line 138, in _run_get_new_deps
    task_gen = self.task.run()
  File "/home/alec.gunny/projects/law-config-repro/law_repro/__init__.py", line 43, in run
    from greeter import greet
ModuleNotFoundError: No module named 'greeter'
DEBUG: 1 running tasks, waiting for next task to finish
INFO: Informed scheduler that task   Greet_Thom_af59ec2587   has status   FAILED
INFO: This progress looks :( because there were failed tasks
Inside container, PYTHONPATH is: /law_forward/py:
Attempting to set PYTHONPATH to: /usr/local/lib/python3.10/site-packages:

=============================== leaving sandbox ================================
task   : Greet_Thom_af59ec2587
sandbox: singularity::app.sif
================================================================================

ERROR: [pid 2788032] Worker Worker(salt=2417965045, workers=1, host=dgx1, username=alec.gunny, pid=2788032) failed    Greet(name=Thom)
Traceback (most recent call last):
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/luigi/worker.py", line 203, in run
    new_deps = self._run_get_new_deps()
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/luigi/worker.py", line 138, in _run_get_new_deps
    task_gen = self.task.run()
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/law/sandbox/base.py", line 350, in run
    raise Exception(
Exception: sandbox 'singularity::app.sif' failed with exit code 40, please see the error inside the sandboxed context above for details
DEBUG: 1 running tasks, waiting for next task to finish
INFO: Informed scheduler that task   Greet_Thom_af59ec2587   has status   FAILED
DEBUG: Asking scheduler for work...
DEBUG: Done
DEBUG: There are no more tasks to run at this time
DEBUG: There are 1 pending tasks possibly being run by other workers
DEBUG: There are 1 pending tasks unique to this worker
DEBUG: There are 1 pending tasks last scheduled by this worker
INFO: Worker Worker(salt=2417965045, workers=1, host=dgx1, username=alec.gunny, pid=2788032) was stopped. Shutting down Keep-Alive thread
INFO: 
===== Luigi Execution Summary =====

Scheduled 1 tasks of which:
* 1 failed:
    - 1 Greet(...)

This progress looks :( because there were failed tasks

===== Luigi Execution Summary =====

```

Evidently, the intended `PYTHONPATH` isn't getting set inside the container. What's the best way to ensure the container is using the appropriate Python interpreter with access to the correct libraries?

### Issue #2: Using a custom sandbox
Inside `law_repro.__init__`, you'll find a custom `DevSandbox` class that will map the host application code into the container at the install directory to allow for more rapid development. However, if we try to run a version of the same task that leverages this sandbox:

```console
law run law_repro.DevGreet --name Thom --local-scheduler
```

You should find that the following issue gets raised:

```console
DEBUG: Checking if DevGreet(name=Thom, dev=False) is complete
INFO: Informed scheduler that task   DevGreet_False_Thom_80b4044546   has status   PENDING
INFO: Done scheduling tasks
INFO: Running Worker with 1 processes
DEBUG: Asking scheduler for work...
DEBUG: Pending tasks: 1
INFO: [pid 2788817] Worker Worker(salt=3304246859, workers=1, host=dgx1, username=alec.gunny, pid=2788817) running   DevGreet(name=Thom, dev=False)
ERROR: [pid 2788817] Worker Worker(salt=3304246859, workers=1, host=dgx1, username=alec.gunny, pid=2788817) failed    DevGreet(name=Thom, dev=False)
Traceback (most recent call last):
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/luigi/worker.py", line 203, in run
    new_deps = self._run_get_new_deps()
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/luigi/worker.py", line 138, in _run_get_new_deps
    task_gen = self.task.run()
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/law/sandbox/base.py", line 344, in run
    cmd = self.sandbox_inst.cmd(self.create_proxy_cmd())
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/law/contrib/singularity/sandbox.py", line 173, in cmd
    env = self._get_env()
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/law/sandbox/base.py", line 241, in _get_env
    for name, value in cfg.items(section):
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/law/config.py", line 477, in items
    options = self.options(section, prefix=prefix, expand_vars=expand_vars,
  File "/home/alec.gunny/miniconda3/envs/law-repro-DBCx7gBt-py3.9/lib/python3.9/site-packages/law/config.py", line 452, in options
    for option in ConfigParser.options(self, section):
  File "/home/alec.gunny/miniconda3/lib/python3.9/configparser.py", line 675, in options
    raise NoSectionError(section) from None
configparser.NoSectionError: No section: 'singularity_dev_sandbox_env'
DEBUG: 1 running tasks, waiting for next task to finish
INFO: Informed scheduler that task   DevGreet_False_Thom_80b4044546   has status   FAILED
DEBUG: Asking scheduler for work...
DEBUG: Done
DEBUG: There are no more tasks to run at this time
DEBUG: There are 1 pending tasks possibly being run by other workers
DEBUG: There are 1 pending tasks unique to this worker
DEBUG: There are 1 pending tasks last scheduled by this worker
INFO: Worker Worker(salt=3304246859, workers=1, host=dgx1, username=alec.gunny, pid=2788817) was stopped. Shutting down Keep-Alive thread
INFO: 
===== Luigi Execution Summary =====

Scheduled 1 tasks of which:
* 1 failed:
    - 1 DevGreet(...)

This progress looks :( because there were failed tasks

===== Luigi Execution Summary =====

```

What's the best way to implement a custom sandbox and ensure that its config args (if there are any) get picked up by `law`'s global Config?
