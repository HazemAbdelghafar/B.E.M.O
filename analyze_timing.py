import re
import statistics
from pathlib import Path
import glob

def extract_timing_data(log_file):
    timing_data = {
        'post': [],
        'pre': [],
        'task_classifier': [],
        'task_handler': [],
        'smart_home': [],
        'todo': [],
        'learning_resources': [],
        'total': []
    }
    
    # Updated regex pattern to match both timing formats
    patterns = [
        r'Execution time \((.*?)\): (\d+\.\d+) seconds',  # Format: Execution time (module): time seconds
        r'Execution time for (.*?): (\d+\.\d+) seconds'   # Format: Execution time for module: time seconds
    ]
    
    print(f"\nProcessing file: {log_file}")
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            for pattern in patterns:
                matches = re.findall(pattern, line)
                for module, time in matches:
                    time = float(time)
                    module = module.lower().strip()
                    print(f"Found timing data - Module: {module}, Time: {time}")
                    
                    # Map module names to our categories
                    if module == 'all':
                        timing_data['total'].append(time)
                    elif module in timing_data:
                        timing_data[module].append(time)
                    # Handle variations in module names
                    elif 'smart home' in module or 'smart_home' in module:
                        timing_data['smart_home'].append(time)
                    elif 'todo' in module or 'tasks_api' in module:
                        timing_data['todo'].append(time)
                    elif 'learning' in module:
                        timing_data['learning_resources'].append(time)
                    elif 'preprocessing' in module or 'pre' in module:
                        timing_data['pre'].append(time)
                    elif 'postprocessing' in module or 'post' in module:
                        timing_data['post'].append(time)
                    elif 'task_classifier' in module:
                        timing_data['task_classifier'].append(time)
                    elif 'task_handler' in module:
                        timing_data['task_handler'].append(time)

    # Print summary of found data
    print("\nSummary of found timing data:")
    for module, times in timing_data.items():
        if times:
            print(f"{module}: {len(times)} entries")
    
    return timing_data

def calculate_statistics(data):
    stats = {}
    for module, times in data.items():
        if times:  # Only calculate if we have data
            stats[module] = {
                'average': statistics.mean(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                'count': len(times)
            }
    return stats

def main():
    # Get all log files in the B.E.M.O directory and its subdirectories
    log_files = glob.glob('**/logging.log', recursive=True)
    
    all_timing_data = {
        'post': [],
        'pre': [],
        'task_classifier': [],
        'task_handler': [],
        'smart_home': [],
        'todo': [],
        'learning_resources': [],
        'total': []
    }
    
    # Process each log file
    for log_file in log_files:
        timing_data = extract_timing_data(log_file)
        for module, times in timing_data.items():
            all_timing_data[module].extend(times)
    
    # Calculate statistics
    stats = calculate_statistics(all_timing_data)
    
    # Write results to a file
    with open('timing_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("Timing Analysis Results:\n")
        f.write("-" * 50 + "\n")
        
        # Print module statistics: avg, min, max, std for each task
        modules = ['pre', 'post', 'task_classifier', 'task_handler', 'smart_home', 'todo', 'learning_resources']
        for module in modules:
            if module in stats:
                data = stats[module]
                f.write(f"{module.upper()}:\n")
                f.write(f"  Average time: {data['average']:.3f} seconds\n")
                f.write(f"  Min time: {min(all_timing_data[module]):.3f} seconds\n")
                f.write(f"  Max time: {max(all_timing_data[module]):.3f} seconds\n")
                f.write(f"  Standard deviation: {data['std_dev']:.3f} seconds\n\n")
        
        # Print total statistics: avg, min, max, std
        if 'total' in stats:
            data = stats['total']
            f.write("TOTAL EXECUTION:\n")
            f.write(f"  Average time: {data['average']:.3f} seconds\n")
            f.write(f"  Min time: {min(all_timing_data['total']):.3f} seconds\n")
            f.write(f"  Max time: {max(all_timing_data['total']):.3f} seconds\n")
            f.write(f"  Standard deviation: {data['std_dev']:.3f} seconds\n")

if __name__ == "__main__":
    main() 