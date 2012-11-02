# vim: syntax=python

import os
import sys
import MySQLdb
import subprocess
import uuid

def get_service_user_file(service):
    return '/var/lib/juju/%s.service_user2' % service


def get_service_user(service):
    if service == '':
        return (None, None)
    sfile = get_service_user_file(service)
    if os.path.exists(sfile):
        with open(sfile, 'r') as f:
            return (f.readline().strip(), f.readline().strip())
    (suser, service_password) = subprocess.check_output(['pwgen', '-N 2', '15']).strip().split("\n")
    with open(sfile, 'w') as f:
        f.write("%s\n" % suser)
        f.write("%s\n" % service_password)
        f.flush()
    return (suser, service_password)


def cleanup_service_user(service):
    os.unlink(get_service_user_file(service))


relation_id = os.environ.get('JUJU_RELATION_ID')
change_unit = os.environ.get('JUJU_REMOTE_UNIT')

# We'll name the database the same as the service.
database_name_file = '.%s_database_name' % (relation_id)
# change_unit will be None on broken hooks
database_name = ''
if change_unit:
    database_name, _ = change_unit.split("/")
    with open(database_name_file, 'w') as dbnf:
        dbnf.write("%s\n" % database_name)
        dbnf.flush()
elif os.path.exists(database_name_file):
    with open(database_name_file, 'r') as dbname:
        database_name = dbname.readline().strip()
else:
    print 'No established database and no REMOTE_UNIT.'
# A user per service unit so we can deny access quickly
user, service_password = get_service_user(database_name)
connection = None
lastrun_path = '/var/lib/juju/%s.%s.lastrun' % (database_name,user)
slave_configured_path = '/var/lib/juju.slave.configured.for.%s' % database_name
slave_configured = os.path.exists(slave_configured_path)
slave = os.path.exists('/var/lib/juju/i.am.a.slave')
broken_path = '/var/lib/juju/%s.mysql.broken' % database_name
broken = os.path.exists(broken_path)

def get_db_cursor():
    # Connect to mysql
    passwd = open("/var/lib/juju/mysql.passwd").read().strip()
    print passwd
    connection = MySQLdb.connect(user="root", host="localhost", passwd=passwd)

    return connection.cursor()

