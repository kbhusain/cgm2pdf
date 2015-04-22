#!/bin/bash

/peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/geolog/data/GOZ_QUICKLOOK/NRTP/engine/bin/pLogApplication.py LICENSEMGR $USER INIT
cd /peasd/fesg/users/husainkb/nrtp/gl671/glicense


source /peasd/geolog/RAPID/bin/usep.bash 

#rsh lnx_eob_7w102 /peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/fesg/users/husainkb/nrtp/gl671/glicense/glm_app.py -display ${HOST}${DISPLAY}
#rsh lnx_eob_7w102 /peasd/fesg/users/husainkb/lnx/usr/local/bin/python /peasd/fesg/users/husainkb/nrtp/gl671/glicense/glm_app.py -display ${DISPLAY}
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

# /usr/bin/rsvg-view $1 
/peasd/fesg/users/husainkb/lnx/usr/local/bin/display $1 

