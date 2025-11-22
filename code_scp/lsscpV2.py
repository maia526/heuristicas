"""      Heuristic Optimization     """
"""              2016               """    
"""       Template exercise 1       """
"""       Set Covering Problem      """
"""                                 """
""" For this code:                  """
"""   rows = elements               """
"""   cols = subsets                """

""" Code implemented for Heuritics optimization class by:  """
""" <add_your_name_here>                                   """

""" Note: Remember to keep your code in order and properly commented. """

import sys
import random
import math

# Algorithm parameters
seed = 1234567
scp_file = ""
output_file = "output.txt"

# Variables to activate algorithms
ch1 = 0
ch2 = 0
bi = 0
fi = 0
re = 0

# Instance static variables
m = 0            # number of rows
n = 0            # number of columns
row = None       # row[i] rows that are covered by column i
col = None       # col[i] columns that cover row i
ncol = None      # ncol[i] number of columns that cover row i
nrow = None      # nrow[i] number of rows that are covered by column i
cost = None      # cost[i] cost of column i

# Solution variables
x = None         # x[i] 0,1 if column i is selected
y = None         # y[i] 0,1 if row i covered by the actual solution
# Note: Use incremental updates for the solution
fx = 0           # sum of the cost of the columns selected in the solution (can be partial)

# Dynamic variables
# Note: use dynamic variables to make easier the construction and modification of solutions.
#       these are just examples of useful variables.
#       these variables need to be updated everytime a column is added to a partial solution
#       or when a complete solution is modified
col_cover = None  # col_cover[i] selected columns that cover row i
ncol_cover = 0    # number of selected columns that cover row i


def error_reading_file(text):
    print(text)
    sys.exit(1)


def usage():
    print("\nUSAGE: lsscpV2.py [param_name, param_value] [options]...")
    print("Parameters:")
    print("  --seed : seed to initialize random number generator")
    print("  --instance: SCP instance to execute.")
    print("  --output: Filename for output results.")
    print("Options:")
    print("  --ch1: random solution construction")
    print("  --ch2: static cost-based greedy values.")
    print("  --re: applies redundancy elimination after construction.")
    print("  --bi: best improvement.")
    print("\n")


# Read parameters from command line
# NOTE: Complete parameter list
def read_parameters(argv):
    global seed, scp_file, output_file, ch1, ch2, bi, fi, re
    
    if len(argv) <= 1:
        usage()
        sys.exit(1)
    
    i = 1
    while i < len(argv):
        if argv[i] == "--seed":
            seed = int(argv[i+1])
            i += 2
        elif argv[i] == "--instance":
            scp_file = argv[i+1]
            i += 2
        elif argv[i] == "--output":
            output_file = argv[i+1]
            i += 2
        elif argv[i] == "--ch1":
            ch1 = 1
            i += 1
        elif argv[i] == "--ch2":
            ch2 = 1
            i += 1
        elif argv[i] == "--bi":
            bi = 1
            i += 1
        elif argv[i] == "--fi":
            fi = 1
            i += 1
        elif argv[i] == "--re":
            re = 1
            i += 1
        else:
            print(f"\nERROR: parameter {argv[i]} not recognized.")
            usage()
            sys.exit(1)
    
    if not scp_file or scp_file == "":
        print("Error: --instance must be provided.")
        usage()
        sys.exit(1)


