# uHTR.py

import Hardware as hw
from DChains import DChains
from DaisyChain import DaisyChain
from QIE import QIE
import iglooClass_adry as i
import os
import sys
import time
import numpy
import multiprocessing as mp
from subprocess import Popen, PIPE
from commands import getoutput
from ROOT import *
gROOT.SetBatch()


if __name__ == "__main__":

	from client import webBus
	from uHTR import *
	all_slots = [2,3,4,5,7,8,9,10,18,19,20,21,23,24,25,26]
	qcard_slots = all_slots
	b = webBus("pi5", 0)
	uhtr_slots = [1,2]
#	uhtr = uHTR(1, qcard_slots, b)
# #	uhtr.ped_test()
# 	for slot in qcard_slots:
# 		for chip in xrange(12):
# 			info=uhtr.get_QIE_map(slot, chip)
# 			print "Q_slot: {4}, Qie: {3}, uhtr_slot: {0}, link: {1}, channel: {2}".format(info[0],info[1],info[2],chip,slot)

	# for i, ave in enumerate(ped_arr):
	# 	print i-31, ave

	u = uHTR(uhtr_slots,qcard_slots, b)
	u.shunt_scan()


class uHTR():
	def __init__(self, uhtr_slots, qcard_slots, bus):

		self.crate=41			#Always 41 for summer 2016 QIE testing

		if isinstance(uhtr_slots, int): self.uhtr_slots=[uhtr_slots]
		else: self.uhtr_slots=uhtr_slots

		self.bus=bus

		self.qcards=qcard_slots

		self.master_dict={}
		### Each key of master_dict corresponds to a QIE chip
		### The name of each QIE is "(qcard_slot, chip)"
		### Each QIE chip returns a dictionary containing test results and its uHTR mapping
		### List of keys: "slot" "link" "channel" "ped_test"

		# setup functions
		clock_setup(self.crate, qcard_slots)
		for slot in self.uhtr_slots:
			init_links(self.crate, slot)
		self.QIE_mapping()


