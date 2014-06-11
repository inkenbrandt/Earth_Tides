NR == 1 {offset = $3; print $0}
NR != 1 { print $1 "\t" $2 "\t" $3-offset "\t" $4 }
