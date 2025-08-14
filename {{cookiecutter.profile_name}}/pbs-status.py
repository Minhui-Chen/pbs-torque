#!/usr/bin/env python3

import sys
import subprocess
import xml.etree.cElementTree as ET

jobid = sys.argv[1]

def is_xml(text):
    return text.lstrip().startswith("<?xml") or text.lstrip().startswith("<")

try:
    # Run qstat
    res = subprocess.run("qstat -f -x {}".format(jobid), check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    output = res.stdout.decode()

    if is_xml(output):
        # --- XML parsing ---
        xmldoc = ET.ElementTree(ET.fromstring(output)).getroot()
        job_state = xmldoc.findall('.//job_state')[0].text
    
        if job_state == "F":  # Light uses "F" instead of "C"
            exit_status = xmldoc.findall('.//exit_status')[0].text
            if exit_status == '0':
                print("success")
            else:
                print("failed")
        else:
            print("running")

    else:
        # --- Plain text parsing ---
        job_state = None
        exit_status = None
        for line in output.splitlines():
            if "job_state" in line:
                job_state = line.split('=')[-1].strip()
            elif "exit_status" in line  or "Exit_status" in line:
                exit_status = line.split('=')[-1].strip()

        if job_state == "F":  # Light uses "F" instead of "C"
            print("success" if exit_status == '0' else "failed")
        elif job_state:
            print("running")
        else:
            print("failed")  # Couldn't determine job state

except (subprocess.CalledProcessError, IndexError, KeyboardInterrupt) as e:
    print("failed")


