# Allan_Variance_Plotter
# Last updated: 5-6-2014
# Author: Shanen Cross
# Purpose: Plot the Allan Variance (rms^2 vs. index number (time block size)) for a 
# set of amplitudes for each frequency in a list of frequencies.

# Currently, 2D array of data is generated randomly for testing.

# MAY NOT BE WORKING PROPERLY CURRENTLY. Resulting plot does not display expected behavior.

# What this does do:
# 	1. At a particular frequency, takes the rms^2 of a list of numbers (amplitudes) and store in a list.
#   2. Averages adjacent pairs of amplitudes in the amplitude list, append their average to the new list along the way.
#		-If there is a lone amplitude left over, store that as an average.
#   3. Takes rms^2 of new list and appends to list of rms^2 values.
#   4. Averages adjacent triplets of amplitudes in the original amplitude list, storing the averages in a new list along the way.
# 	  -If there are less than three amplitudes left over, append their average to the new list.
#   5. Takes rms^2 of new list and appends to list of rms^2 values.
#   6. Repeats 4-5, except averages quadruplets, then pintuplets, etc., appending the rms^2 values along the way, until averaging
#      the entire list (and appending its rms^2).
#   7. Graph rms^2 list (vertical axis) against index number (horizontal axis) starting at 1,
#      which is

from __future__ import division # import floating point division, suggested by:
                               #http://labs.physics.dur.ac.uk/computing/docs/PythonRefresher.pdf
import numpy as np # Ya gotta have numpy
import matplotlib.pyplot as pyplot # And this if you are going to plot anything
import random # for randomized data generation

#get THE SQUARE OF the rms of a list of numbers
def get_rms_squared(numbers):
	result = 0
	for num in numbers:
		result += (num*num)
		#print result
	result =(result/len(numbers))
	return result
		
# Appears to function, but messy and has terribly wordy variable names.
# Replace Python lists with Numpy arrays?
def main():
	data = []
	number_of_freqs = 1
	number_of_amps_per_freq = 8
	
	for i in xrange(number_of_freqs):
		data.append([])
		for j in xrange(number_of_amps_per_freq):
			random.seed()
			random_number = random.uniform(1,100)
			data[i].append(random_number)
	
	list_of_rms_squared_lists = []
	for freq_index in range(number_of_freqs):
		amps = data[freq_index]
		rms_squared_list = [get_rms_squared(amps)]
		print "Initial amps list:", amps
		print "Initial Sigma^2 List:", rms_squared_list
		
		for divisor in range(2, number_of_amps_per_freq+1):
			averaged_amps = []
			
			for i in xrange(0, number_of_amps_per_freq+1-divisor,divisor):
				averaged_amp = np.average(amps[i:i+divisor])
				averaged_amps.append(averaged_amp)
				print "Starting index:", i
				print "Ending index:", i+divisor, "(up to but not including)"
				print str(divisor)+"-block averaged amps list addition:", averaged_amp
			if ((number_of_amps_per_freq % divisor) != 0): # Include average of remaining elements of divisor does not divide evenly into number of amps
				averaged_amp = np.average(amps[i+divisor:])
				averaged_amps.append(averaged_amp)
				print "Starting index:", i+divisor
				print "Ending index:", number_of_amps_per_freq, "(up to but not including)"
				print str(divisor)+"-block averaged amps list addition:", averaged_amp
			print "averaged amps list:", averaged_amps
			print "---------------------------------------------"
			rms_squared_list.append(get_rms_squared(averaged_amps))
			#print "Updated Sigma^2 List:", rms_squared_list
			print "________________________________________________"
		print "Sigma^2 length:", len(rms_squared_list)
		print "Sigma^2 list:", rms_squared_list
		
		index_list = range(1, number_of_amps_per_freq+1)
		#print index_list
		pyplot.plot(index_list, rms_squared_list)
		pyplot.show()
		
		list_of_rms_squared_lists.append(rms_squared_list)
			
main()
