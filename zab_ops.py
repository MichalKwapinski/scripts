
# Import libraries
import sys, getopt
from pyzabbix import ZabbixAPI


# Data to access Zabbix server
ZABBIX_SERVER = 'http://zabbix-ip/zabbix'
USER_NAME = 'admin_user'
PASS = 'admin_pass'


# Make a connection
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(USER_NAME, PASS)


# Functions
def print_usage():
    print ''
    print '     Usage: python zab_ops.py [OPTION]...'
    print '     Zabbix operations'
    print ''
    print '     -h, --help			print this output'
    print '     -l, --list=ITEM			list mode ITEM in (host,group,template)'
    print '     -a, --add=ITEM			add mode ITEM in (host)'
    print '     -d, --del=ITEM			del mode ITEM in (host)'
    print '     -g, --group=GROUP_NAME		group name for list and adding options'
    print '     -t, --template=TEMPLATE_NAME	template name for list and adding options'
    print '     -n, --host-name=HOST_NAME	host name for adding hosts'
    print '     -i, --ip=IP_ADDRESS		ip addres for adding hosts'


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

def get_host_id(hostname):
    for h in zapi.host.get(output='extend'):
        if h['name'] == hostname:
            host_id = h['hostid']

    return host_id


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


# Lsting hosts by group
def list_hosts_by_group(line_attr):
    if line_attr not in list_all_hostgroups():
        print "WRONG GROUP NAME!. Possible groups: "
        print list_all_hostgroups()
        sys.exit(2)
    else:
        hostgroup_id = get_hostgroup_id(line_attr)

        # Get a list of all hosts from the group
        hosts = zapi.host.get(groupids=hostgroup_id,
                              monitored_hosts=1,
                              output='extend')

        # Print the list
        print 'Hosts from group ' + line_attr

        for h in hosts:
            print ("{0} {1}".format(h['host'].encode('UTF-8'),
                   h['name'].encode('UTF-8')))


# Listing hosts by template
def list_hosts_by_template(line_attr):
    if line_attr not in list_all_templates():
        print "WRONG TEMPLATE NAME!. Possible templates: "
        print list_all_templates()
        sys.exit(2)
    else:
        template_id = get_template_id(line_attr)

        # Get a list of all hosts from the template
        hosts = zapi.host.get(templateids=template_id,
                              monitored_hosts=1,
                              output='extend')

        # Print the list
        print 'Hosts from template ' + line_attr

        for h in hosts:
            print ("{0} {1}".format(h['host'].encode('UTF-8'),
                   h['name'].encode('UTF-8')))


def add_host(host_name,ip_addr,group,template):
    if group not in list_all_hostgroups():
        print "WRONG GROUP NAME!. Possible groups: "
        print list_all_hostgroups()
        sys.exit(2)
    elif template not in list_all_templates():
        print "WRONG TEMPLATE NAME!. Possible templates: "
        print list_all_templates()
        sys.exit(2)
    else:
        group_id = get_hostgroup_id(group)
        template_id = get_template_id(template)
        zapi.host.create({ 'host': host_name, 'groups' : [{'groupid' : int(group_id)}], 'templates' : [{'templateid' : int(template_id)}], 
                        'interfaces' : [ { 'type' : 1, 'main' : 1, 'useip' : 1, 'ip' : ip_addr, 'dns' : host_name, 'port' : '10050'}, 
                                         { 'type' : 2, 'main' : 1, 'useip' : 1, 'ip' : ip_addr, 'dns' : '', 'port' : '161'} ] 
                        })


def del_host(host_name):
    host_id = get_host_id(host_name)

    print 'Removing host: ' + host_name 
    print 'host_id: ' + host_id 
    
    zapi.host.delete(host_id)


def main(argv):
    _list_mode = ''
    _add_mode = ''
    _del_mode = ''
    _group_name = ''
    _template_name = ''
    _ip_addr = ''
    _host_name = ''

    try:
        opts, args = getopt.getopt(argv,'hl:a:d:g:t:n:i:',['help','list=','add=','del=','group=','template=','host-name=','ip='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
            sys.exit()
        elif opt in ('-l', '--list'):
            if arg in ('host'):
                _list_mode = arg
            elif arg in ('group'):
                _list_mode = arg
            elif arg in ('template'):
                _list_mode = arg
            else:
                print_usage()
                sys.exit()
        elif opt in ('-a', '--add'):
            if arg in ('host'):
                _add_mode = arg
            else:
                print_usage()
                sys.exit()
        elif opt in ('-d', '--del'):
            if arg in ('host'):
                _del_mode = arg
            else:
                print_usage()
                sys.exit()
        elif (opt in ('-g', '--group') and (_list_mode == 'host' or _add_mode == 'host')):
            _group_name = arg
        elif (opt in ('-t', '--template') and (_list_mode == 'host' or _add_mode == 'host' )):
            _template_name = arg
        elif (opt in ('-i', '--ip')):
            _ip_addr = arg
        elif (opt in ('-n', '--host-name')):
            _host_name = arg


    if _list_mode == 'group':
         print list_all_hostgroups()
    elif _list_mode == 'template':
         print list_all_templates()
    elif (_list_mode == 'host' and _group_name):
        list_hosts_by_group(_group_name)
    elif (_list_mode == 'host' and _template_name):
        list_hosts_by_template(_template_name)
    elif (_add_mode == 'host' and _host_name and _ip_addr and _group_name and _template_name):
        add_host(_host_name,_ip_addr,_group_name,_template_name)
    elif (_del_mode == 'host' and _host_name):
        del_host(_host_name)


if __name__ == "__main__":
   main(sys.argv[1:])
