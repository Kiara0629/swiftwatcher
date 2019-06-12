# Stdlib imports
import os
import csv

# Data structure handling
import numpy as np


def save_test_config(args, params):
    """Save the parameters chosen for the given test of the algorithm. Some
    parameters include commas, so files are delimited with semicolons."""
    load_directory = (args.video_dir + os.path.splitext(args.filename)[0])
    save_directory = load_directory + "/" + args.custom_dir
    if not os.path.isdir(save_directory):
        try:
            os.makedirs(save_directory)
        except OSError:
            print("[!] Creation of the directory {0} failed."
                  .format(save_directory))

    # Writing a summary of the parameters to a file
    with open(save_directory + "/parameters.csv", 'w') as csv_file:
        filewriter = csv.writer(csv_file, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(["PARAMETERS"])
        for key in params.keys():
            filewriter.writerow(["{}".format(key),
                                 "{}".format(params[key])])


def save_test_results(args, count_estimate):
    """Save the bird count estimations from image processing to csv files.

    Count labels:
        0, frame_number
        1, total_birds
        2, total_matches
        3, appeared_from_chimney
        4, appeared_from_edge
        5, appeared_ambiguous (could be removed, future-proofing for now)
        6, disappeared_to_chimney
        7, disappeared_to_edge
        8, disappeared_ambiguous (could be removed, future-proofing for now)
        9, outlier_behavior

    Estimate array contains a 10th catch-all count, "segmentation_error"."""

    # Create save directory if it does not already exist
    load_directory = (args.video_dir + os.path.splitext(args.filename)[0])
    save_directory = load_directory + "/" + args.custom_dir
    if not os.path.isdir(save_directory):
        try:
            os.makedirs(save_directory)
        except OSError:
            print("[!] Creation of the directory {0} failed."
                  .format(save_directory))

    print("[========================================================]")
    print("[*] Saving results of test to files.")

    # Comparing ground truth to estimated counts, frame by frame
    ground_truth = np.genfromtxt(load_directory + '/groundtruth.csv',
                                 delimiter=',').astype(dtype=int)
    num_counts = count_estimate.shape[0]
    results_full = np.hstack((ground_truth[0:num_counts, 0:10],
                              count_estimate[:, 0:10])).astype(np.int)

    # Using columns 1:10 so that the "frame number" column is excluded
    error_full = count_estimate[:, 1:10] - ground_truth[0:num_counts, 1:10]

    # Calculating when counts were overestimated
    error_over = np.copy(error_full)
    error_over[error_over < 0] = 0

    # Calculating when counts were underestimated
    error_under = np.copy(error_full)
    error_under[error_under > 0] = 0

    # Summarizing the performance of the algorithm across all frames
    results_summary = {
        "count_true": np.sum(ground_truth[0:num_counts, 1:10], axis=0),
        "count_estimated": np.sum(count_estimate[:, 1:10], axis=0),
        "error_net": np.sum(error_full, axis=0),
        "error_overestimate": np.sum(error_over, axis=0),
        "error_underestimate": np.sum(error_under, axis=0),
        "error_total": np.sum(abs(error_full), axis=0),
    }

    # Writing the full results to a file
    np.savetxt(save_directory + "/results_full.csv", results_full,
               delimiter=';')

    # Writing a summary of the results to a file
    with open(save_directory + "/results_summary.csv", 'w') as csv_file:
        filewriter = csv.writer(csv_file, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([" ", "SEGMNTS", "MATCHES",
                             "ENT_CHM", "ENT_FRM", "ENT_AMB",
                             "EXT_CHM", "EXT_FRM", "EXT_AMB", "OUTLIER"])
        for key in results_summary.keys():
            filewriter.writerow(["{}".format(key),
                                 "{}".format(results_summary[key][0]),
                                 "{}".format(results_summary[key][1]),
                                 "{}".format(results_summary[key][2]),
                                 "{}".format(results_summary[key][3]),
                                 "{}".format(results_summary[key][4]),
                                 "{}".format(results_summary[key][5]),
                                 "{}".format(results_summary[key][6]),
                                 "{}".format(results_summary[key][7]),
                                 "{}".format(results_summary[key][8])])

    print("[-] Results successfully saved to files.")


def plot_cumulative_comparison(sequence1=None, sequence2=None):
    """For a given pair of equal-length sequences, plot a comparison of the
    cumulative totals and save to an image. Used to compare running totals
    between bird count estimates and ground truth."""

    results_full = np.genfromtxt('videos/ch04_20170518205849/tests/'
                                 '0_initial-configuration/results_full.csv',
                                 delimiter=';').astype(dtype=int)
