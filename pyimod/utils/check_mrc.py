import subprocess

def check_mrc(file):
    cmd = "header {0}".format(file)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    streamdata = proc.communicate()[0]
    exit_code = proc.returncode
    return exit_code
