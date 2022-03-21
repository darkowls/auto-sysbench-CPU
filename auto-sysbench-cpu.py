#!/bin/python3
import subprocess							# For launching Sysbench
import multiprocessing							# Solely for detecting number of threads
import statistics							# Solely for mean,median and stdev (Python 3 only)
import csv								# For exporting results to CSV file for Excel etc processing
from datetime import datetime						# for CSV unique naming

# Test settings
iterations = 7								# For detecting median value - it can be more, but odd number if preferred
max_prime = 20000							# Max prime number to detect. 20000 seams hard enough

eventspersec=[]								# list for storing Events Per Second for 5 iterations in one threads run
iter_latmin=[]								# list for storing minimum latency per run
iter_latavg=[]								# list for storing average latency per run
iter_latmax=[]								# list for maximum latency per run
iter_latper=[]								# list for percentile per run

medianEPS=[]								# storing median value from several iterations for specific threads run
averageEPS=[]								# storing average value from several iterations for specific threads run 
stdevEPS=[]								# storing standard deviation for specific threads run
minEPS=[]								# Storing absolute minimum EPS for specific threads run
maxEPS=[]								# Storing absolute maximunm EPS for specific threads run
latmin=[]								# Storing minimum latency for specific threads run
latavg=[]								# Storing average latency for specific threads run
latmax=[]								# Storing maximum latency for specific threads run
latper=[]								# Storing latency for 95% percentile for specific threads run

csvname=""								# CSV filename

# Detecting CPU threads
detected_threads=multiprocessing.cpu_count()
#max_threads=int(round(float(detected_threads)*1.1/8))*8
max_threads=round(detected_threads*1.2/8)*8				# Adding aproxumately 20 % of threads (incremented by 8) for testing
#max_threads=1								# TEMP speeding up for debugging
print ("Detected "+str(detected_threads)+" threads")
print ("Testing with maximum "+str(max_threads)+" threads")
# Running tests in 2 loops
for i in range(1, max_threads + 1):					# Going from 1 thread to max CPU threads
	print("Testing CPU with "+str(i)+" threads:",end="",flush=True)
	for iter in range(iterations):
		print("*",end="",flush=True)
		bashCommand = "sysbench cpu --cpu-max-prime=" + str(max_prime) + " --threads=" + str(i) + " run"
		sysbench_output=subprocess.run([bashCommand],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
		if sysbench_output.returncode==0:			# If command completed successfully
			indbeg = sysbench_output.stdout.find("second:")+7
			indend = sysbench_output.stdout.find("\n", indbeg)
			eventspersec.append(float(sysbench_output.stdout[indbeg:indend]))
			latminbeg = sysbench_output.stdout.find("min:")+4
			latminend = sysbench_output.stdout.find("\n",latminbeg)
			iter_latmin.append(float(sysbench_output.stdout[latminbeg:latminend]))
			latavgbeg = sysbench_output.stdout.find("avg:")+4
			latavgend = sysbench_output.stdout.find("\n",latavgbeg)
			iter_latavg.append(float(sysbench_output.stdout[latavgbeg:latavgend]))
			latmaxbeg = sysbench_output.stdout.find("max:")+4
			latmaxend = sysbench_output.stdout.find("\n", latmaxbeg)
			iter_latmax.append(float(sysbench_output.stdout[latmaxbeg:latmaxend]))
			latperbeg = sysbench_output.stdout.find("percentile:")+12
			latperend = sysbench_output.stdout.find("\n", latperbeg)
			iter_latper.append(float(sysbench_output.stdout[latperbeg:latperend]))
		else:							# if Sysbench failed
			print("Error occured"+sysbench_output.stderr)
			exit
	medianEPS.append(statistics.median(eventspersec))		# Calculating and storing median value
	averageEPS.append(statistics.mean(eventspersec))		# Calculating and storing average value
	stdevEPS.append(statistics.stdev(eventspersec))			# Calculating and storing standard deviation
	minEPS.append(min(eventspersec))				# Calculating and storing minimum EPS value
	maxEPS.append(max(eventspersec))				# Calculating and storing maximum EPS value
	latmin.append(min(iter_latmin))					# Calculating and storing minimum latency value
	latavg.append(statistics.mean(iter_latmin))                     # Calculating and storing average latency value
	latmax.append(max(iter_latmax))                                 # Calculating and storing maximum latency value
	latper.append(statistics.mean(iter_latper))                     # Calculating and storing average latency percentile value
	eventspersec.clear()						# We need to clear it all for the next threads run
	iter_latmin.clear()
	iter_latavg.clear()
	iter_latmax.clear()
	iter_latper.clear()
	print("  DONE; median="+str(round(medianEPS[i-1],2))+";mean="+str(round(averageEPS[i-1],2))+";stdev="+str(round(stdevEPS[i-1],2))+";min="+str(minEPS[i-1])+";max="+str(maxEPS[i-1]))
# Exporting results to CSV file
dateTimeObj=datetime.now()						# Getting current date and time
dateTimeStr=dateTimeObj.strftime("%Y%m%d_%H%M%S")			# Formatting date to simplify naming
csvname="cpu_"+dateTimeStr+".csv"					# defining name for CSV file
print(csvname)
with open(csvname,"w",newline="") as csvfile:
	writer=csv.writer(csvfile)
	writer.writerow(["threads","median","mean","stdev","min","max","latmin","latavg","latmax","latper95"])
	for i in range(1, max_threads + 1):
		writer.writerow([str(i),medianEPS[i-1],averageEPS[i-1],stdevEPS[i-1],minEPS[i-1],maxEPS[i-1],latmin[i-1],latavg[i-1],latmax[i-1],latper[i-1]])
