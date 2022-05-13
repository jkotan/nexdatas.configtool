#!/usr/bin/env bash

# workaround for a bug in debian9, i.e. starting mysql hangs
if [ "$1" = "debian11" ]; then
    docker exec --user root ndts service mariadb restart
else
    docker exec --user root ndts service mysql stop
    if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu22.04" ]; then
	docker exec --user root ndts /bin/bash -c 'usermod -d /var/lib/mysql/ mysql'
    fi
    docker exec --user root ndts service mysql start
    # docker exec  --user root ndts /bin/bash -c '$(service mysql start &) && sleep 30'
fi

docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   tango-db tango-common; sleep 10'
if [ "$?" -ne "0" ]; then exit 255; fi
if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu21.10" ] || [ "$1" = "ubuntu22.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=127.0.0.1\npassword=rootpw" > /var/lib/tango/.my.cnf'
fi
docker exec  --user root ndts service tango-db restart

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
    echo "install python packages"
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y  python-pytango   nxsconfigserver-db; sleep 10; apt-get -qq install -y   python-nxsconfigserver python-nxstools python-pyqt5 python-setuptools'
else
    echo "install python3 packages"
    if [ "$1" = "ubuntu22.04" ] || [ "$1" = "ubuntu20.04" ] || [ "$1" = "debian10" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "debian11" ]; then
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-tango   nxsconfigserver-db; sleep 10; apt-get -qq install -y   python3-nxsconfigserver python3-nxstools python3-pyqt5 python3-setuptools'
    else
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-pytango   nxsconfigserver-db; sleep 10; apt-get -qq install -y   python3-nxsconfigserver python3-nxstools python3-pyqt5 python3-setuptools'
    fi
fi
if [ "$?" -ne "0" ]; then exit 255; fi

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
