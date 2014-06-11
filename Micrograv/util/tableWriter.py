# Formatted Table Writes
#
# usage:
# create a a tableWriter instance, setting justification, columnwidth, and
# separator
#
# note that this assumes fixed, constant width columns!
#
# set the header for the table with writeHeader - embedded newlines are OK
# (use '\n'); lines will be centered over the table
#
# then, add rows or columns using writeRow/writeColumn
# start a new row with newRow() - columns are appended until newRow is
# called!
# writeRow/writeColumn take string arguments!
#
# when done, draw the table to stdout using writeTable()
#
# Can change the separator partway through, although this assumes the length
# of string is constant
#
# Can also change the justification at will; use setJustify('R'|'L')
#
# Only last call to writeHeader matters!
#

import sys, string

class tableWriter:
  def __init__(self, cwidth, justify=0, sep='|'):
    self.__cw = cwidth
    self.__justify = justify
    self.__cs = sep
    self.__cr = 0
    self.__nr = 1
    self.__rows = []
    self.__nc = 0
    self.__cc = 0
    self.__rows.append("")
    self.__header = ""

  def setJustify(self, justify):
    if justify == 'R':
      self.__justify = 1
    elif justify == 'L':
      self.__justify = 0
    else:
      self.__justify = 0

  def setSeparator(self, sep):
    self.__cs = sep

  def writeHeader(self, headerstring):
    self.__header = headerstring

  def writeRow(self, strings, row=-1):
    if row != -1:
      self.__cr = row - 1
    for s in strings:
      self.writeColumn(s)

  def newRow(self):
    self.__cr = self.__cr + 1
    if self.__cr == 0:
      # were at last row, so we set to that again
      self.__cr = len(self.__rows)
    self.__rows.append("")
    if self.__cc > self.__nc:
      self.__nc = self.__cc
    self.__cc = 0

  def writeColumn(self, string):
    if self.__justify == 0:	## LEFT
      self.__rows[self.__cr] = "%s%s"%(self.__rows[self.__cr], string[0:self.__cw])
      self.__rows[self.__cr] = "%s%s"%(self.__rows[self.__cr], " "*(self.__cw-len(string)))
    elif self.__justify == 1:	## RIGHT
      self.__rows[self.__cr] = "%s%s"%(" "*(self.__cw-len(string)))
      self.__rows[self.__cr] = "%s%s"%(self.__rows[self.__cr], string[0:self.__cw])
    self.__rows[self.__cr] = "%s%s"%(self.__rows[self.__cr], self.__cs)
    self.__cc = self.__cc + 1

  def writeTable(self):
    # spit out header
    lines = string.split(self.__header, "\n")
    for i in range(len(lines)):
      sys.stdout.write(" "*((self.__nc/2*(self.__cw+len(self.__cs))) - len(lines[i])/2))
      sys.stdout.write(lines[i])
      sys.stdout.write("\n")
      
    # spit out rows
    for i in range(len(self.__rows)):
      sys.stdout.write("%s"%self.__rows[i])
      sys.stdout.write("\n")

