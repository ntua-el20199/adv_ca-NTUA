import os
import numpy as np
import matplotlib.pyplot as plt
import re
import argparse
import sys

def extract_predictor_stats(filepath):
    """Extracts predictor stats (accuracy) from a single file."""
    stats = {}
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                # Look for lines with Nbit predictor data
                if line.startswith('Nbit-'):
                    try:
                        parts = line.split(':')
                        if len(parts) != 2:
                            print(f"Warning: Skipping malformed line {i+1} in {os.path.basename(filepath)}: {line}", file=sys.stderr)
                            continue
                        predictor_name = parts[0].strip()
                        values = parts[1].strip().split()
                        if len(values) != 2:
                            print(f"Warning: Skipping malformed values on line {i+1} in {os.path.basename(filepath)}: {line}", file=sys.stderr)
                            continue

                        correct = int(values[0])
                        incorrect = int(values[1])
                        total = correct + incorrect

                        if total == 0:
                            # Assign 0 accuracy if total is 0, or decide how to handle (e.g., skip)
                            accuracy = 0.0
                            print(f"Warning: Zero total branches for {predictor_name} in {os.path.basename(filepath)}. Accuracy set to 0.", file=sys.stderr)
                        else:
                            accuracy = correct / total

                        # Ensure accuracy is valid before storing
                        if not (0.0 <= accuracy <= 1.0):
                             print(f"Warning: Calculated accuracy {accuracy:.4f} for {predictor_name} in {os.path.basename(filepath)} is outside [0, 1]. Skipping this entry.", file=sys.stderr)
                             continue

                        stats[predictor_name] = accuracy
                    except ValueError:
                        print(f"Warning: Skipping line {i+1} in {os.path.basename(filepath)} due to non-integer values: {line}", file=sys.stderr)
                    except IndexError:
                         print(f"Warning: Skipping line {i+1} in {os.path.basename(filepath)} due to unexpected format: {line}", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return None # Indicate error
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        return None # Indicate error

    if not stats:
        print(f"Warning: No valid 'Nbit-' predictor data found in {os.path.basename(filepath)}", file=sys.stderr)

    return stats

def calculate_geometric_mean(accuracies):
    """Calculates the geometric mean, handling potential log(0)."""
    # Filter out accuracies <= 0 before taking log
    valid_accuracies = [acc for acc in accuracies if acc > 0]
    if not valid_accuracies:
        # Return 0 or np.nan if no valid accuracies > 0 exist
        return 0.0
    log_accuracies = np.log(valid_accuracies)
    return np.exp(np.mean(log_accuracies))


def main(target_directory):
    """Main function to process files and plot results."""
    try:
        # List files in the target directory
        all_files = os.listdir(target_directory)
        # Filter for .out files
        out_files = [f for f in all_files if f.endswith('.out')]
        # Create full paths
        filepaths = [os.path.join(target_directory, f) for f in out_files]

        if not filepaths:
            print(f"Error: No '.out' files found in directory: {target_directory}", file=sys.stderr)
            sys.exit(1)
        print(f"Found {len(filepaths)} '.out' files in '{target_directory}'.")

    except FileNotFoundError:
         print(f"Error: Directory not found: {target_directory}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
         print(f"Error accessing directory {target_directory}: {e}", file=sys.stderr)
         sys.exit(1)

    # Dictionary to store all accuracies for each predictor
    # Key: predictor_name, Value: list of accuracies from different files
    predictor_accuracies = {}

    # Process each file
    processed_files_count = 0
    for filepath in filepaths:
        print(f"Processing {os.path.basename(filepath)}...")
        stats = extract_predictor_stats(filepath)

        # If stats extraction failed or returned no data, skip to next file
        if stats is None or not stats:
            continue

        processed_files_count += 1
        for predictor, accuracy in stats.items():
            if predictor not in predictor_accuracies:
                predictor_accuracies[predictor] = []
            predictor_accuracies[predictor].append(accuracy)

    if processed_files_count == 0:
        print("Error: No files were processed successfully or contained valid data.", file=sys.stderr)
        sys.exit(1)

    if not predictor_accuracies:
        print("Error: No predictor data found across all processed files.", file=sys.stderr)
        sys.exit(1)

    # Calculate geometric means
    geometric_means = {}
    skipped_predictors = []
    for predictor, accuracies in predictor_accuracies.items():
        if not accuracies:
             print(f"Warning: No accuracy values collected for predictor {predictor}. Skipping.", file=sys.stderr)
             skipped_predictors.append(predictor)
             continue
        mean_val = calculate_geometric_mean(accuracies)
        geometric_means[predictor] = mean_val
        # Report if some accuracies were zero (and thus ignored in geom mean)
        num_zeros = accuracies.count(0.0)
        num_valid_positive = len([acc for acc in accuracies if acc > 0])
        if num_zeros > 0:
            print(f"Info: Predictor {predictor} had {num_zeros} zero-accuracy entries (ignored in geometric mean calculation). Used {num_valid_positive} positive entries.")
        elif num_valid_positive == 0:
             print(f"Warning: Predictor {predictor} had no positive accuracy values. Geometric mean set to 0.", file=sys.stderr)
             skipped_predictors.append(predictor) # Treat as skipped if mean is 0 due to no positive data


    # Filter out predictors that were skipped or resulted in 0 mean due to no positive data
    plot_predictors = {p: m for p, m in geometric_means.items() if p not in skipped_predictors}

    if not plot_predictors:
        print("Error: Could not calculate a valid geometric mean for any predictor.", file=sys.stderr)
        sys.exit(1)

    # Sort predictors for consistent plotting order
    sorted_predictors = sorted(plot_predictors.keys())
    sorted_means = [plot_predictors[p] for p in sorted_predictors]

    # --- Plotting ---
    try:
        plt.figure(figsize=(12, 8)) # Slightly larger figure for better spacing
        bars = plt.bar(sorted_predictors, sorted_means)

        # Increase font sizes
        title_fontsize = 16
        label_fontsize = 14
        tick_fontsize = 12
        bar_label_fontsize = 10

        plt.title('Geometric Mean of Branch Predictor Accuracies', fontsize=title_fontsize)
        plt.xlabel('Predictor Type', fontsize=label_fontsize)
        plt.ylabel('Geometric Mean Accuracy', fontsize=label_fontsize)
        plt.xticks(rotation=45, ha='right', fontsize=tick_fontsize) # Adjust rotation for better label visibility
        plt.yticks(fontsize=tick_fontsize) # Adjust y-tick font size
        plt.ylim(bottom=0) # Start y-axis at 0
        plt.grid(True, axis='y', linestyle='--', alpha=0.6)

        # Add value labels on top of bars
        plt.bar_label(bars, fmt='%.4f', padding=3, fontsize=bar_label_fontsize)

        # Print results to console
        print("\nGeometric Means of Predictor Accuracies:")
        for predictor in sorted_predictors:
            print(f"  {predictor}: {plot_predictors[predictor]:.4f}")

        plt.tight_layout() # Adjust plot to prevent labels overlapping
        output_filename = 'predictor_geometric_means.png'
        plt.savefig(output_filename)
        print(f"\nPlot saved successfully as '{output_filename}'")
        # plt.show() # Uncomment this line if you want the plot to display interactively

    except Exception as e:
        print(f"Error during plotting or saving figure: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Calculate and plot geometric mean of branch predictor accuracies from .out files.")
    # Optional argument for directory, defaults to current directory '.'
    parser.add_argument('directory', nargs='?', default='.',
                        help="Directory containing the .out files (default: current directory)")
    args = parser.parse_args()

    # Pass the specified or default directory to main
    main(args.directory)