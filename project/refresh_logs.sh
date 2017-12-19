#!/bin/bash
# Store server names in array
declare -a logfiles=("log_alford.log" "log_holiday.log" "log_welsh.log" "log_ball.log" "log_hamilton.log")
# Remove each logfile
echo "Flushing all logs..."
for files in "${logfiles[@]}"; do
    > "$files"
done
echo "Complete"
