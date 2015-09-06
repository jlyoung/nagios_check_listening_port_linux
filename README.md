# nagios_check_listening_port_linux

## Summary
**nagios_check_listening_port_linux** is a Nagios plugin written to verify that a specified process name can be found listening on a specified TCP port.

## Requirements
- Linux version of netstat installed at /bin/netstat
- Python version 2.4 - 2.7.X
- /etc/sudoers configured to allow execution of `sudo /bin/netstat -tanp` by the nrpe user

## Example output
Executing the script directly on the host to monitored yields the following results for a process name that is found to be correctly listening on the specified port.
```
[root@ip-joeyoung.io ~]# python /usr/lib/nagios/plugins/nagios_check_listening_port_linux.py -n nginx -p 80
OK. nginx found listening on port 80 for the following address(es): [0.0.0.0] | 'listening_on_expected_port'=1;;;;
```

It yields the following when the specified process name could not be found to be listening on the specified port.
```
[root@ip-joeyoung.io ~]# python /usr/lib/nagios/plugins/nagios_check_listening_port_linux.py -n nginx -p 9999
CRITICAL - No process named nginx could be found listening on port 9999 | 'listening_on_expected_port'=0;;;;
```

# Installation

## On the host to be monitored:

Save the script in the *nagios plugins* folder of the host you wish to monitor.  For example:

```
/usr/lib/nagios/plugins/nagios_check_listening_port_linux.py
```

Modify the /etc/sudoers file (for example, using the `visudo` command) to give the `nrpe` user permission to execute `netstat` as root via the `sudo` command

```
nrpe ALL=(root) NOPASSWD: /bin/netstat -tanp
```

Create an nrpe command definition for the remote execution of the nagios_check_listening_port_linux.py script via `check_nrpe`.
The configuration file to be modified is installation dependent.  Just as an example:
```
vim /etc/nagios/nrpe.cfg
```

Add an nrpe command definition to the config file like so:
```
command[check_listening_port]=/usr/bin/python /usr/lib/nagios/plugins/nagios_check_listening_port_linux.py -n $ARG1$ -p $ARG2$
```

Restart the nrpe service:
```
service nrpe restart
```

## On the Nagios server

Create a command definition for `check_listening_port` to be called from a service definition.  The configuration file to be modified is installation dependent.  We'll modify `/usr/local/nagios/etc/objects/commands.cfg` for this example adding the following:
```
define command{
        command_name check_listening_port
        command_line $USER1$/check_nrpe -H $HOSTADDRESS$ -c check_listening_port -a $ARG1$ $ARG2$
}

```

Create a service definition that will call the `check_listening_port` command. The configuration file to be modified is installation dependent.  We'll modify `/usr/local/nagios/etc/objects/services.cfg` for this example adding the following:
```
define service{
        use                     generic-service
        host_name               linux-server
        service_description     check_listening_port
        check_command           check_listening_port!process_name!port_number
}
```

Replace `process_name` with the process you wish to monitor. (e.g. `nginx`)

Replace `port_number` with the port number you wish to monitor. (e.g. `80`)

Modify the service to match your specific installation and configuration details. (i.e. replace the host_name, etc.)

Reload the nagios configuration.
```
service nagios restart
```




