#!/bin/bash
#
## usage: make_trend_plot.sh LONG_TERM_DRIFT_FILE REDUCE.PY_OUTPUT_FILE

# compute long-term drift rate
cg3e_cmd.py $1 longterm "RD G S"
drift=`llsq.py longterm 1 2`
echo "Drift rate: ${drift}"

# Get start date, time, and gravity
cg3e_cmd.py $1 longterm "TS G S"
start_date=`tail -1 longterm | awk '{printf("%s", $1)}'`
start_time=`tail -1 longterm | awk '{printf("%s", $2)}'`
start_g=`tail -1 longterm | awk '{printf("%s", $3)}'`
echo "Start date, time, and gravity"
echo ${start_date}
echo ${start_time}
echo ${start_g}

# compute the plottable trend file
~/micrograv/micrograv-src/util/calc_trend_stations.py $2 ${drift} \
	${start_date} ${start_time} ${start_g} > stations

# create the plot
cat > gnuplot.cmd <<EOF
#!/usr/bin/gnuplot -persist
# gnuplot command file for trended station plot
set xdata time
set format y "%.3f"
set format x "%m/%d/%Y\n%H:%M:%S"
set title "" 0.000000,0.000000  ""
set xlabel "Date" 0.000000,0.000000  ""
set timefmt "%m/%d/%Y %H:%M:%S"
set xrange [ "${start_date} 0:0:0" : * ] noreverse nowriteback
set ylabel "Reading (mGal)" 0.000000,0.000000  ""
set key top left
set term post
set output "trend.ps"
plot "longterm" u 1:3 t "" w l, "longterm" u 1:(\$3-\$4) t "" w l, "longterm" u 1:(\$3+\$4) t "" w l, \
	"stations" i 0 u 1:3 t "BEAR" w lp, \
	"stations" i 1 u 1:3 t "EGI" w lp, \
	"stations" i 2 u 1:3 t "FALC" w lp, \
	"stations" i 3 u 1:3 t "FOXH" w lp, \
	"stations" i 4 u 1:3 t "MAIN" w lp, \
	"stations" i 5 u 1:3 t "MNTN" w lp, \
	"stations" i 6 u 1:3 t "MOCK" w lp, \
	"stations" i 7 u 1:3 t "VAULT" w lp, \
	"stations" i 8 u 1:3 t "VAULT" w lp, \
	"stations" i 9 u 1:3 t "WIND" w lp
EOF

gnuplot gnuplot.cmd
