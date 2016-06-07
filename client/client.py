#!/usr/bin/python
#
#client.py
#client with which to send commands to server

#websocket (install websocket-client)
from websocket import create_connection
from Tkinter import *
#from nGCCeCommands import makeGui
import re, sys
import optparse, commands #parse command line options

################################################################################
# Parse Script Options and Arguments
################################################################################
parser = optparse.OptionParser("usage: %prog [options] <input file> \n")
parser.add_option("-v", "--verbosity",
                  dest="verbosity", type='int', default=1,  #Shaun changed this from 2 to 1 to keep things less verbose
                  help="amount of detail in output")
parser.add_option("-a", "--address",
                  dest="serverAddress", type="string",
                  default="pi5",
                  help ="address of server node")
options, args = parser.parse_args()
#if len(args) != 1:
#    print "Please specify input file. Exiting"
#    sys.exit()

#inputFileName = args[0]
VERBOSITY = options.verbosity
serverAddress = "ws://%s:1738/ws" % options.serverAddress
################################################################################


################################################################################
# Function definitions
################################################################################
def read_byte(address):
    message = send_message("SR "+hex(address))
    if VERBOSITY >= 1:
        print message
    match = re.search(r"OK\s+(\w+)",message,re.I|re.X)
    if match:
        return int(match.group(1),0)
    return None

def read_byte_s(address):
    ret = read_byte(address)
    if ret == None:
        return None
    return hex(ret)

def write_byte(address,value):
    message = send_message("SW "+hex(address)+" "+hex(value))
    if VERBOSITY >= 1:
        print message

def read_byte_data(address,register):
    message = send_message("CR "+hex(address)+" "+hex(register))
    if VERBOSITY >= 1:
        print message
    match = re.search(r"OK\s+(\w+)",message,re.I|re.X)
    if match:
        return int(match.group(1),0)
    return None

def read_byte_data_s(address,register):
    ret = read_byte_data(address,register)
    if ret == None:
        return None
    return hex(ret)

def write_byte_data(address,register,value):
    message = send_message("CW "+hex(address)+" "+hex(register)+" "+hex(value))
    if VERBOSITY >= 1:
        print message

def send_message(m):
    ws.send(m)
    if VERBOSITY >= 2:
        print "Sent '%s'" %m
    result = ws.recv()
    if VERBOSITY >= 2:
        print "Received '%s'" % result
    return(result)
################################################################################


################################################################################
# Function aliases for testers
################################################################################
def SR(address): return read_byte(address)
def SRs(address): return read_byte_s(address)
def SW(address, value): return write_byte(address, value)
def CR(address, register): return read_byte_data(address, register)
def CRs(address, register): return read_byte_data_s(address, register)
def CW(address, register, value): return write_byte_data(address,register,value)
################################################################################


################################################################################
# Run
################################################################################
ws = create_connection(serverAddress) #connect to pi server

#if __name__ == "__main__":
    #import tests
#    i = re.match('(.*)\.py', inputFileName)
#    if i:
#        inputFile = __import__(i.group(1))
#    else:
#        inputFile = __import__(inputFileName)

    #run tests
    #root = Tk()
    #myapp = makeGui(root)
    #root.mainloop()
    #inputFile.test()
    
################################################################################
