# vim: syntax=python

import os
import MySQLdb
import subprocess

try:
    change_unit = os.environ['ENSEMBLE_REMOTE_UNIT']
except KeyError:
    pass

if len(change_unit) == 0:
    # XXX hack to work around https://launchpad.net/bugs/791042
    change_unit  = subprocess.check_output(['relation-list']).strip().split("\n")[0]

# We'll name the database the same as the service.
database_name, _ = change_unit.split("/")
# A user per service unit so we can deny access quickly
user = change_unit.split("/")[0]
connection = None
lastrun_path = '/var/lib/ensemble/%s.%s.lastrun' % (database_name,user)
slave_configured_path = '/var/lib/ensemble.slave.configured.for.%s' % database_name
slave_configured = os.path.exists(slave_configured_path)
slave = os.path.exists('/var/lib/ensemble/i.am.a.slave')
broken_path = '/var/lib/ensemble/%s.mysql.broken' % database_name
broken = os.path.exists(broken_path)

def get_db_cursor():
    # Connect to mysql
    passwd = open("/var/lib/ensemble/mysql.passwd").read().strip()
    print passwd
    connection = MySQLdb.connect(user="root", host="localhost", passwd=passwd)

    return connection.cursor()

