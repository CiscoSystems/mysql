MYSQL="mysql -uroot -p`cat /var/lib/juju/mysql.passwd`"
monitor_user=monitors
. /usr/share/charm-helper/sh/net.sh
remote_addr=$(ch_get_ip $(relation-get private-address))
mkdir -p data
revoke_todo=data/${JUJU_RELATION_ID}
