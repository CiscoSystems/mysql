import utils
import commands
import re
import subprocess
import sys
import os
import shutil


def execute(cmd):
    subprocess.check_call(cmd)


def execute_shell(cmd):
    subprocess.check_call(cmd, shell=True)


def prepare_drbd_disk(block_device=None):
    if block_device is None:
        sys.exit(1)

    cmd = 'dd if=/dev/zero of=%s bs=512 count=1 oflag=direct >/dev/null' % block_device
    execute_shell(cmd)
    cmd = '(echo n; echo p; echo 1; echo ; echo; echo w) | fdisk %s' % block_device
    execute_shell(cmd)


def modprobe_module():
    cmd = ['modprobe', 'drbd']
    execute(cmd)
    cmd = 'echo drbd >> /etc/modules'
    execute_shell(cmd)


def create_md(resource):
    cmd = ['drbdadm', '--', '--force', 'create-md', resource]
    execute(cmd)


def bring_resource_up(resource):
    cmd = ['drbdadm', 'up', resource]
    execute(cmd)


def clear_bitmap(resource):
    cmd = ['drbdadm', '--', '--clear-bitmap', 'new-current-uuid', resource]
    execute(cmd)


def make_primary(resource):
    cmd = ['drbdadm', 'primary', resource]
    execute(cmd)


def make_secondary(resource):
    cmd = ['drbdadm', 'secondary', resource]
    execute(cmd)


def format_drbd_device():
    cmd = ['mkfs', '-t', 'ext3', '/dev/drbd0']
    execute(cmd)


def is_connected():
    (status, output) = commands.getstatusoutput("drbd-overview")
    show_re = re.compile("0:export  Connected")
    quorum = show_re.search(output)
    if quorum:
        return True
    return False


def is_quorum_secondary():
    (status, output) = commands.getstatusoutput("drbd-overview")
    show_re = re.compile("Secondary/Secondary")
    quorum = show_re.search(output)
    if quorum:
        return True
    return False


def is_quorum_primary():
    (status, output) = commands.getstatusoutput("drbd-overview")
    show_re = re.compile("Primary/Secondary")
    quorum = show_re.search(output)
    if quorum:
        return True
    return False


def is_state_inconsistent():
    (status, output) = commands.getstatusoutput("drbd-overview")
    show_re = re.compile("Inconsistent/Inconsistent")
    quorum = show_re.search(output)
    if quorum:
        return True
    return False


def is_state_uptodate():
    (status, output) = commands.getstatusoutput("drbd-overview")
    show_re = re.compile("UpToDate/UpToDate")
    quorum = show_re.search(output)
    if quorum:
        return True
    return False


def copy_files(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def put_on_drbd():
    cmd = ['mount', '-t', 'ext3', '/dev/drbd0', '/mnt']
    execute(cmd)
    # TODO: Before copying make sure it is mounted.
    copy_files('/var/lib/mysql','/mnt')
    cmd = ['chown', '-R', 'mysql:mysql', '/mnt']
    execute(cmd)
    cmd = ['umount', '/mnt']
    execute(cmd)
    cmd = ['mount', '-t', 'ext3', '/dev/drbd0', '/var/lib/mysql']
    execute(cmd)
