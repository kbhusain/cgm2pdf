#!/bin/bash

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
/enod/support/LDP/users/scripts/setdisplay.sh ${HOST} 

#/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/apps/glicense/glm_app.py -display ${DISPLAY}
#/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/RAPID/bin/pLogApplication.py LICENSEMGR $USER CLOSE
# /peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/apps/cnvCGM/p_cgm_gui.py -display ${DISPLAY}

/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/apps/cnvCGM/p_cgm_gui.py 
