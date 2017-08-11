
# Import libraries
import sys, getopt
from pyzabbix import ZabbixAPI


# Data
ZABBIX_SERVER = 'http://zabbix-ip/zabbix'
USER_NAME = 'user'
PASS = 'pass'


# Make a connection
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(USER_NAME, PASS)


# Functions
def print_usage():
    print ''
    print '     Usage: python zab_ops.py [OPTION]...'
    print '     Zabbix operations'
    print ''
    print '     -h, --help                      print this output'
    print '     -a, --add=ITEM                  add mode ITEM in (host)'
    print '     -g, --group=GROUP_NAME          group name for list and adding options'
    print '     -t, --template=TEMPLATE_NAME    template name for list and adding options'
    print '     -n, --host-name=HOST_NAME       host name for adding hosts'
    print '     -i, --ip=IP_ADDRESS             ip addres for adding hosts'



def get_hostgroup_id(hostgroup_name):
    hostgroups = zapi.hostgroup.get(output='extend')

    # Get group ID
    for hg in hostgroups:
        if hg['name'] == hostgroup_name:
            hostgroup_id = hg['groupid']
            return hostgroup_id


def get_template_id(template_name):
    templates = zapi.template.get(output='extend')

    # Get template ID
    for tp in templates:
        if tp['name'] == template_name:
            template_id = tp['templateid']
            return template_id


def list_all_hostgroups():
    all_hostgroups = []
    for hg in zapi.hostgroup.get(output='extend'):
       all_hostgroups.append(hg['name'])
    return all_hostgroups


def list_all_templates():
    all_templates = []
    for tp in zapi.template.get(output='extend'):
       all_templates.append(tp['name'])
    return all_templates


def list_all_hosts():
    all_hosts = []
    for h in zapi.host.get(output='extend'):
       all_hosts.append(h['name'])
    return all_hosts


def add_host(host_name,ip_addr,group,template):
    if group not in list_all_hostgroups():
        print "WRONG GROUP NAME!. Possible groups: "
        print list_all_hostgroups()
        sys.exit(2)
    elif template not in list_all_templates():
        print "WRONG TEMPLATE NAME!. Possible templates: "
        print list_all_templates()
        sys.exit(2)
    elif host_name in list_all_hosts():
        print "Hostname already exits in Zabbix Server"
        sys.exit()
    else:
        group_id = get_hostgroup_id(group)
        template_id = get_template_id(template)
        zapi.host.create({ 'host': host_name, 'groups' : [{'groupid' : int(group_id)}], 'templates' : [{'templateid' : int(template_id)}],
                        'interfaces' : [ { 'type' : 1, 'main' : 1, 'useip' : 1, 'ip' : ip_addr, 'dns' : host_name, 'port' : '10050'}, 
                                         { 'type' : 2, 'main' : 1, 'useip' : 1, 'ip' : ip_addr, 'dns' : host_name, 'port' : '161'} ]})


def main(argv):
    _add_mode = ''
    _group_name = ''
    _template_name = ''
    _ip_addr = ''
    _host_name = ''

    try:
        opts, args = getopt.getopt(argv,'ha:g:t:n:i:',['help','add=','group=','template=','host-name=','ip='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
            sys.exit()
        elif opt in ('-a', '--add'):
            if arg in ('host'):
                _add_mode = arg
            else:
                print_usage()
                sys.exit()
        elif (opt in ('-g', '--group') and (_add_mode == 'host')):
            _group_name = arg
        elif (opt in ('-t', '--template') and (_add_mode == 'host')):
            _template_name = arg
        elif (opt in ('-i', '--ip')):
            _ip_addr = arg
        elif (opt in ('-n', '--host-name')):
            _host_name = arg

    if (_add_mode == 'host' and _host_name and _ip_addr and _group_name and _template_name):
        add_host(_host_name,_ip_addr,_group_name,_template_name)


if __name__ == "__main__":
   main(sys.argv[1:])
