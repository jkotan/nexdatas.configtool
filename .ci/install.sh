#!/usr/bin/env bash

echo "restart mysql service"
if [ "$1" = "debian11" ] || [ "$1" = "debian12" ] || [ "$1" = "ubuntu24.04" ]; then
    docker exec --user root ndts service mariadb restart
else
    # workaround for a bug in debian9, i.e. starting mysql hangs
    docker exec --user root ndts service mysql stop
    if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu22.04" ] ; then
	docker exec --user root ndts /bin/bash -c 'usermod -d /var/lib/mysql/ mysql'
    fi
    # docker exec  --user root ndts /bin/bash -c '$(service mysql start &) && sleep 30'
    docker exec --user root ndts service mysql start
fi

echo "install tango-common"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive; apt-get -qq install -y tango-common; sleep 10'
if  [ "$1" = "ubuntu24.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /var/lib/tango/.my.cnf'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"%" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"localhost" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
fi
if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu21.10" ] || [ "$1" = "ubuntu22.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=127.0.0.1\npassword=rootpw" > /var/lib/tango/.my.cnf'
fi
echo "install tango-db"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive; apt-get -qq install -y tango-db; sleep 10'
if [ "$?" -ne "0" ]; then exit 255; fi
if  [ "$1" = "ubuntu24.04" ]; then
    docker exec  --user tango ndts /usr/bin/mysql -e 'create database tango'
    docker exec  --user tango ndts /bin/bash -c '/usr/bin/mysql tango < /usr/share/dbconfig-common/data/tango-db/install/mysql'
fi

docker exec  --user root ndts service tango-db restart


echo "install tango servers"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive;  apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java'
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec --user root ndts service tango-starter restart

docker exec  --user root ndts chown -R tango:tango .


docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y xvfb  libxcb1 libx11-xcb1 libxcb-keysyms1 libxcb-image0 libxcb-icccm4 libxcb-render-util0 xkb-data'
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec  --user root ndts mkdir -p /tmp/runtime-tango
docker exec  --user root ndts chown -R tango:tango /tmp/runtime-tango

echo "install tango servers"
docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update;  apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java pyqt5-dev-tools'
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec  --user root ndts service tango-starter restart

if [ "$?" -ne "0" ]; then exit -1; fi
echo "start Xvfb :99 -screen 0 1024x768x24 &"
docker exec  --user root ndts /bin/bash -c 'export DISPLAY=":99.0"; Xvfb :99 -screen 0 1024x768x24 &'
if [ "$?" -ne "0" ]; then exit 255; fi

echo "install python-pytango"
docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y'
if [ "$?" -ne "0" ]; then exit 255; fi




if [ "$2" = "2" ]; then
    echo "install pytango and nxsconfigserver-db"
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y   python-pytango  nxsconfigserver-db ; sleep 10'
else
    if [ "$1" = "debian10" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu22.04" ] || [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "debian11" ] || [ "$1" = "debian12" ] ; then
	echo "install pytango"
	docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y   python3-tango'
	echo "install nxsconfigserver-db"
	docker exec --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get  install -y   nxsconfigserver-db'
	if [ "$1" = "ubuntu24.04" ]; then
	    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"%" identified by "rootpw"'
	    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"localhost" identified by "rootpw"'
	    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
	    docker exec  --user tango ndts /usr/bin/mysql -e 'create database nxsconfig'
	    docker exec  --user tango ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; /usr/bin/mysql nxsconfig < /usr/share/dbconfig-common/data/nxsconfigserver-db/install/mysql'
	fi
    else
	echo "install pytango and nxsconfigserver-db"
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y   python3-pytango nxsconfigserver-db; sleep 10'
    fi
fi
if [ "$?" != "0" ]; then exit 255; fi


echo "install nxs packages"
if [ "$2" = "2" ]; then
    echo "install python-pytango"
    docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y python-nxsconfigserver python-nxswriter python-pyqt5  python-nxstools  python-setuptools; sleep 10'
else
    docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y python3-nxsconfigserver python3-nxswriter s python3-pyqt5  python3-nxstools python3-setuptools; sleep 10'
fi
if [ "$?" != "0" ]; then exit 255; fi

if [ "$2" = "2" ]; then
    echo "install nxsconfigtool"
    docker exec --user root ndts chown -R tango:tango .
    docker exec  ndts python setup.py build
    docker exec --user root ndts python setup.py  install
else
    echo "install nxsconfigtool3"
    docker exec --user root ndts chown -R tango:tango .
    docker exec  ndts python3 setup.py build
    docker exec --user root ndts python3 setup.py  install
fi
if [ "$?" -ne "0" ]; then exit 255; fi
