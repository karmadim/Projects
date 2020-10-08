import paramiko
import getpass
import operator
import sys


def io_spec(parameter, mandatory=False):
    value = input(parameter)
    if not value and mandatory:
        print("##### This parameter is required! #####")
        value = io_spec(parameter, mandatory)
    return value


def wd_spec(wd_name):
    command = 'wd=' + wd_name + ',sd=sd*,xfersize='
    xfersize = io_spec("---- Data Transfer Size (xfersize)\n"
                       "   Specifies how much data is transferred for each I/O operation.\n"
                       "   Allows (k)ilo and (m)ega bytes. "
                       "Enter numbers with 'k' or 'm' symbol without space. Default - 4k : ")
    command += xfersize if xfersize else ('4k')

    skew = io_spec("---- Percentage skew (skew).\n"
                   "   Specifies the percentage of the run's total I/O rate that will be generated for workload. \n"
                   "   By default the total I/O rate will be evenly divided among all workloads. \n"
                   "   However, if the skew value is nonzero for this WD, the remaining skew "
                   "evenly divided among the workloads that have no skew percentage specified.\n"
                   "   The total skew for all workloads used in a Run Definition must equal 100%.  \n"
                   "   Enter only numbers without a '%' symbol or not specify: ")
    if skew:
        command += ',skew=' + str(skew)
    command += ',rdpct=100' if wd_name[-1] == "R" else ',rdpct=0'
    command += ',seekpct=0' if wd_name[0] == "S" else ',seekpct=random'
    command += '\n'
    return command


if __name__ == "__main__":
    #   host = input("Enter LG short name to collect volumes from: ") + ".xiolab.lab.emc.com"
    #    host = input("Enter LG fqdn name to collect volumes from: ")
    host = 'lg712.xiolab.lab.emc.com'
    user = 'root'
    password = 'Password123!'
    #    password = getpass.getpass('Enter root password: ')
    port = 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print('Connecting to ssh host {} ...'.format(host))
    try:
        client.connect(host, port, user, password, look_for_keys=True, allow_agent=True)
    except Exception as e:
        print('*** Failed to connect to {}: {}'.format(host, e))
        sys.exit(1)

    print('#### General parameters:')

    io_config = ''
    dedupratio = io_spec("----Data Deduplication (dedupratio)\n"
                         "   The dedup logic included in the target storage device looks at each n-byte data block "
                         "to see if a block with identical content already exists. \n"
                         "   Ratio between the original data and the actually written data, e.g. "
                         "dedupratio=2 for a 2:1 ratio. If not specified, no deduplication: ")
    if dedupratio:
        io_config += 'dedupratio=' + str(dedupratio) + '\n'
        dedupunit = io_spec("---- Size of data does Dedup compare (dedupunit)\n"
                            "   The size of a data block that dedup tries to match with already"
                            "existing data. There is no longer a default of 128k\n"
                            "   Enter numbers with a symbol (k) without space: ", mandatory=True)
        io_config += 'dedupunit=' + str(dedupunit) + '\n'

    compratio = io_spec("----Compression for data patterns (compratio)\n"
                        "   Compression generates a data pattern that results in a nn:1 ratio. If not specified, "
                        "data uncompressed: ")
    if compratio:
        io_config += 'compratio=' + str(compratio) + '\n'

    print('#### Storage Definition parameters:')

    io_config += 'sd=default,openflags=o_direct'
    size = io_spec("----The size of the raw disk (size)\n"
                   "   If not specified, the size will be taken from the raw disk.\n"
                   "   Enter numbers with a symbol (k/m/g/t) without space: ")
    if size:
        io_config += ',size=' + str(size)

    if not dedupratio:
        align = io_spec("----Determine lba boundary for random seeks (align)\n"
                        "   Vdbench generates an random lba (logical byte address) it by default is always on "
                        "a block boundary (xfersize=). \n"
                        "   You can change that to always generate an LBA on a different alignment. \n"
                        "   The align= value is in bytes and must be a multiple of 512 or kilobytes (k). \n"
                        "   If not specified, the block boundary will equal xfersize parameter: ")
        if align:
            io_config += ',align=' + str(align)
    io_config += '\n'

    command = 'multipath -ll | grep "status=active\|status=enabled" -A 1 -B 2 | xargs | sed -e \'s/--/.\\n/g\' | ' \
              'awk \'{print $1}\''
    stdin, stdout, stderr = client.exec_command(command)
    vol_id_list = stdout.readlines() + stderr.readlines()
    #   vol_id_list = list(map(str.strip, vol_id_list))
    vol_id_list = [vol_id.strip() for vol_id in vol_id_list]

    for thread, vol_id in enumerate(vol_id_list, 1):
        io_config += 'sd=sd' + str(thread) + ',lun=/dev/mapper/' + str(vol_id) + '\n'

    print('#### Workload Definition parameter:')
    wd_param = ''
    rrio = input("Random Read I/O (type 'yes' if necessary): ")
    if rrio == "yes":
        wd_param += wd_spec("RR")
    rwio = input("Random Write I/O (type 'yes' if necessary): ")
    if rwio == "yes":
        wd_param += wd_spec("RW")
    srio = input("Sequential Read I/O (type 'yes' if necessary): ")
    if srio == "yes":
        wd_param += wd_spec("SR")
    swio = input("Sequential Write I/O (type 'yes' if necessary): ")
    if swio == "yes":
        wd_param += wd_spec("SW")

    if not wd_param:
        print("You don't select any workload definition")
        sys.exit(1)

    io_config += wd_param

    print('#### Run Definition parameter:')
    io_config += 'rd=IOWG1,wd=*'
    iorate = io_spec("---- IO rates to be generated (iorate)\n"
                     "   Appropriate options:\n"
                     "     100 : Run a workload of 100 I/Os per second\n"
                     "     100,200,… : Run a workload of 100 I/Os per second, then 200, etc\n"
                     "     curve : Run a performance curve\n"
                     "     max': Run the maximum I/O rate possible\n"
                     "   Enter IO rate: ", mandatory=True)
    io_config += ',iorate=(' + str(iorate) + ')'

    elapsed = io_spec("---- Elapsed Time (elapsed)\n"
                      "   Specifies the elapsed time in seconds for each run.\n"
                      "   This value needs to be at least twice the value of the reporting "
                      "interval below: ", mandatory=True)
    io_config += ',elapsed=' + str(elapsed)

    interal = io_spec("---- Reporting Interval (interal)\n"
                    "   Specifies the duration in seconds for each reporting interval: ", mandatory=True)
    io_config += ',interval=' + str(interal) + ',forthreads=' + str(thread) + '\n'

    dir = '/root/'
    sftp = client.open_sftp()
    file_sd = sftp.open(dir + 'io_config.txt', 'w')
    file_sd.write(io_config)
    file_sd.close()

    command1 = 'screen -L -dmS vdbench_1'
    stdin, stdout, stderr = client.exec_command(command=command1)
    stdout.read()
    command2 = 'screen -S vdbench_1 -p 0 -X stuff ' + '\'vdbench -f /root/io_config.txt' + '\'' + '$(echo -ne ' + '\'\\015\')'
    stdin, stdout, stderr = client.exec_command(command=command2)
    stdout.read()
    print("One screen session 'vdbench_1' was run on host ", host)
    print("Result in: /root/output")

    client.close()
