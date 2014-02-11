#!/bin/env python
import sys
import os
import argparse
import subprocess
import numpy as np
import pickle
#from scipy.stats import logistic

logistic = lambda x: float(1) / (1 + np.exp(-float(x)))

np.set_printoptions(precision=5, suppress=True)

Xs = [0, 1, 3, 5, 10, 100]
num_power_bins = 1000

pickle_fname = "freqs.pickle"
if os.path.exists(pickle_fname):
    with open(pickle_fname, "r") as f:
        freqs = pickle.load(f)
else:
    freqs = {}
    for xindex, X in enumerate(Xs):
        print "#####################################################"
        print "Starting X =", X, "..."
        print "#####################################################"

        # Holds the fraction of players with a given record for each power bin.
        # Invariant: For all of the records with the same number of (wins+losses)
        # the sum of the numbers equals 1.  Likewise, the sum of of the terminal
        # records (X-3, 12-0, 12-1, 12-2) also equals 1.
        # Queried like freqs[num_wins, num_losses, power]
        freqs[X] = np.zeros(shape=(13,4,num_power_bins))


        freqs[X][0,0,:] = float(1)/num_power_bins

        for num_wins in range(12): # don't need to update if wins=12
            for num_losses in range(3): # done need to update if losses=3
                print num_wins, num_losses, "..."
                player_distribution = freqs[X][num_wins, num_losses, :]
                norm_player_distribution = player_distribution / sum(player_distribution)
                for power in range(num_power_bins):
                    freq_power = freqs[X][num_wins, num_losses, power]
                    total_prob_win = 0
                    for other_power in range(num_power_bins):
                        prob_win = logistic(X * (float(power-other_power)/num_power_bins))

                        total_prob_win += norm_player_distribution[other_power] * prob_win

                    freqs[X][num_wins+1, num_losses, power] += total_prob_win * freq_power
                    freqs[X][num_wins, num_losses+1, power] += (1-total_prob_win) * freq_power

    with open(pickle_fname, "w") as f:
        pickle.dump(freqs, f)


outputs = [open("out-%s.csv" % X, "w") for X in Xs]


for i,X in enumerate(Xs):
    outputs[i].write("Power difference,Probability strong player wins\n")
    for diff in [0.0, 0.01, 0.1, 0.25, 0.5, 0.75]:
        outputs[i].write("%s,%s\n" % (diff, logistic(X*diff)))
    outputs[i].write("\n\n")

final_records = [(0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,2),(12,1),(12,0)]

query_powers = [0.0, 0.25, 0.5, 0.75, 0.9, (1-1.0/num_power_bins)]
query_power_bins = [int(num_power_bins*power) for power in query_powers]
print query_power_bins
for i,X in enumerate(Xs):
    outputs[i].write("Probability of different final records given power\n")
    outputs[i].write("Record,%s\n" % ",".join(map(str, query_powers)))
    for wins,losses in final_records:
        outputs[i].write("\'%s-%s," % (wins,losses))

        for j,query_power in enumerate(query_power_bins):
            if j != 0: outputs[i].write(",")
            outputs[i].write(str(freqs[X][wins, losses, query_power]*num_power_bins))
        outputs[i].write("\n")
    outputs[i].write("\n\n")



query_powers = [0.0, 0.25, 0.5, 0.75, (1-1.0/num_power_bins)]
query_power_bins = [int(num_power_bins*power) for power in query_powers]
#query_powers = query_powers[-8:]
print "query_powers:", query_powers
for i,X in enumerate(Xs):
    outputs[i].write("Fraction of players at different power levels at each record\n")
    outputs[i].write("Record,%s\n" % ",".join(map(str, query_powers)))
    for num_wins in range(13):
        for num_losses in range(4):
            if ((num_wins == 12) and (num_losses == 3)): continue
            report_freqs = np.zeros(len(query_powers))
            for j, query_power in enumerate(query_power_bins):
                report_freqs[j] = freqs[X][num_wins, num_losses, query_power]
            outputs[i].write("\'%s-%s,%s\n" % (num_wins, num_losses, ",".join(map(str,list(report_freqs/sum(report_freqs))))))
    outputs[i].write("\n\n")


