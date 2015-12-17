import subprocess

def get_obj_basic_metrics(file, N):
    cmd = "imodinfo -F -o {0} {1}".format(N, file)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    bb = []
    cent = []
    for line in proc.stdout:
        if "Number of Contours = " in line:
            ncont = int(line.split()[4])
        elif "Bounding Box" in line:
            line = line.split()
            bb.append(float(line[4][1:-1]))
            bb.append(float(line[5][0:-1]))
            bb.append(float(line[6][0:-2]))
            bb.append(float(line[7][1:-1]))
            bb.append(float(line[8][0:-1]))
            bb.append(float(line[9][0:-2]))
        elif "Center" in line:
            line = line.split()
            cent.append(float(line[2][1:-1]))
            cent.append(float(line[3][0:-1]))
            cent.append(float(line[4][0:-1]))
        elif "Volume Inside" in line:
            vol = float(line.split()[4])
        elif "Mesh Surface" in line:
            sa = float(line.split()[4])
    return ncont, vol, sa, cent, bb
