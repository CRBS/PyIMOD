import subprocess

def get_mrc_header(file_mrc, str):
    cmd = "header -{0} {1}".format(str, file_mrc)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    output = proc.stdout.read()
    output = [float(x) for x in output.split()]
    return output
