#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render

hooks = hookenv.Hooks()

RSYSLOGCONF='/etc/rsyslog.d/rsyslog-elasticsearch.conf'

@hooks.hook('rest-relation-joined', 'rest-relation-changed')
def rest_relation():
    elasticsearch = hookenv.relation_get(attribute='private-address')
    hookenv.log('Elasticsearch relation present for %s, install config' % elasticsearch)
    render("rsyslog-elasticsearch.conf", RSYSLOGCONF,
           { 'elasticsearch': elasticsearch} )
    host.service_restart('rsyslog')
    
@hooks.hook('rest-relation-departed', 'rest-relation-broken')
def rest_relation_gone():
    hookenv.log('Elasticsearch relation no longer present, remove config')
    try:
        os.unlink(RSYSLOGCONF)
    except OSError:
        pass
    host.service_restart('rsyslog')

if __name__ == '__main__':
    hooks.execute(sys.argv)

    
