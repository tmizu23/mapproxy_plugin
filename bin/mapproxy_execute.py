# -*- coding: utf-8 -*-
import os, platform, subprocess
import ast

myos = platform.system()
mydir = os.path.dirname(os.path.abspath(__file__))


def run(projectdir):
    if myos == "Windows":
        cmd = "\"" + mydir + os.sep + "run.bat\" " + projectdir
    else:
        cmd = "bash " + mydir + os.sep + "run.sh " + projectdir
    p = subprocess.Popen(cmd, shell=True)
    return


def install():
    if myos == "Windows":
        cmd = "\"" + mydir + os.sep + "install.bat\""
    else:
        cmd = "bash " + mydir + os.sep + "install.sh"
    p = subprocess.call(cmd, shell=True)
    return p


def kill():
    if myos == "Windows":
        cmd = "\"" + mydir + os.sep + "kill.bat\""
    else:
        cmd = "kill `ps -ef|grep mapproxy_plugin/bin/mypython|awk '{print $2;}'`"
    p = subprocess.call(cmd, shell=True)
    return p


def layers(filename):
    if myos == "Windows":
        cmd = "\"" + mydir + os.sep + "layers.bat\" " + filename
    else:
        cmd = "bash " + mydir + os.sep + "layers.sh " + filename
    #print cmd
    out, err = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=True).communicate()
    return ast.literal_eval(out) #string to dict
