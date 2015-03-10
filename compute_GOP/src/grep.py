import subprocess

def locate_file(filename, fileslist):
    # use grep
    p = subprocess.Popen(["grep", "-lr", filename, fileslist], stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output.replace("\n","")   