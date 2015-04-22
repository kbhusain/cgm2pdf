#!/bin/bash

stty sane
export PATH=/peasd/fesg/users/husainkb/jre1.6.0_17/bin:/peasd/fesg/users/husainkb/firefox/:/peasd/fesg/users/husainkb/lnx/usr/local/bin:${PATH}:/usr/bin
export PYTHONPATH=/peasd/fesg/users/husainkb/lnx/usr/local/lib
export JAVA_HOME=/peasd/fesg/users/husainkb/jre1.6.0_17/
export LD_LIBRARY_PATH=/peasd/fesg/users/husainkb/jre1.6.0_17/lib:/peasd/fesg/users/husainkb/firefox/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/peasd/fesg/users/husainkb/lnx/usr/local/lib64:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/peasd/fesg/users/husainkb/lnx/usr/local/lib:$LD_LIBRARY_PATH
export LD_RUN_PATH=$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/peasd/fesg/users/husainkb/lnx/usr/local/lib/pkgconfig
export EDITOR=/usr/bin/vim
export CLASSPATH=/peasd/fesg/users/husainkb/eclipse-jee-indigo-SR2-linux-gtk-x86_64/jdk1.7.0_03/bin
export PATH=/peasd/fesg/users/husainkb/eclipse-jee-indigo-SR2-linux-gtk-x86_64/jdk1.7.0_03/bin:$PATH
export DVPATH=/peasd/fesg/users/husainkb/lnx/
export EPATH=/peasd/fesg/users/husainkb/eclipse-jee-indigo-SR2-linux-gtk-x86_64/jdk1.7.0_03/
export WSPACE=/peasd/fesg/users/husainkb/wspace
export LD_LIBRARY_PATH=/peasd/fesg/users/husainkb/lnx/usr/local/lib/vtk-5.10/:$LD_LIBRARY_PATH


#---------------------------------- ORACLE--------------------------------------
export ORACLE_HOME=/ep/appl01/ep/orabase_lnx/ora11gr2_64_lnx
#export ORACLE_HOME=/ep/appl01/ep/orabase_lnx/ora10gr2_64_lnx
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
export PATH=$ORACLE_HOME/bin:$PATH
export CLASSPATH=$ORACLE_HOME:$CLASSPATH
export TNS_ADMIN=/ep/appl01/ep/tns_admin
export SQLPATH=/ep/appl01/ep/scripts/sql
alias vm=/usr/bin/vim


export QTDIR=/usr/lib64/qt4
export QTINC=/usr/lib64/qt4/include
export QTLIB=/usr/lib64/qt4/lib



/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/data/GOZ_QUICKLOOK/NRTP/engine/bin/pLogApplication.py LICENSEMGR $USER INIT
cd /peasd/geolog/apps/cnvCGM/

if [ $DISPLAY == ":0" ]
then
        export DISPLAY=${HOST}:0.0
        echo "2. I am now using $DISPLAY on $HOST "
fi

if [ $DISPLAY == "" ]
then
        export DISPLAY=${HOST}:0
fi
# /enod/support/LDP/users/scripts/setdisplay.sh ${HOST} 

#/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/apps/glicense/glm_app.py -display ${DISPLAY}
#/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/RAPID/bin/pLogApplication.py LICENSEMGR $USER CLOSE
# /peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/apps/cnvCGM/p_cgm_gui.py -display ${DISPLAY}

/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/apps/cnvCGM/p_cgm_gui.py 
