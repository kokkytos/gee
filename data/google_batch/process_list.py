import os
import sys
import subprocess

def run_gini_process(index):
    filename = 'year_fua_list.txt'
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            
            if 0 <= index < len(lines):
                target_line = lines[index].strip()
                # Split line into YEAR and NUTS (FUA)
                YEAR, NUTS = target_line.split()
                
                print(f"--- Task Index {index} ---")
                print(f"Extracted: YEAR={YEAR}, FUA={NUTS}")
                
                # Call gini.py using subprocess
                # We convert YEAR to string to pass it as a command line argument
                subprocess.run([
                    sys.executable,  # Ensures we use the same Python environment
                    "/app/gini.py", 
                    str(YEAR), 
                    str(NUTS)
                ], check=True)
                
            else:
                print(f"Error: Index {index} out of range.")
    except FileNotFoundError:
        print("Error: year_fua_list.txt not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error: gini.py failed with exit code {e.returncode}")

if __name__ == "__main__":
    # Check if we are running in GC Batch via environment variable
    # If not found, default to command line argument, then default to 0
    batch_index = os.environ.get("BATCH_TASK_INDEX")
    
    if batch_index is not None:
        idx = int(batch_index)
    elif len(sys.argv) > 1:
        idx = int(sys.argv[1])
    else:
        idx = 0
        
    run_gini_process(idx)