#############################################################
# uHTR tests
# Results of each test recorded in master_dict
#############################################################

	def ped_test(self):
		ped_results = {}
		ped_settings = list(i-31 for i in xrange(63))
		ped_results={}
		ped_results["settings"]=ped_settings
		for setting in ped_settings:
			for qslot in self.qcards:
				dc=hw.getDChains(qslot, self.bus)
				dc.read()
				for chip in xrange(12):
					dc[chip].PedestalDAC(setting)
				dc.write()
				dc.read()
			histo_results=self.get_histo_results(self.crate, self.uhtr_slots)
			for uhtr_slot, uhtr_slot_results in histo_results.iteritems():
				for chip, chip_results in uhtr_slot_results.iteritems():
					key="({0}, {1}, {2})".format(uhtr_slot, chip_results["link"], chip_results["channel"])
					ped_results[key].append(chip_results["PedBinMax"])

		for qslot in self.qcards:
			for chip in xrange(12):
				ped_key=str(self.get_QIE_map(qslot, chip))
				chip_arr=ped_results[ped_key]



	def charge_inject_test(self):
		ci_results = {} #ci=chargeinjection
		ci_settings = [90, 180, 360, 720, 1440, 2880, 5760, 8640] #in fC
		ci_results={}
		ci_results["settings"]=ci_settings
		for setting in ci_settings:
			for qslot in self.qcards:
				dc=hw.getDChains(qslot, self.bus)
				dc.read()
				for chip in xrange(12):
					dc[chip].ChargeInjectDAC(setting)
				dc.write()
				dc.read()
			histo_results=self.get_histo_results(self.crate, self.uhtr_slots)
			for uhtr_slot, uhtr_slot_results in histo_results.iteritems():
				for chip, chip_results in uhtr_slot_results.iteritems():
					key="({0}, {1}, {2})".format(uhtr_slot, chip_results["link"], chip_results["channel"])
					ci_results[key].append(chip_results["signalBinMax"])

		for qslot in self.qcards:
			for chip in xrange(12):
				ci_key=str(self.get_QIE_map(qslot, chip))
				chip_arr=ci_results[ci_key]



	''' set chargeinject to highest setting, adjust shunt with Gsel, assess gain ratio between peaks '''
	def shunt_scan(self):
		peak_results = {}
		default_peaks = [] #holds the CI values for 3.1 fC/LSB setting for chips
		ratio_pf = [0,0] #pass/fail for ratio within 10% of nominal
		default_peaks_AVG = 0
		#GSel table gain values (in fC/LSB)
		# gain_settings = [3.1, 4.65, 6.2, 9.3, 12.4, 15.5, 18.6, 21.7, 24.8]
		# gain_settings = [0,1,2,4,8,16,18,20,24]
		gain_settings = [0]
		#ratio between default 3.1fC/LSB and itself/other GSel gains
		nominalGainRatios = [1.0, .67, .5, .33, .25, .2, .17, .14, 0.02]
		for setting in gain_settings:
			print "\n\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
			print "&&&&&&&&&&&&&&&&&&&& S E T. = %d &&&&&&&&&&&&&&&&&&&&&&&&" %setting
			print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"

			for qslot in self.qcards:
				dc=hw.getDChains(qslot, self.bus)
				dc.read()
				hw.SetQInjMode(1, qslot, self.bus) #turn on CI mode (igloo function)
				i.displayCI(self.bus, qslot)
				for chip in xrange(12):
					dc[chip].PedestalDAC(31)
					dc[chip].ChargeInjectDAC(8640) #set max CI value
					dc[chip].Gsel(setting) #increase shunt/decrease gain
				dc.write()
				dc.read()

			histo_results=self.get_histo_results(self.crate, self.uhtr_slots, signalOn=True)

			for uhtr_slot, uhtr_slot_results in histo_results.iteritems():
				for chip, chip_results in uhtr_slot_results.iteritems():
					key="({0}, {1}, {2})".format(uhtr_slot, chip_results["link"], chip_results["channel"])
					if setting == 0: peak_results[key] = []
					peak_results[key].append(chip_results["signalBinMax"])
					if setting == 0 and chip_results['signalBinMax'] != 1:
						default_peaks.append(chip_results['signalBinMax'])

			print "\n\nPeak Results: ", peak_results,'\n\n\n\n\n'
			print "\n\n\n##########################################"
			print "##########################################\n"
			print "Default peaks: ", default_peaks

		total = 0
		for val in default_peaks:
			default_peaks_AVG += val
			total += 1
		default_peaks_AVG /= total


		# 	count = 0
		# 	for peak in peak_results:
		# 		ratio = float(peak_results[peak]) / default_peaks[count] #ratio between shunt-adjusted peak & default peak
		# 		print "Setting: ", setting, "     ", peak_results[peak], '/', default_peaks[count], ' = ', ratio
		# 		if (ratio < nominalGainRatios[count]*1.1 and ratio > nominalGainRatios[count]*0.9): #within 10% of nominal
		# 			ratio_pf[0]+=1
		# 		else: ratio_pf[1]+=1
		#
		# 		count += 1
		#
		# for qslot in self.qcards:
		# 	for chip in xrange(12):
		# 		peak_key=str(self.get_QIE_map(qslot, chip))
		# 		chip_arr=peak_results[peak_key]
		# 		ratio_pf = [0, 0]
		# 		for i in xrange(9):
		# 		if (ratio < nominalGainRatios[count]*1.1 and ratio > nominalGainRatios[count]*0.9): #within 10% of nominal
		# 			ratio_pf[0]+=1
		# 		else: ratio_pf[1]+=1
		#
		# self.get_QIE(qslot, chip)["shunt_scan"]=(ratio_pf[0], ratio_pf[1])
		# return "Pass/Fail:  (", ratio_pf[0], ", ", ratio_pf[1], ")"

#############################################################


