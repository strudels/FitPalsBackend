#!/bin/bash
#Tigase server must be reset after tigase database has been reset
MUSER="tigase"
MDB="tigasedb"
MHOST="192.168.1.12"
 
# Detect paths
MYSQL=$(which mysql)
AWK=$(which awk)
GREP=$(which grep)

read -s -p "Password for database: " MPASS
echo
 
TABLES=$($MYSQL -u $MUSER -p$MPASS -h $MHOST $MDB -e 'show tables' | $AWK '{ print $1}' | $GREP -v '^Tables' )
 
for t in $TABLES
do
	echo "Deleting $t table from $MDB database..."
	$MYSQL -u $MUSER -h $MHOST -p$MPASS $MDB -e "drop table $t"
done

mysql -u $MUSER -h $MHOST -p$MPASS $MDB < database/mysql-schema-5-1.sql
mysql -u $MUSER -h $MHOST -p$MPASS $MDB < jabber_msg_trigger.sql
echo "Now go reset the Tigase Server!"
