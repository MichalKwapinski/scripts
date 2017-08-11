node['zabbix']['agent']['packages'].each do |packages_to_install|
  package packages_to_install do
    action :install
  end
end

zabbix_server_ip = node['zabbix']['server']['ip']

zabbix_agent_hostname = node['hostname']

template "/etc/zabbix/zabbix_agentd.conf" do
  source "zabbix_agentd.conf.erb"
  owner "root"
  group "root"
  mode "0644"
  variables( :zabbix_agent_hostname => zabbix_agent_hostname, :zabbix_server_ip => zabbix_server_ip )
end

service "zabbix-agent" do
  supports :status => true, :restart => true, :reload => true
  action [:enable, :start]
end


case node['myEnv']
    when "env1"
        filename = "add_host_to_zabbix_ver1.py"
    when "env2"
        filename = "add_host_to_zabbix_ver2.py"
    else
      Chef::Log::warn("don't know what script to use for environment:#{node['myEnv']}")
end


package "python-pip" do
  action :install
end


execute "install pyzabbix using pip" do
  command 'pip install pyzabbix'
  action :run
end

cookbook_file "/tmp/#{filename}" do
  source "#{filename}"
  mode 0755
end

execute "run #{filename}" do
  user "root"
  cwd "/tmp"
  command "python #{filename} --add='host' --host-name='#{node["hostname"]}' --ip='#{node["ipaddress"]}' --group='Linux servers' --template='Template X'"
end

file "/tmp/#{filename}" do
  action :delete
end