#############################################################
# Adding and extracting data from the master_dict
#############################################################

	def get_QIE(self, qcard_slot, chip):
		### Returns the dictionary storing the test results of the specified QIE chip
		key="({0}, {1})".format(qcard_slot, chip)
		return self.master_dict[key]

	def get_QIE_results(self, qcard_slot, chip, test_key=""):
		### Returns the (pass, fail) tuple of specific test
		QIE=self.get_QIE(qcard_slot, chip)
		return QIE[test_key]

	def get_QIE_map(self, qcard_slot, chip):
		key="({0}, {1})".format(qcard_slot, chip)
                qie=self.master_dict[key]
		slot=qie["uhtr_slot"]
		link=qie["link"]
		channel=qie["channel"]
		return (slot, link, channel)

	def add_QIE(self, qcard_slot, chip, uhtr_slot, link, channel):
		QIE_info={}
		QIE_info["uhtr_slot"]=uhtr_slot
		QIE_info["link"]=link
		QIE_info["channel"]=channel
		key="({0}, {1})".format(qcard_slot, chip)
		self.master_dict[key]=QIE_info

#############################################################


#############################################################
# Mapping functions
#############################################################

	def QIE_mapping(self):
		# Records the uHTR slot, link, and channel of each QIE in master_dict
		for qslot in self.qcards:
			dc=hw.getDChains(qslot, self.bus)
			hw.SetQInjMode(0, qslot, self.bus)
			dc.read()
			for chip in [0,6]:
				for num in xrange(12):
					dc[num].PedestalDAC(-9)
					if num==chip:
						dc[num].PedestalDAC(31)
				dc.write()
				dc.read()
				info=self.get_mapping_histo()
				if info is not None:
					uhtr_slot=info[0]
					link=info[1]
					for i in xrange(6):
						self.add_QIE(qslot, chip+i, uhtr_slot, link, 5-i)
				else: print "mapping failed"
			for num in xrange(12):
				dc[num].PedestalDAC(-9)
				dc.write()
				dc.read()


	def get_mapping_histo(self):
		# matches histo to QIE chip for mapping
		map_results=self.get_histo_results(out_dir="map_test")
		for uhtr_slot, uhtr_slot_results in map_results.iteritems():
			for chip, chip_results in uhtr_slot_results.iteritems():
				if chip_results["pedBinMax"] > 15:
					return (int(uhtr_slot), chip_results["link"], chip_results["channel"])
		return None

#############################################################


#############################################################
# Generate and read histos
#############################################################

	def get_histo_results(self, crate=None, slots=None, n_orbits=1000, sepCapID=0, signalOn=0, out_dir="histotest"):
		# Runs uHTRtool.exe and returns layered ditctionary of results.
		if slots is None:
			slots=self.uhtr_slots
		if crate is None:
			crate=self.crate
		histo_results = {}
		path_to_root = generate_histos(crate, slots, n_orbits, sepCapID, out_dir=out_dir)
		for file in os.listdir(path_to_root):
			# Extract slot number from file name
			temp = file.split('_')
			temp = temp[-1].split('.root')
			slot_num = str(temp[0])

			histo_results[slot_num] = getHistoInfo(signal=signalOn, file_in=path_to_root+"/"+file)
#		os.removedirs(path_to_root)
		return histo_results


#############################################################


#############################################################
# uHTRtool functions
#############################################################

def generate_histos(crate, slots, n_orbits=5000, sepCapID=0, file_out_base="", out_dir="histotests"):
	#can only generate over a single crate
	if not file_out_base:
		file_out_base="uHTR_histotest"
	cwd=os.getcwd()
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	dir_path="{0}/{1}".format(cwd, out_dir)
	os.chdir(dir_path)

	for slot in slots:
		file_out=file_out_base+"_{0}_{1}.root".format(crate, slot)
		p = mp.Process(target=get_histo, args=(crate, slot, n_orbits, sepCapID, file_out,))
		p.start()

	while mp.active_children():
		time.sleep(0.1)

	os.chdir(cwd)
	return dir_path

def send_commands(crate=None, slot=None, cmds=''):
	# Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is the crate number, slot number, and a list of commands.
	raw = ""
	results = {}

	if isinstance(cmds, str):
		print 'WARNING (uhtr.send_commands): You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
		cmds = [cmds]

	uhtr_ip = "192.168.{0}.{1}".format(crate, slot*4)
	uhtr_cmd = "uHTRtool.exe {0}".format(uhtr_ip)
	# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	raw_output = Popen(['printf "{0}" | {1}'.format(' '.join(cmds), uhtr_cmd)], shell = True, stdout = PIPE, stderr = PIPE).communicate()
	raw += raw_output[0] + raw_output[1]
	results[uhtr_ip] = raw
	return results

