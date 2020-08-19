"""
This file takes in 5 flags:

--op: a string representing the operation (can be 'add', 'mul', or 'shl')

--nests_list: a list of integers representing the number of nested ops for each proof

--bits: an integer representing the bitvector length for the inputs of the proof

--solvers: a list of strings representing each of the solvers to be tested

--fname: a file name to store the data (if fname already exists, data is appended
         to the end of the file)

This script creates smt2 files for each proof, runs each of the solvers on these
smt2 files, and stores the speed of each solver on each smt2 file in a csv file. 
This data can then be plotted using plot_csv_solver_speed_data.py.
"""
import sys
import csv
from matplotlib import pyplot as plt
from n_bit_nested_add_generator import n_bit_nested_add_existing_file
from n_bit_nested_mul_generator import n_bit_nested_mul_existing_file
from n_bit_nested_shift_generator import n_bit_nested_shift_existing_file
from solvers_op_comparison_functions import *
from xls.common.gfile import open as gopen
from flags_checks import *

from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string("op", None, "Operation for the smt2 files (add, mul, shl)")
flags.DEFINE_integer("bits", None, "Integer for the number of bits.")
flags.DEFINE_list("nests_list", None, "List of nest values for each n-bit multiplication proof.")
flags.register_validator("nests_list",
                         list_contains_only_integers,
                         message="--nests_list must contain only integers.")
flags.DEFINE_list("solvers", None, "List of solvers to test.")
flags.DEFINE_string("fname", None, "Name for the file to store the data.")

flags.mark_flag_as_required("op")
flags.mark_flag_as_required("bits")
flags.mark_flag_as_required("nests_list")
flags.mark_flag_as_required("fname")
flags.mark_flag_as_required("solvers")

def create_and_get_smt_files_nests_list(op, nests_list, bits_val):
  """
  Create smt2 files for the necessary proof and return them in a list. 

  Given an operation, a list of nest values, and the number of bits, create smt2
  files for each proof, and return them in a list. 

  Args:
  op: A string, the operation to test ('add', 'mul', or 'shl')
  nests_list: A list of integers, the number of nested operations for each proof
  bits_val: An integer, the input bitvector length
  """
  if op not in ["add", "mul"]:
    raise ValueError("op argument is not a valid operation")
  files = []
  for nest in nests_list:
    with gopen(f"{op}{nest}_2x{bits_val}.smt2", "w+") as f:
      files.append(f)
      if op == "add":
        n_bit_nested_add_existing_file(bits_val, nest, f)
      elif op == "mul":
        n_bit_nested_mul_existing_file(bits_val, nest, f)
      elif op == "shl":
        n_bit_nested_shift_existing_file(bits_val, nest, f)
  return files

def csv_solvers_speeds_nests_list(op, nests_list, bits_val, solvers, fname):
  """
  Create smt2 files for each proof, test the solvers, and write the data to a csv file.

  Create smt2 files for each of the nest values in nests_list with the 
  given operation and the input bitvector length, get the average speeds of 
  each of the solvers on these proofs, and store the data in a csv file with fname.

  Args:
  op: A string, the operation to test
  nests_list: A list of integers, the number of nested operations for each proof
  bits_val: An integer, the input bitvector length
  solvers: A list of strings, the solvers to test
  fname: The name of the file to store the data in
  """
  files = create_and_get_smt_files_nests_list(op, nests_list, bits_val)
  solvers_milliseconds = get_solver_speeds_ms(solvers, files)
  write_row = False if os.path.isfile(fname) else True
  with gopen(fname, "a") as f:
    wr = csv.writer(f, delimiter=",")
    if write_row:
      wr.writerow(["nests_list"] + nests_list)
    for i in range(len(solvers)):
      wr.writerow([solvers[i]] + solvers_milliseconds[i])

def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')
  else:
    op = FLAGS.op
    bits_val = FLAGS.bits
    nests_list = [int(elm) for elm in FLAGS.nests_list]
    solvers = FLAGS.solvers
    fname = FLAGS.fname
    csv_solvers_speeds_nests_list(op, nests_list, bits_val, solvers, fname)

if __name__ == '__main__':
  app.run(main)