# Read instance in the OR-LIBRARY format
def read_scp(filename):
    global m, n, row, col, ncol, nrow, cost
    
    try:
        fp = open(filename, "r")
    except IOError:
        error_reading_file("ERROR: could not open instance file.")
    
    try:
        # number of rows and columns (may be on same line or different lines)
        line = fp.readline().strip()
        if not line:
            error_reading_file("ERROR: there was an error reading instance file.")
        values = line.split()
        if len(values) < 1:
            error_reading_file("ERROR: there was an error reading instance file.")
        m = int(values[0])
        
        # number of columns (may be on same line as m or next line)
        if len(values) >= 2:
            n = int(values[1])
        else:
            line = fp.readline().strip()
            if not line:
                error_reading_file("ERROR: there was an error reading instance file.")
            values = line.split()
            if len(values) < 1:
                error_reading_file("ERROR: there was an error reading instance file.")
            n = int(values[0])
        
        # Cost of the n columns (may span multiple lines)
        cost = []
        cost_values = []
        while len(cost_values) < n:
            line = fp.readline().strip()
            if not line:
                error_reading_file("ERROR: there was an error reading instance file.")
            cost_values.extend(line.split())
        
        if len(cost_values) < n:
            error_reading_file("ERROR: there was an error reading instance file.")
        
        for j in range(n):
            cost.append(int(cost_values[j]))
        
        # Info of columns that cover each row
        col = []
        ncol = []
        for i in range(m):
            line = fp.readline().strip()
            if not line:
                error_reading_file("ERROR: there was an error reading instance file.")
            values = line.split()
            if len(values) < 1:
                error_reading_file("ERROR: there was an error reading instance file.")
            ncol_i = int(values[0])
            ncol.append(ncol_i)
            
            col_i = []
            col_values = values[1:] if len(values) > 1 else []
            # Read additional lines if needed
            while len(col_values) < ncol_i:
                line = fp.readline().strip()
                if not line:
                    error_reading_file("ERROR: there was an error reading instance file.")
                col_values.extend(line.split())
            
            if len(col_values) < ncol_i:
                error_reading_file("ERROR: there was an error reading instance file.")
            
            for h in range(ncol_i):
                col_i.append(int(col_values[h]) - 1)  # Convert to 0-based indexing
            col.append(col_i)
        
        # Info of rows that are covered by each column
        # First, count how many rows each column covers
        nrow = [0] * n
        for i in range(m):
            for h in range(ncol[i]):
                nrow[col[i][h]] += 1
        
        # Now, build the row array
        row = []
        k = [0] * n
        for j in range(n):
            row.append([0] * nrow[j])
        
        for i in range(m):
            for h in range(ncol[i]):
                col_idx = col[i][h]
                row[col_idx][k[col_idx]] = i
                k[col_idx] += 1
        
        fp.close()
        
    except (ValueError, IndexError) as e:
        error_reading_file("ERROR: there was an error reading instance file.")


# Use level>=1 to print more info (check the correct reading)
def print_instance(level):
    print("**********************************************")
    print(f"  SCP INSTANCE: {scp_file}")
    print(f"  PROBLEM SIZE\t m = {m}\t n = {n}")
    
    if level >= 1:
        print("  COLUMN COST:")
        for i in range(n):
            print(f"{cost[i]} ", end="")
        print("\n")
        if nrow and len(nrow) > 0:
            print(f"  NUMBER OF ROWS COVERED BY COLUMN 1 is {nrow[0]}")
            if row and len(row) > 0 and len(row[0]) > 0:
                for i in range(nrow[0]):
                    print(f"{row[0][i]} ", end="")
                print()
        if ncol and len(ncol) > 0:
            print(f"  NUMBER OF COLUMNS COVERING ROW 1 is {ncol[0]}")
            if col and len(col) > 0 and len(col[0]) > 0:
                for i in range(ncol[0]):
                    print(f"{col[0][i]} ", end="")
                print()
    
    print("**********************************************\n")


# Use this function to initialize other variables of the algorithms
def initialize():
    pass


# Use this function to finalize execution
def finalize():
    # In Python, memory is automatically managed, but we can clear references
    global row, col, nrow, ncol, cost
    row = None
    col = None
    nrow = None
    ncol = None
    cost = None


if __name__ == "__main__":
    read_parameters(sys.argv)
    random.seed(seed)  # set seed
    read_scp(scp_file)
    print_instance(1)
    finalize()
    sys.exit(0)

