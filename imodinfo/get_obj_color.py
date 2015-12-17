import subprocess

def get_obj_color(file, N):
    cmd = "imodinfo -F -o {0} {1}".format(N, file)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    for line in proc.stdout:
        if "Color" in line:
            line = line.split()
            color = "{0},{1},{2}".format( 
                line[7][1:-1],
                line[8][0:-1],
                line[9][0:-1])
            break
    return color 
