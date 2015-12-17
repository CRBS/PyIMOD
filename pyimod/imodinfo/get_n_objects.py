import subprocess

def get_n_objects(file):
    cmd = "imodinfo -a {0}".format(file)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    for line in proc.stdout:
        line = line.split()
        if len(line) and "imod" in line[0]:
            nobj = line[1]
            break
    return nobj
