import subprocess

def filter_by_ncontours(file, thresh):
    cmd = "imodinfo -a {0}".format(file)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    ncont = []
    keep = []
    C = 0
    for line in proc.stdout:
        if "object" in line:
            # Extract the number of contours from the relevant line
            line = line.split()
            ncont.append(int(line[2]))

            # If the number of contours is greater than the specified
            # threshold, then keep the object in the output
            if ncont[C] > thresh:
                keep.append(C + 1)

            # Increment the object counter
            C = C + 1 

    return keep