def get_histo(crate, slot, n_orbits=5000, sepCapID=0, file_out=""):
        # Set up some variables:
        log = ""
        if not file_out:
                file_out = "histo_uhtr{0}.root".format(slot)
	        # Histogram:
        cmds = [
                '0',
                'link',
                'histo',
                'integrate',
                '{0}'.format(n_orbits),                # number of orbits to integrate over
                '{0}'.format(sepCapID),
                '{0}'.format(file_out),
		'0',
		'quit',
                'quit',
                'exit',
                '-1'
        ]
        result = send_commands(crate=crate, slot=slot, cmds=cmds)
        return result


def getHistoInfo(file_in="", sepCapID=False, signal=False, qieRange = 0):
	slot_result = {}
	f = TFile(file_in, "READ")
	if sepCapID:
		rangeADCoffset = qieRange*64.
		for i_link in range(24):
			for i_ch in range(6):
				histNum = 6*i_link + i_ch
				h = f.Get("h%d"%(histNum))
				chip_results = {}
				chip_results["link"] = i_link
				chip_results["channel"] = i_ch
				chip_results["binMax"] = []
				chip_results["RMS"] = []
				for i_capID in range(4):
					offset = 64*(i_capID)
					h.GetXaxis().SetRangeUser(offset, offset+63)
					chip_results["RMS"].append(max(h.GetRMS(), 0.01))

				slot_result[histNum] = chip_results

	else: #Josh
		if signal:
			for i_link in range(24):
				for i_ch in range(6):
					histNum = 6*i_link + i_ch
					h = f.Get("h%d"%(histNum))
					lastBin = h.GetSize() - 5
					chip_results = {}
					chip_results["link"] = i_link
					chip_results["channel"] = i_ch
					#Transition from pedestal to signal is consistently around 10
					h.GetXaxis().SetRangeUser(0,35)
					binMax = h.GetMaximumBin()
					chip_results["pedBinMax"] = h.GetMaximumBin()
					chip_results["pedRMS"] = h.GetRMS()
					h.GetXaxis().SetRangeUser(40,lastBin)
					binValue = 0
					binNum = 0
					for Bin in range(40, lastBin):
						if binValue <= h.GetBinContent(Bin):
							binValue = h.GetBinContent(Bin)
							binNum = Bin
						elif Bin > binNum + 10 and h.GetBinContent(Bin) != 0:
							binValue = h.GetBinContent(Bin)
							binNum = Bin
							h.GetXaxis().SetRangeUser(binNum-10,binNum+10)
					chip_results["signalBinMax"] = binNum
					chip_results["signalRMS"] = h.GetRMS()
					slot_result[histNum] = chip_results

		else:
			for i_link in range(24):
				for i_ch in range(6):
					histNum = 6*i_link + i_ch
					h = f.Get("h%d"%(histNum))
					chip_results = {}
					chip_results["link"] = i_link
					chip_results["channel"] = i_ch
					chip_results["pedBinMax"] = h.GetMaximumBin()
					chip_results["pedRMS"] = h.GetRMS()

					slot_result[histNum] = chip_results

	f.Close()
	return slot_result

#############################################################
#Initialization functions
#############################################################

def uHTRtool_source_test():
	        ### checks to see if the uHTRtool is sourced, and sources it if needed
		uhtr_cmd="uHTRtool.exe"
		error="sh: uHTRtool.exe: command not found"
		check=getoutput(uhtr_cmd)
		source_cmd=["source /home/daqowner/dist/etc/env.sh"]

		if check==error:
			print "WARNING, you need to run 'source ~daqowner/dist/etc/env.sh' before you can use uHTRtool.exe"


def clock_setup(crate, slots):
	cmds = [
		'0'
		'clock'
		'setup'
		'3'
		'quit'
		'exit'
		]
	for slot in slots:
		send_commands(crate=crate, slot=slot, cmds=cmds)


