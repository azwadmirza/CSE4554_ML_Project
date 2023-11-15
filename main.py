import os
import csv
from radon.complexity import cc_visit
import textwrap

def calculate_cyclomatic_complexity(file_path):
    print(file_path)
    with open(file_path, 'r', encoding='latin-1') as file:
        content = file.read()
    content=textwrap.dedent(content)
    try:
        results = cc_visit(content)
    except Exception as e:
        return []
    else:
        return results

def process_files_in_folder(folder_path):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".py"):
            file_path = os.path.join(folder_path, filename)
            complexity_results = calculate_cyclomatic_complexity(file_path)
            total_complexity = sum(item.complexity for item in complexity_results)
            results.append((filename, total_complexity))
    return results

def write_results_to_csv(results, output_csv):
    with open(output_csv, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['File Name', 'Cyclomatic Complexity'])
        for filename, total_complexity in results:
            csv_writer.writerow([filename, total_complexity])

if __name__ == "__main__":
    folder_path = "./buggy_snippets_files"
    output_csv = "complexity_results_buggy.csv"

    complexity_results = process_files_in_folder(folder_path)
    write_results_to_csv(complexity_results, output_csv)