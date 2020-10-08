DCB_operation.py standalone script allows users to write I/O to a source, check for consistency data on source and target hosts, pause, resume and stop DCB I/O processes.

Also, you can choose which array you need to work with, currently implemented two storage systems: XtremIO and Vplex.
The script was tested on Python interpreter version 3.7.
If you work with one resource for a long time, you can exclude additional steps to determine the initial data, just correct next variables:
- host
- password
- storage
This script used DCB writes to 20% of the capacity of the specified data set (parameter -size in run_dcb function).

The basic operations:

1. Start a DCB instance

When DCB starts, it uses devices from the storage system you specified earlier. If DCB instances have already started on some devices of storage system you're chosen, you need to answer 'yes' on the additional question. In this case, only new devices will be used for the start process.

If the logical unit configuration of the host has not been updated yet for new disks, you can select this option during the start process.

Upon completion of the start process, you will find running on the host:
- screen sessions for each device
- DCB instances ( wait until DCB has completed initializing the data set.)

2. Check a DCB instance

There are two ways to check the consistency of a dataset: use the consist -check command to verify the consistency of a static point-in-time copy (snap, clone, etc.) on the target host or the dataset for a paused DCB instance on the source host. The value of 'source' or 'target' host you will be prompted to select during this process

a) If you are checking the consistency of datasets on source host:

After the completion of the check process, you will find on the source host a new one screen session for all devices and generated files, in root user's home directory (for each DCB instance), in which will record the result of the verification operation of each DC instance. In the future, these files will be overwritten at the next run of this procedure.

b) If you are checking the consistency of a static point-in-time copy (snap, clone, etc.) on the target host:

After the completion of the check process, you will find on the target host screen sessions for all devices where you can find results. 

3. Pause and Resume IO

When these operations are selected, one screen session and generated files, in root user's home directory (for each DCB instance), will be created with the result of the operation.

4. Stop a DCB instance

When DCB instances stoped, screen sessions are also deleted.
