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


def install():
    ceph_dir = "/etc/ceph"
    if not os.path.isdir(ceph_dir):
        os.mkdir(ceph_dir)
    utils.install('ceph-common')


def create_image(service, image, sizemb):
    cmd = [
        'rbd',
        'create',
        image,
        '--size',
        sizemb,
        '--id',
        service,
        '--pool',
        'images'
        ]
    execute(cmd)


def create_image_pool(service):
    cmd = [
        'rados',
        '--id',
        service,
        'mkpool',
        'images'
        ]
    execute(cmd)


def create_keyring(service, keyring, key):
    cmd = [
        'ceph-authtool',
        keyring,
        '--create-keyring',
        '--name=client.%s' % service,
        '--add-key=%s' % key
        ]
    execute(cmd)


def map_block_storage(service, image, keyfile):
    cmd = [
        'rbd',
        'map',
        'images/%s' % image,
        '--user',
        service,
        '--secret',
        keyfile,
        ]
    execute(cmd)


def make_filesystem(service, blk_device, fstype='ext4'):
    cmd = ['mkfs', '-t', fstype, blk_device]
    execute(cmd)


def place_data_on_ceph(service, blk_device, data_src_dst, fstype='ext4'):
    # mount block device into /mnt
    cmd = ['mount', '-t', fstype, blk_device, '/mnt']
    execute(cmd)

    # copy data to /mnt
    try:
        copy_files(data_src_dst, '/mnt')
    except:
        pass

    # umount block device
    cmd = ['umount', '/mnt']
    execute(cmd)

    # re-mount where the data should originally be
    cmd = ['mount', '-t', fstype, blk_device, data_src_dst]
    execute(cmd)


# TODO: re-use
def modprobe_kernel_module(module):
    cmd = ['modprobe', module]
    execute(cmd)
    cmd = 'echo %s >> /etc/modules' % module
    execute_shell(cmd)


def copy_files(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
