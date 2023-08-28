# Note:
This project is forked from Dustin Maas's 
[powder project](https://gitlab.flux.utah.edu/powder-profiles/powder-control).
The scripts are modified to reflect a specific project run for my experiments 
and should be modified appropriately.

# About

This project shows how to instantiate and interact with a Powder experiment
programmatically via the Powder portal API. It includes some useful tools to
this effect, as well as example code showing how to use them. Finally, it
includes a Powder profile that will spin up an orchestration node with some
dependencies installed for exploring these tools.

In [powder/experiment.py](powder/experiment.py), there is a class
`PowderExperiment`, which serves as the main abstraction for starting,
interacting with, and terminating a single Powder experiment. It relies on
[powder/rpc.py](powder/rpc.py) for interacting with the Powder RPC server, and
[powder/ssh.py](powder/ssh.py) for interacting with the nodes in the experiment
after they've become ready.

In [project.py](project.py), you can see how one might use these tools to
leverage Powder resources in, e.g., a CI/CD pipeline. The script does the
following:

1. instantiates a Powder experiment based on an existing Powder profile;
2. setup/install dependencies on the experimental nodes;
5. runs the experiments/scripts (currently empty);
6. terminates the instance.

Logs are collected at each step and parsed in order to verify success/failure.

## Getting Started

In order to run [project.py](project.py) or otherwise use the tools in this
project, you'll need a Powder/Cloudlab account to which you've added your public `ssh`
key. If you haven't already done this, you can find instructions
[here](https://docs.powderwireless.net/users.html#%28part._ssh-access%29).
You'll also need to download your Powder/Cloudlab credentials. You'll find a button to do
so in the drop-down menu accessed by clicking on your username after logging
into the Powder/Cloudlab portal. This will download a file called `cloudlab.pem`, which
you will need later.

While [project.py](project.py) can be run on the orchestration node that the
included [profile](profile.py) provides, it can just as easily be run on any
machine that holds or forwards the `ssh` key associated with your Powder
account.

If you **are not** using the node provided by the included profile, you will
need to make sure the machine you are using has `python3` installed, as well as
the packages in [requirements.txt](requirements.txt). You can install the
packages by doing

```bash
pip install -r requirements.txt
```

If you **are** using the included profile, it includes a startup script that
installs these packages for you. However, you'll need to start `ssh-agent` on
the machine you're using to access the orchestration node, and enable agent
forwarding. This will allow the orchestration node to use your credentials to
log into the experimental nodes instantiated programmaticaly by
[project.py](project.py). There is a good `ssh-agent` tutorial
[here](https://www.ssh.com/ssh/agent).

Whatever machine you are using to run [project.py](project.py), it will need a
local copy of the `cloudlab.pem` file you downloaded earlier.

### Running the Example

The RPC client that `Experiment` relies on to interact with the Cloudlab RPC
server expects some environment variables to be set. If your private `ssh` key
is encrypted, the key password needs to be set in an environment variable as
well, unless you have already started `ssh-agent`.

If your ssh key is encrypted:

```bash
set +o history
USER=your_powder_username PWORD=your_powder_password \
CERT=/path/to/your/cloulab.pem KEYPWORD=your_ssh_key_password ./example.py <profile-to-instantiate>
```

If not:

```bash
set +o history
USER=your_powder_username PWORD=your_powder_password \
CERT=/path/to/your/cloulab.pem ./example.py <profile-to-instantiate>
```

The `set +o history` command will keep these passwords out of your `bash`
history (assuming you're using `bash`).

It can take more than 30 minutes for all of the steps in
[project.py](project.py) to complete, but you'll see intermittent messages on
`stdout` indicating progress and logging results. In some cases, the Powder
resources required by [project.py](project.py) might not be available. If so,
you'll see a log message that indicates as much and the script will exit; you
can look at the [Resource Availability](https://www.powderwireless.net/resinfo.php)
page on the Powder portal to see the status of the required nuc5300 nodes. After
completion, the script will exit with a message about failure/success.

# Sections to modify

You can hardcode the profile in [project.py](project.py) and reduce commandline arguments 
by modifying `__main__` where we instantiate `experiment`.
You need to change `_setup_nodes` function to point to appropriate setup scripts if there are any.
`string_cmd` gathers all the node's ssh info and updates the ~/.ssh/config with correct hostnames.
It relies on the fact that the existing config has appropriate number of host entries already existing 
in the format `cloudlab<i>` e.g. `cloudlab0` and `cloudlab1` if the experiment contains 2 nodes.
