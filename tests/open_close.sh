#!/bin/bash
PROGRAM="../main.py"
echo Python Script without detaching the cid >> o_c_log_err.txt
for i in `seq 1 50`;
do 
		echo Running iteration $i &>> o_c_log_err.txt 
		python $PROGRAM 2.0 &>>  o_c_log_err.txt
done
