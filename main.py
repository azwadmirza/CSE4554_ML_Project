import mccabe
import csv
import os
output_file = 'mccabe_complexity.csv'
cyclomatic_complexity_data = []
for root, _, files in os.walk('./source_files'):
    for file in files:
        if file.endswith('.py'):
            # Calculate cyclomatic complexity for the current file
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                source_code = f.read()
            tree = mccabe.parse_string(source_code)
            cyclomatic_complexity = mccabe.complexity(tree)

            # Extract relevant metrics from the results
            filename = file
            cyclomatic_complexity = cyclomatic_complexity

            # Append the extracted metrics to the list
            cyclomatic_complexity_data.append((filename, cyclomatic_complexity))

# Open the output CSV file in write mode
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write the column headers
    writer.writerow(['Filename', 'Cyclomatic Complexity'])

    # Write the extracted metrics to the CSV file
    writer.writerows(cyclomatic_complexity_data)
