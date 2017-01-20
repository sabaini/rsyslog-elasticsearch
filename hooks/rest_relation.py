#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))

from charmhelpers.core import hookenv, host
from charmhelpers.core.hookenv import relations_of_type

from charmhelpers.core.templating import render

hooks = hookenv.Hooks()

RSYSLOGCONF='/etc/rsyslog.d/rsyslog-elasticsearch.conf'

def get_rel_hosts():
    relation_data = relations_of_type('rest')
    if relation_data is None or len(relation_data) == 0:
        hookenv.log("No relation data, exiting.")
        return []
    hosts = [ unit_data['private-address'] for unit_data in relation_data ]
    return hosts

def update_config(hosts):
    ## rsyslog omelastic issue with more than one ES server
    # elasticsearch = ', '.join(['"{}"'.format(s) for s in hosts])
    elasticsearch = '"{}"'.format(hosts[0])
    render("rsyslog-elasticsearch.conf", RSYSLOGCONF,
           { 'elasticsearch': elasticsearch} )

@hooks.hook('rest-relation-joined', 'rest-relation-changed')
def rest_relation():
    hosts = get_rel_hosts()
    hookenv.log('Elasticsearch relation present for %s, install config' % hosts)
    update_config(hosts)
    host.service_restart('rsyslog')    
    
@hooks.hook('rest-relation-departed', 'rest-relation-broken')
def rest_relation_gone():
    hosts = get_rel_hosts()
    if hosts:
        update_config(hosts)        
        host.service_restart('rsyslog')    
    else:
        hookenv.log('Elasticsearch relation no longer present, remove config')
        try:
            os.unlink(RSYSLOGCONF)
        except OSError:
            pass
    host.service_restart('rsyslog')

if __name__ == '__main__':
    hooks.execute(sys.argv)

    
