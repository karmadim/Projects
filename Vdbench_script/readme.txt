vdbench_io.py standalone, interaction script designed to execute a controlled IO load on a storage system.The script was tested on Python interpreter version 3.7.
Raw I/O workload generated on all volumes which mapped to LG (the script doesn't generate file systems workload).
Script use next parameters for I/O such as data deduplication, compression, LUN sizes, transfer sizes, percentage skew, I/O rate to be generated, elapsed time and interval, and random or sequential read/write workloads.

Variables 'host' and 'password' are used to connect to the linux host.

The configuration file 'io_config.txt' is created in the /root/ directory, an output directory with the reports that Vdbench creates is also created there.

Vdbench process (vdbench -f /root/io_config.txt) runs in the screen session 'vdbench_1' on the host.



Example of script execution:

C:\Users\karmad3\AppData\Local\Programs\Python\Python37-32\python.exe C:/Users/karmad3/PycharmProjects/kdv/vdbench_io.py
Connecting to ssh host lg712.xiolab.lab.emc.com ...
#### General parameters:
----Data Deduplication (dedupratio)
The dedup logic included in the target storage device looks at each n-byte data block to see if a block with identical content already exists. 
Ratio between the original data and the actually written data, e.g. dedupratio=2 for a 2:1 ratio. If not specified, no deduplication: 4
---- Size of data does Dedup compare (dedupunit)
The size of a data block that dedup tries to match with alreadyexisting data. There is no longer a default of 128k
Enter numbers with a symbol (k) without space: 32k
----Compression for data patterns (compratio)
Compression generates a data pattern that results in a nn:1 ratio. If not specified, data uncompressed: 2
#### Storage Definition parameters:
----The size of the raw disk (size)
If not specified, the size will be taken from the raw disk.
Enter numbers with a symbol (k/m/g/t) without space: 
#### Workload Definition parameters:
Random Read I/O (type 'yes' if necessary): yes
---- Data Transfer Size (xfersize)
Specifies how much data is transferred for each I/O operation.
Allows (k)ilo and (m)ega bytes. Enter numbers with 'k' or 'm' symbol without space. Default - 4k : 
---- Percentage skew (skew).
Specifies the percentage of the run's total I/O rate that will be generated for workload. 
By default the total I/O rate will be evenly divided among all workloads. 
However, if the skew value is nonzero for this WD, the remaining skew evenly divided among the workloads that have no skew percentage specified.
The total skew for all workloads used in a Run Definition must equal 100%. 
Enter only numbers without a '%' symbol or not specify: 10
Random Write I/O (type 'yes' if necessary): yes
---- Data Transfer Size (xfersize)
Specifies how much data is transferred for each I/O operation.
Allows (k)ilo and (m)ega bytes. Enter numbers with 'k' or 'm' symbol without space. Default - 4k : 8k
---- Percentage skew (skew).
Specifies the percentage of the run's total I/O rate that will be generated for workload. 
By default the total I/O rate will be evenly divided among all workloads. 
However, if the skew value is nonzero for this WD, the remaining skew evenly divided among the workloads that have no skew percentage specified.
The total skew for all workloads used in a Run Definition must equal 100%. 
Enter only numbers without a '%' symbol or not specify: 20
Sequential Read I/O (type 'yes' if necessary): yes
---- Data Transfer Size (xfersize)
Specifies how much data is transferred for each I/O operation.
Allows (k)ilo and (m)ega bytes. Enter numbers with 'k' or 'm' symbol without space. Default - 4k : 16k
---- Percentage skew (skew).
Specifies the percentage of the run's total I/O rate that will be generated for workload. 
By default the total I/O rate will be evenly divided among all workloads. 
However, if the skew value is nonzero for this WD, the remaining skew evenly divided among the workloads that have no skew percentage specified.
The total skew for all workloads used in a Run Definition must equal 100%. 
Enter only numbers without a '%' symbol or not specify: 30
Sequential Write I/O (type 'yes' if necessary): yes
---- Data Transfer Size (xfersize)
Specifies how much data is transferred for each I/O operation.
Allows (k)ilo and (m)ega bytes. Enter numbers with 'k' or 'm' symbol without space. Default - 4k : 32k
---- Percentage skew (skew).
Specifies the percentage of the run's total I/O rate that will be generated for workload. 
By default the total I/O rate will be evenly divided among all workloads. 
However, if the skew value is nonzero for this WD, the remaining skew evenly divided among the workloads that have no skew percentage specified.
The total skew for all workloads used in a Run Definition must equal 100%. 
Enter only numbers without a '%' symbol or not specify: 
#### Run Definition parameters:
---- IO rates to be generated (iorate)
Appropriate options:
100 : Run a workload of 100 I/Os per second
100,200,… : Run a workload of 100 I/Os per second, then 200, etc
curve : Run a performance curve
max': Run the maximum I/O rate possible
Enter IO rate: 200
---- Elapsed Time (elapsed)
Specifies the elapsed time in seconds for each run.
This value needs to be at least twice the value of the reporting interval below: 30
---- Reporting Interval (interal)
Specifies the duration in seconds for each reporting interval: 1
One screen session 'vdbench_1' was run on host lg712.xiolab.lab.emc.com
Result in: /root/output


Created configuration file on the host:

[root@lg712 ~]# cat io_config.txt
dedupratio=4
dedupunit=32k
compratio=2
sd=default,openflags=o_direct
sd=sd1,lun=/dev/mapper/3514f0c5a5780000f
sd=sd2,lun=/dev/mapper/3514f0c5a5780000e
sd=sd3,lun=/dev/mapper/3514f0c5a5780000d
sd=sd4,lun=/dev/mapper/3514f0c5a57800011
sd=sd5,lun=/dev/mapper/3514f0c5a57800010
wd=RR,sd=sd*,xfersize=4k,skew=10,rdpct=100,seekpct=random
wd=RW,sd=sd*,xfersize=8k,skew=20,rdpct=0,seekpct=random
wd=SR,sd=sd*,xfersize=16k,skew=30,rdpct=100,seekpct=0
wd=SW,sd=sd*,xfersize=32k,rdpct=0,seekpct=0
rd=IOWG1,wd=*,iorate=(200),elapsed=30,interval=1,forthreads=5
[root@lg712 ~]#