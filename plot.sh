#!/bin/sh

python digest.py < ~/tmp/temp.log > data.txt

tee script <<EOF | gnuplot
set terminal svg enhanced background rgb "white" size 800 600
set output "graph.svg"
set ytics nomirror
set y2tics auto
set ylabel "Humidity"
set y2label "Temperature"
set xdata time
set timefmt "%Y-%m-%dT%H:%M:%S"
set xtics format "%H:%M:%S"
set xtics rotate
plot "data.txt" using 1:2 with lines title "Humidity (%)", \
	"data.txt" using 1:3 with lines axis x1y2 title "Temperature (°C)"
EOF

eog graph.svg
