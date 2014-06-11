#! /usr/bin/python

# get stations into particular files
# usage: get_stations namefile inputfile outputdir
import sys, string;


def get(namefile, inputfile, outputfile):
  file = open(namefile, "rt");
  names = file.readlines();
  file.close();

  for rawname in names:
    name = string.strip(rawname);
    if not name: continue
    file = open(inputfile, "rt");
    out = open("%s/%s"%(outputdir,name), "wt");
    while 1:
      line = file.readline();
      if not line: break;
      line = string.strip(line);
      if not line: continue;
      fields = string.split(line)
      if fields[0] == name:
	out.write("%s\t%s\t%s\t%s\n"%(fields[4],fields[0],fields[2],fields[3]));
    file.close();
    out.close();

if __name__ == "__main__":
  if len(sys.argv) < 4:
    print "usage: %s namefile inputfile outputdir"%sys.argv[0]
    print "where namefile has list of names to extract (1/line)"
    print "      inputfile is the concatenated reduced data"
    print "      outputdir is the directory name to put results into"
    sys.exit();

  namefile = sys.argv[1];
  inputfile = sys.argv[2];
  outputdir = sys.argv[3];

  get(namefile, inputfile, outputdir);
