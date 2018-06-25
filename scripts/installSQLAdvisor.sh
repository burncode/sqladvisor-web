#!/bin/bash
# Filename: installSQLAdvisor.sh
# Author: zhoubangjun
# Date: 2017-06-24
# Description: 安装 SQLAdvisor
# Note: 以下安装步骤来自https://github.com/Meituan-Dianping/SQLAdvisor/blob/master/doc/QUICK_START.md

clone_repo(){
    cd /tmp
    [ -d SQLAdvisor ] && rm -rf SQLAdvisor
    git clone https://github.com/Meituan-Dianping/SQLAdvisor.git
    [ $? -ne 0 ] && exit 1
}

install_dep(){
    yum install gcc gcc-c++ make cmake libaio-devel libffi-devel glib2 glib2-devel -y
    yum install http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm -y
    yum-config-manager --enable=percona-release
    yum install Percona-Server-shared-56 -y
    cd /usr/lib64/
    ln -sf libperconaserverclient_r.so.18 libperconaserverclient_r.so
}

make_sqlparse(){
    [ -d /tmp/SQLAdvisor ]  && cd /tmp/SQLAdvisor
    cmake -DBUILD_CONFIG=mysql_release -DCMAKE_BUILD_TYPE=debug -DCMAKE_INSTALL_PREFIX=/usr/local/sqlparser ./
    make && make install
    [ $? -ne 0 ] && echo "sqlparser安装失败" && exit 1

}

install_sqladvisor(){
    cd sqladvisor
    cmake -DCMAKE_BUILD_TYPE=debug ./
    make
    if [ $? -ne 0 ]
    then
        echo "sqladvisor编译错误"
        exit 1
    else
        cp sqladvisor /usr/local/sqlparser/bin/
        ln -sf /usr/local/sqlparser/bin/sqladvisor /bin/
        echo "sqladvisor安装成功"
    fi
}

main(){
    clone_repo
    install_dep
    make_sqlparse
    install_sqladvisor
}

main $*


