import subprocess

def get_obj_advanced_metrics(file, N, **kwargs):
    # Get optional arguments
    csv = kwargs.get('csv')

    # Parse imodinfo output line-by-line and extract meaningful values
    point = []
    length = []
    area = []
    cmd = "imodinfo -o {0} {1}".format(N, file)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    for line in proc.stdout:
        if "CONTOUR" in line:
            line = line.split()
            point.append(int(line[2]))
            length.append(float(line[6][0:-1]))
            area.append(float(line[9]))

    # If output is desired in CSV form, convert integer/float lists to comma-
    # delimited strings
    if csv:
        point = ",".join([str(x) for x in point])
        length = ",".join([str(x) for x in length])
        area = ",".join([str(x) for x in area])

    return point, length, area
