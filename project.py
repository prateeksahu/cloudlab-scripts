#!/usr/bin/env python3
import logging
import mmap
import multiprocessing as mp
import powder.experiment as pexp
import random
import re
import string
import sys
import time
import subprocess

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


class SetupExperiment:
    """Instantiates a Powder experiment based on the Powder profile `PROFILE_NAME`
    and interacts with the nodes in the experiment in order to setup, build, and
    test an OAI RAN network in a controlled RF environment. Logs for each step
    are collected from the nodes and stored in this directory.

    """

    # Powder experiment credentials
    PROJECT_NAME = 'ACSES'
    PROFILE_NAME = 'sidecar-characterization'
    EXPERIMENT_NAME_PREFIX = 'SC-'

    TEST_SUCCEEDED   = 0  # all steps succeeded
    TEST_FAILED      = 1  # on of the steps failed
    TEST_NOT_STARTED = 2  # could not instantiate an experiment to run the test on

    def __init__(self, profile='sidecar-characterization', experiment_name=None):
        self.PROFILE_NAME = profile
        if experiment_name is not None:
            self.experiment_name = experiment_name
        else:
            self.experiment_name = self.EXPERIMENT_NAME_PREFIX + self._random_string()
    
    def log(self):
        print(self.PROFILE_NAME)

    def status(self):
        logging.info('Getting Powder experiment status')
        self.exp = pexp.PowderExperiment(experiment_name=self.experiment_name,
                                         project_name=self.PROJECT_NAME,
                                         profile_name=self.PROFILE_NAME)

        exp_status = self.exp._get_status().status
        if exp_status != self.exp.EXPERIMENT_READY:
            logging.error('Experiment is not ready yet.')
            return False
        else:
            self._setup_nodes()
            return True

    def run(self):
        if not self._start_powder_experiment():
            self._finish(self.TEST_NOT_STARTED)

        if not self._setup_nodes():
            self._finish(self.TEST_FAILED)

        if not self._run_test():
            self._finish(self.TEST_FAILED)

        else:
            sys.exit(self.TEST_SUCCEEDED)
            #self._finish(self.TEST_SUCCEEDED)

    def _random_string(self, strlen=7):
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(characters) for i in range(strlen))

    def _start_powder_experiment(self):
        logging.info('Instantiating Powder experiment...')
        self.exp = pexp.PowderExperiment(experiment_name=self.experiment_name,
                                         project_name=self.PROJECT_NAME,
                                         profile_name=self.PROFILE_NAME)

        exp_status = self.exp.start_and_wait()
        if exp_status != self.exp.EXPERIMENT_READY:
            logging.error('Failed to start experiment.')
            return False
        else:
            return True

    def _setup_nodes(self):
        # Run install scripts
        setup_valid = True
        # Copy ssh command
        if not setup_valid:
            logging.info('See logs')
            return False
        else:
            #print(self.exp.sshp.user)
            #print(self.exp.sshp.host)
            i = 0
            for key in self.exp.nodes.keys():
                node = self.exp.nodes[key]
                config = 'cloudlab'+str(i)
                #string_cmd = "sed -i -r '/HostName/s/(HostName ).*cloudlab.*/\\1"+node.sshp.host+"/g' ~/.ssh/config"
                string_cmd = "sed -i -r '/"+config+"/!b;n;c    HostName "+node.sshp.host+"' ~/.ssh/config"
                scp_cmd = "scp -o StrictHostKeyChecking=no cloudlab_scripts/ssh/* "+config+":~/.ssh/"
                #git_cmd = "ssh "+config+" 'cd /proj/acses-PG0/sidecar-characterization;git pull origin hotinfra'"
                setup_cmd = "ssh -o StrictHostKeyChecking=no "+config+" 'cd /proj/acses-PG0/sidecar-characterization;./setup_scripts/setup_node.sh'"
                subprocess.run(string_cmd, shell=True)
                subprocess.run(scp_cmd, shell=True)
                subprocess.run(setup_cmd, shell=True)
                i+=1
            return True

    def _run_test(self):
        # Run experiment
        return True

    def _finish(self, test_status):
        if self.exp.status not in [self.exp.EXPERIMENT_NULL, self.exp.EXPERIMENT_NOT_STARTED]:
            self.exp.terminate()

        if test_status == self.TEST_NOT_STARTED:
            logging.info('The experiment could not be started... maybe the resources were unavailable.')
        elif test_status == self.TEST_FAILED:
            logging.info('The test failed.')
        elif test_status == self.TEST_SUCCEEDED:
            logging.info('The test succeeded.')

        sys.exit(test_status)


if __name__ == '__main__':
    if len(sys.argv) > 3:
        print(sys.argv)
        exit()
    if len(sys.argv) > 2:
        experiment = SetupExperiment(profile=sys.argv[1], experiment_name=sys.argv[2])
        experiment.status()
    else:
        experiment = SetupExperiment(profile=sys.argv[1])
        experiment.run()

