#!/usr/bin/python

## Compute the average signal for a day
## Date format is assumed to be "MM/DD/YYYY"
## Column that is date is a command-line option

## usage: average_day.py infile outfile date_col sig_col

import sys, string;

def main():
  # get cmd-line args
  if len(sys.argv) < 5:
    usage();

  infile = sys.argv[1];
  outfile = sys.argv[2];
  date_col = int(sys.argv[3]);
  sig_col = int(sys.argv[4]);

  file = open(infile, "rt");
  out = open(outfile, "wt");
  old_day = 0;
  sum = 0.0; n = 0;
  while 1:
    line = file.readline();
    if not line: break
    line = string.strip(line);
    if not line: continue
    if line[0] == "#":
      out.write("%s\n"%line)
      continue

    fields = string.split(line);

    date_str = fields[date_col - 1];
    sig_str  = fields[sig_col  - 1];

    signal = float(sig_str);

    df = string.split(date_str, "/");
    day = int(df[1]);
    if old_day == day:
      sum = sum + signal;
      n = n+1;
    else:
      if n > 0:
	output_record(out, fields, old_date, sum/n, sig_col, date_col);
      sum = 0.0
      n = 0
      old_day = day;
      old_date = date_str;
  output_record(out, fields, old_date, sum/n, sig_col, date_col);
  file.close();
  out.close();

def output_record(out, fields, date, signal, scol, dcol):
  for i in range(len(fields)):
    if i == scol-1:
      out.write("%s "%signal);
    elif i == dcol-1:
      out.write("%s "%date);
    else:
      out.write("%s "%fields[i]);
  out.write("\n");

def usage():
  print "usage: %s <infile> <outfile> date_col sig_col"%sys.argv[0]
  sys.exit();

## Run it
main()