def init_links(crate, slot, attempts=0):
	if attempts == 10:
		print "Skipping initialization of links for crate %d, slot %d after 10 failed attempts!"%(crate,slot)
		return
	attempts += 1
	linkInfo = get_link_info(crate, slot)
	onLinks, goodLinks, badLinks = check_link_status(linkInfo)
	if onLinks == 0:
		print "All crate %d, slot %d links are OFF! NOT initializing that slot!"%(crate,slot)
		return
	if badLinks == 0:
		return
	medianOrbitDelay = int(median_orbit_delay(linkInfo))
	if badLinks > 0:
		initCMDS = ["0","link","init","1","%d"%(medianOrbitDelay),"0","0","0","quit","exit"]
		send_commands(crate=crate, slot=slot, cmds=initCMDS)
		init_links(crate, slot, attempts)


def get_BCN_status(uHTRPrintOut):
	for key, value in uHTRPrintOut.iteritems():
		linesList = value.split("\n")
		BCNs = []
		for j in range(len(linesList)):
			if len(linesList[j].split("Align BCN")) == 2:
				BCNLine = filter(None, linesList[j].split("Align BCN"))
				BCNList = filter(None, BCNLine[0].split(" "))
				BCNList = map(int, BCNList)
				BCNs = BCNs + BCNList
	return BCNs


def get_ON_links(uHTRPrintOut):
	for key, value in uHTRPrintOut.iteritems():
		linesList = value.split("\n")
		ONLinks = []
		for j in range(len(linesList)):
			if len(linesList[j].split("BadCounter")) == 2:
				ONLine = filter(None, linesList[j].split("BadCounter"))
				ONList = filter(None, ONLine[0].split(" "))
				ONLinks = ONLinks + ONList
	return ONLinks


def get_BPR_status(uHTRPrintOut):
	for key, value in uHTRPrintOut.iteritems():
		linesList = value.split("\n")
		BPRs = []
		for j in range(len(linesList)):
			if len(linesList[j].split("BPR Status")) == 2:
				BPRLine = filter(None, linesList[j].split("BPR Status"))
				BPRList = filter(None, BPRLine[0].split(" "))
				BPRs = BPRs + BPRList
	return BPRs


def get_AOD_status(uHTRPrintOut):
	for key, value in uHTRPrintOut.iteritems():
		linesList = value.split("\n")
		AODs = []
		for j in range(len(linesList)):
			if len(linesList[j].split("AOD Status")) == 2:
				AODLine = filter(None, linesList[j].split("AOD Status"))
				AODList = filter(None, AODLine[0].split(" "))
				AODs = AODs + AODList
	return AODs


def median_orbit_delay(linkInfo):
	BCNList = []
	for k in range(len(linkInfo["BCN Status"])):
		if linkInfo["ON Status"][k] == "ON":
			BCNList = BCNList + [linkInfo["BCN Status"][k]]
	BCNMedian = int(numpy.median(BCNList))
	return BCNMedian


def check_link_status(linkInfo):
	goodLinks = 0
	badLinks = 0
	onLinks = 0
	for l in range(len(linkInfo["BPR Status"])):
		if linkInfo["ON Status"][l] == "ON":
			onLinks += 1
		if linkInfo["BPR Status"][l] == "111" and linkInfo["AOD Status"][l] == "111" and linkInfo["ON Status"][l] == "ON":
			goodLinks += 1
		elif linkInfo["ON Status"][l] == "ON" and not (linkInfo["BPR Status"][l] == "111" and linkInfo["AOD Status"][l] == "111"):
			badLinks += 1
	return onLinks, goodLinks, badLinks


def get_link_info(crate, slot):
	linkInfo = {}
        statCMDs = ["0", "link", "status", "quit", "exit"]
        statsPrintOut = send_commands(crate=crate, slot=slot, cmds=statCMDs)
        linkInfo["BCN Status"] = get_BCN_status(statsPrintOut)
        linkInfo["BPR Status"] = get_BPR_status(statsPrintOut)
        linkInfo["AOD Status"] = get_AOD_status(statsPrintOut)
        linkInfo["ON Status"] = get_ON_links(statsPrintOut)
	return linkInfo

#############################################################
# Analyze test results
#############################################################

def analyze_results(x, y):
	if len(x) != len(y):
		print "Sets are of unequal length"
		return None
