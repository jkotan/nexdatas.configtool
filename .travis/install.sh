#!/usr/bin/env bash

# workaround for incomatibility of default ubuntu 16.04 and tango configuration
if [ $1 = "ubuntu16.04" ]; then
    docker exec -it --user root ndts sed -i "s/\[mysqld\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION/g" /etc/mysql/mysql.conf.d/mysqld.cnf
fi

# workaround for a bug in debian9, i.e. starting mysql hangs
docker exec -it --user root ndts service mysql stop
docker exec -it --user root ndts /bin/sh -c '$(service mysql start &) && sleep 30'

docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   tango-db tango-common; sleep 10'
if [ $? -ne "0" ]
then
    exit -1
fi
echo "install tango servers"
docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update;  apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java pyqt5-dev-tools'
if [ $? -ne "0" ]
then
    exit -1
fi

docker exec -it --user root ndts service tango-db restart
docker exec -it --user root ndts service tango-starter restart


echo "install python-pytango"
docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y'
if [ $? -ne "0" ]
then
    exit -1
fi


if [ $2 = "2" ]; then
    echo "install python packages"
    docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y  python-pytango   nxsconfigserver-db; sleep 10; apt-get -qq install -y   python-nxsconfigserver python-nxstools python-pyqt5 python-setuptools'
else
    echo "install python3 packages"
    docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-pytango   nxsconfigserver-db; sleep 10; apt-get -qq install -y   python3-nxsconfigserver python3-nxstools python3-pyqt5 python3-setuptools'
fi
if [ $? -ne "0" ]
then
    exit -1
fi

if [ $2 = "2" ]; then
    echo "install nxsconfigtool"
    docker exec -it --user root ndts python setup.py -q install
else
    echo "install nxsconfigtool3"
    docker exec -it --user root ndts python3 setup.py -q install
fi
if [ $? -ne "0" ]
then
    exit -1
fi
