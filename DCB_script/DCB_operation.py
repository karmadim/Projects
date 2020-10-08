import paramiko
import getpass
import operator
import sys


def volumes_lun_id():
    command = 'multipath -ll | grep "status=active\|status=enabled" -A 1 -B 2 | xargs | sed -e \'s/--/.\\n/g\' | ' \
              'awk \'{i = 1; if(NF > 0) do {if($i ~/.*[0-9]:.*[0-9]:.*[0-9]:.*[0-9]/) print $1, $i; i++;} while (i <= NF);}\''
    stdin, stdout, stderr = client.exec_command(command)
    command_res = stdout.readlines() + stderr.readlines()

    # create dictionary (key: Volume, value: LUN Id)
    lun_id = {}
    storage_volume = {}
    for item in command_res:
        item = item.rstrip()
        item = item.split(' ')
        lun_id[item[0]] = item[1].split(':')[3]
    if storage == "vplex":
        storage_volume = {k: v for k, v in lun_id.items() if k[0:4] == '3600'}
        print("Volumes with Lun id", storage_volume)
        return storage_volume
    if storage == "xio":
        storage_volume = {k: v for k, v in lun_id.items() if k[0:4] == '3514'}
        print("Volumes with Lun id", storage_volume)
        return storage_volume


def used_vol():
    # getting list of volumes already used in dcb
    volumes = []
    if storage == "xio":
        command = "ps aux | grep -E 'consist.*3514' | grep -v grep"
        stdin, stdout, stderr = client.exec_command(command)
        ps_aux_consist = stdout.readlines() + stderr.readlines()
        volumes = [y[y.find("3514"):(y.find("3514") + 17)] for y in ps_aux_consist]
    if storage == "vplex":
        command = "ps aux | grep -E 'consist.*3600' | grep -v grep"
        stdin, stdout, stderr = client.exec_command(command)
        ps_aux_consist = stdout.readlines() + stderr.readlines()
        volumes = [y[y.find("3600"):(y.find("3600") + 33)] for y in ps_aux_consist]
    return volumes


def run_dcb(operation):
    if operation == "start":
        if not vol_id:
            print("There are no free additional volumes for dcb process.")
            return
        for key, value in sorted(vol_id.items(), key=operator.itemgetter(1)):
            command1 = 'screen -L -dmS ' + 'dcb_' + storage + '_' + value
            stdin, stdout, stderr = client.exec_command(command=command1)
            command2 = 'screen -S ' + 'dcb_' + storage + '_' + value + ' -p 0 -X stuff ' + \
                       '\'consist -data /dev/mapper/' + key + ' -size 20 -name dcb_' + storage + '_' + value + \
                       ' -bg' + '\'' + '$(echo -ne ' + '\'\\015\')'
            stdin, stdout, stderr = client.exec_command(command=command2)
        print("Check new screen sessions and consist processes (wait until initialization takes place) on the host: ",
              host)

    if operation == "check" or operation == "pause" or operation == "resume" or operation == "stop":
        command = "consist -list | grep dcb_" + storage + " | awk '{print $1}'"
        stdin, stdout, stderr = client.exec_command(command)
        consist_list = stdout.readlines() + stderr.readlines()
        command1 = 'screen -L -dmS dcb_' + storage + '_' + operation
        print("One screen session (dcb_" + storage + "_" + operation + ") was created on host: ", host)
        stdin, stdout, stderr = client.exec_command(command=command1)
        for item in consist_list:
            item = item.rstrip()
            command2 = 'screen -S dcb_' + storage + '_' + operation + ' -p 0 -X stuff ' + '\'consist -name ' \
                       + item + ' -cmd ' + operation + ' | tee ' + item + '_' + operation + '.log' \
                       + '\'' + '$(echo -ne ' + '\'\\015\')'
            stdin, stdout, stderr = client.exec_command(command=command2)
            print("Check file in root user's home directory: ", item + "_" + operation + ".log")
            if operation == "stop":
                command3 = 'screen -S ' + item + ' -p 0 -X quit'
                stdin, stdout, stderr = client.exec_command(command3)

    if operation == "checkTarget":
        for key, value in sorted(vol_id.items(), key=operator.itemgetter(1)):
            command1 = 'screen -L -dmS dcb_' + storage + '_' + value
            stdin, stdout, stderr = client.exec_command(command=command1)
            command2 = 'screen -S dcb_' + storage + '_' + value + ' -p 0 -X stuff ' + '\'consist -data /dev/mapper/' + key \
                       + ' -check' + '\'' + '$(echo -ne ' + '\'\\015\')'
            stdin, stdout, stderr = client.exec_command(command=command2)
        print("Check new screen sessions on the host: ", host)


if __name__ == "__main__":
    host = input("Enter LG short name to collect volumes from: ") + ".xiodrm.lab.emc.com"
    #    host = input("Enter LG fqdn name to collect volumes from: ")
    #    host = 'lgdrm469.xiodrm.lab.emc.com'
    user = 'root'
    password = 'Password123!'
    #    password = getpass.getpass('Enter root password: ')
    port = 22

    dcb_current_status = None
    vol_rescan = None
    host_status = None

    storage = input("Volumes mapped to host from  (xio/vplex): ")
    dcb_operation = input("What dcb process is needed (start/check/pause/resume/stop): ")
    if dcb_operation == "start":
        dcb_current_status = input(
            "Is the DCB process already running on the volumes of the specified storage? (yes/no): ")
    if dcb_operation == "check":
        host_status = input("Is this host source or target (source/target): ")

    if dcb_operation == "start" or dcb_operation == "check" and host_status == "target":
        vol_rescan = input("Do you want to rescan devices on the host (yes/no): ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to ssh host {} ...'.format(host))
    try:
        client.connect(hostname=host,
                       username=user,
                       password=password,
                       port=port,
                       look_for_keys=False,
                       allow_agent=False)
    except Exception as e:
        print('*** Failed to connect to {}: {}'.format(host, e))
        sys.exit(1)

    if vol_rescan == "yes":
        print('### Rescanning host for volumes...')
        command = '/home/qa/util-scripts/fast_rescan_luns.py'
        stdin, stdout, stderr = client.exec_command(command)
        command_res = stdout.readlines() + stderr.readlines()
        print("Scanning result: ", command_res)

    if dcb_operation == "start":
        vol_id = volumes_lun_id()
        if dcb_current_status == "no":
            run_dcb("start")
        if dcb_current_status == "yes":
            used_volumes = used_vol()
            for vol in used_volumes:
                vol_id.pop(vol)
            run_dcb("start")

    if dcb_operation == "check":
        if host_status == "source": run_dcb("check")
        if host_status == "target":
            vol_id = volumes_lun_id()
            run_dcb("checkTarget")

    if dcb_operation == "pause": run_dcb("pause")
    if dcb_operation == "resume": run_dcb("resume")
    if dcb_operation == "stop": run_dcb("stop")

    client.close()
