import os
import subprocess

def extract_objects(file_in, file_out, obj_list):
    nkeep = len(obj_list)
    max_line_length = os.sysconf(os.sysconf_names['SC_ARG_MAX'])

    cmd_frame = "imodextract {0} {1}".format(file_in, file_out)
    cmd_arg = ",".join([str(x) for x in obj_list])

    nchar = len(cmd_frame) + len(cmd_arg)

    if nchar < max_line_length:
        cmd = "imodextract {0} {1} {2}".format(cmd_arg, file_in, file_out)
        subprocess.call(cmd.split())

