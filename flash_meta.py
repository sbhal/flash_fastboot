
#*****************************************************************************/
#
# Fastboot Flash Utility
#
# Version information
# $Header: //source/qcom/qct/tools/meta/main/latest/common/build/fastboot_complete.py#2 $
# $DateTime: 2014/06/28 19:15:13 $
# $Author: Siddharth Bhal (sbhal@qti.qualcomm.com)
#*****************************************************************************

'''fastboot_complete.py:

Description:

flash_meta.py is a layer above flastboot_complete.py which flashes all the binaries that are required for for an android Boot up.

Usage:

      python fastboot_complete.py [--meta=meta_path] [--dest=dest_path]

      meta_path:

         An compulsory parameter to the root of the meta build.
            
      dest_path:

         An optional parameter indicating the path where success/failure .txt of fastboot would be created
'''


#---------------------------------------------------------#
# Import libraries                                        #
#---------------------------------------------------------#

import sys
import os
import subprocess
import time
import signal
from optparse import OptionParser
from glob import glob
from subprocess import call

#---------------------------------------------------------#
# Define a handler to exit when Ctrl+C is pressed         #
#---------------------------------------------------------#
def interrupt_handler(signum, frame):
   sys.exit("Exiting")

parser = OptionParser()
parser.add_option("--meta","-m",action="store", type="string",dest="meta_path",help="META PATH")
parser.add_option("--dest","-d",action="store", type="string",dest="dest_path",help="DEST PATH")
(options, args) = parser.parse_args()


#---------------------------------------------------------#
# Print some diagnostic info                              #
#---------------------------------------------------------#
print "Platform is:", sys.platform
print "Python Version is:", sys.version
print "Current directory is:", os.getcwd()


if options.meta_path or options.dest_path:
   print "New path Specified."
   if options.meta_path:
      meta_path = options.meta_path
  
   if options.dest_path:
      dest_path = options.dest_path
   else:
      dest_path = os.path.dirname(os.path.abspath(__file__))
elif len(sys.argv) >= 2 :
      meta_path = sys.argv[1]
elif len(sys.argv) >= 3 :
      dest_path = sys.argv[2]
else:
      dest_path = os.path.dirname(os.path.abspath(__file__))
      meta_path = raw_input('Enter Meta path ')

#---------------------------------------------------------#
# Load the Meta-Info file                                 #
#---------------------------------------------------------#
lib_path = os.path.join(meta_path, 'common/tools/meta')
sys.path.insert(1, lib_path)
import meta_lib as ml
print "flash_meta.py: Loading Meta-Info file from Meta location"
mi = ml.meta_info()

#---------------------------------------------------------#
# Find Apps build.  							          #
#---------------------------------------------------------#
print "flash_meta.py: Finding Apps paths"
apps_path = mi.get_build_path('apps')

la_path = os.path.join(apps_path, 'LINUX/android')
if os.path.exists(la_path):
   apps_path = la_path
la_path = os.path.join(apps_path,'out/target/product/msm8974')
if os.path.exists(la_path):
   apps_path = la_path

#---------------------------------------------------------#
# Mkdir and Copy    							          #
#---------------------------------------------------------#
if not os.path.exists(dest_path + "\\apps"):
    os.makedirs(dest_path + "\\apps")

subprocess.call("Robocopy " + str(apps_path) + " " + str(dest_path)+"\\apps" + " boot.img emmc_appsboot.mbn userdata.img persist.img system.img cache.img recovery.img", shell=True)

subprocess.call("net use g: " + str(meta_path), shell=True)

os.chdir("g:\\common\\build")

sys.path.insert(1, "g:\\common\\build")
subprocess.call("Robocopy " + str(os.getcwd()) + " " + str(dest_path)+"\\apps" + " Ver_Info.txt", shell=True)
subprocess.call("adb reboot bootloader", shell=True)
subprocess.call("python fastboot_complete.py --ap=" + str(dest_path) + "\\apps", shell=True)
subprocess.call("fastboot reboot", shell=True)

subprocess.call("net use g: /Delete /Y", shell=True)

print "flash_meta.py: Flashing complete,Window will be closed in 1 minute"
print "Hit Ctrl+C to exit"
time.sleep(60)
