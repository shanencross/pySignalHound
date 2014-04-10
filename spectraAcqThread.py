# -*- coding: UTF-8 -*-

# Wrapper for Test-Equipment-Plus's "SignalHound" series of USB spectrum analysers.
#
# Written By Connor Wolf <wolf@imaginaryindustries.com>
#

#  * ----------------------------------------------------------------------------
#  * "THE BEER-WARE LICENSE":
#  * Connor Wolf <wolf@imaginaryindustries.com> wrote this file. As long as you retain
#  * this notice you can do whatever you want with this stuff. If we meet some day,
#  * and you think this stuff is worth it, you can buy me a beer in return.
#  * (Only I don't drink, so a soda will do). Connor
#  * Also, support the Signal-Hound devs. Their hardware is pretty damn awesome.
#  * ----------------------------------------------------------------------------
#


import logSetup
import logging
import time
import traceback


H_FLIP_FREQ            = 1.420405751786e9

# I'm worried about possible IF frequencies creeping into the data, so I'm adding a 2.5 Mhz shift to
# prevent the signal of interest (h-flip band) from being exactly centered in the acquired data.
# I suspect the IF runs at the center frequency, and is sensitive to +-10 Mhz around the center.
# Therefore, I can see some of the IF center-frequency creeping into the actual data.
ACQ_FREQ               = H_FLIP_FREQ + 2.5e6
ACQ_SPAN               = 20e6

ACQ_REF_LEVEL_DB       = -50
ACQ_ATTENUATION_DB     = 0
ACQ_GAIN_SETTING       = 3

ACQ_RBW                = 2.465e3
ACQ_VBW                = ACQ_RBW

ACQ_SWEEP_TIME_SECONDS = 0.010

ACQ_WINDOW_TYPE        = "hamming"
ACQ_UNITS              = "power"

PRINT_LOOP_CNT = 100
CAL_CHK_LOOP_CNT = 1000

def startAcquisition(sh, dataQueue):

	sh.configureAcquisition("average", "log-scale")
	sh.configureCenterSpan(center = ACQ_FREQ, span = ACQ_SPAN)
	sh.configureLevel(ref = ACQ_REF_LEVEL_DB, atten = ACQ_ATTENUATION_DB)
	sh.configureGain(gain = ACQ_GAIN_SETTING)
	sh.configureSweepCoupling(rbw = ACQ_RBW, vbw = ACQ_VBW, sweepTime = ACQ_SWEEP_TIME_SECONDS, rbwType = "native", rejection = "no-spur-reject")
	sh.configureWindow(window = ACQ_WINDOW_TYPE)
	sh.configureProcUnits(units = ACQ_UNITS)
	sh.configureTrigger(trigType = "none", edge = "rising-edge", level = 0, timeout = 5)
	# sh.configureIO("dc", "int-ref-out", "out-logic-low")
	# sh.configureDemod("fm", 102.3e6, 250e3, 12e3, 20, 50)

	# sh.configureRawSweep(100, 8, 2)
	sh.initiate(mode = "real-time", flag = "ignored")

	dataQueue.put({"settings" : sh.getCurrentAcquisitionSettings()})

def sweepSource(dataQueue, ctrlNs, printQueue):


	from SignalHound import SignalHound

	logSetup.initLogging(printQ = printQueue)
	loop_timer = time.time()
	print "Starting sweep-logger!"
	log = logging.getLogger("Main.AcqProcess")

	loop_timer = time.time()
	loops = 0

	sh = SignalHound()
	startAcquisition(sh, dataQueue)


	temperature = sh.queryDeviceDiagnostics()["temperature"]

	while 1:
		try:
			dataQueue.put(sh.fetchTrace())
		except IOError:

			log.error("IOError in Acquisition Thread!")
			log.error(traceback.format_exc())

		if loops % PRINT_LOOP_CNT == 0:
			now = time.time()
			delta = now-loop_timer
			freq = 1 / (delta / PRINT_LOOP_CNT)
			log.info("Elapsed Time = %0.5f, Frequency = %s", delta, freq)
			loop_timer = now

		if loops % CAL_CHK_LOOP_CNT == 0:
			temptmp = sh.queryDeviceDiagnostics()["temperature"]
			if abs(temperature - temptmp) > 2.0:    # Temperature deviations of > 2° cause IF shifts. Therefore, we do a re-cal if they're detected
				dataQueue.put({"status" : "Recalibrating IF"})
				sh.selfCal()
				startAcquisition(sh, dataQueue)

		loops += 1

		if ctrlNs.run == False:
			log.info("Stopping Sweep-thread!")
			break


	sh.abort()
	sh.closeDevice()

	del(sh)

	ctrlNs.acqRunning = False

	while not dataQueue.empty():
		dataQueue.get()

	log.info("Sweep-thread exiting!")
	dataQueue.close()
	dataQueue.join_thread()