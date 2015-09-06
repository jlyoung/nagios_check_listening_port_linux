"""This module serves as a Nagios check whose goal is to report whether the
specified process can be found listening on an expected port.
"""

import shlex, sys, re
from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT

def main():
	"""Parses command line arguments for the Nagios check."""
	# Compatible with with Python versions 2.4 - 2.7.X
	usage = "usage: %prog [options]"
	parser = OptionParser(usage)
	parser.add_option("-n", "--name",
	                  action="store", dest="process_name",
	                  help="process name")
	parser.add_option("-p", "--port",
	                  action="store", type="int", dest="port_number",
	                  help="port number")
	options = parser.parse_args()[0]
	if (options.process_name is None) or (options.port_number is None):
		print "Incorrect usage. Process name and port number arguments are mandatory."
		parser.print_help()
		sys.exit(3)
	check_execution = perform_check()
	process_results(check_execution, options.process_name, int(options.port_number))


def perform_check():
	"""Executes netstat and returns the output."""
	# NOTE: Execute "which netstat"
	# to find the full path to your netstat utility.
	# Replace the path below with the installation path for netstat on your system.
	command = "sudo /bin/netstat -tanp"
	command_args = shlex.split(command)
	process = Popen(command_args, stdout=PIPE, stderr=STDOUT)
	output = process.communicate()[0]
	process_return_code = process.returncode
	check_execution = {'result': output, 'return_code': process_return_code}
	return check_execution


def process_results(check_execution, process_name, port_number):
	"""Parses netstat output looking for the process name and port number."""
	metric_name = 'listening_on_expected_port'
	if check_execution['return_code'] != 0:
		print "UNKNONW ERROR - An unknown error occured: %s" % (check_execution['result'])
		sys.exit(3)
	if not check_execution['result']:
		print "UNKNOWN ERROR - No output from netstat. Listening status could " \
		"not be determined for process %s on port %d | '%s'=%d;;;;" % \
			(process_name, port_number, metric_name, 0)
		sys.exit(3)
	state_regex = re.compile('(LISTEN.*|ESTABLISH.*)')
	header_regex = re.compile('(Active Internet connections|Recv-Q)')
	processes_found = []
	for line in check_execution['result'].splitlines():
		if header_regex.match(line):
			continue
		netstat_columns = line.split()
		if len(netstat_columns) < 7:
			print "UNKNOWN ERROR - netstat column format not recognized.  " \
			"This script only works with the Linux version of netstat."
			sys.exit(3)
		if process_name in netstat_columns[6]:
			if state_regex.match(netstat_columns[5]):
				local_address, listening_port = netstat_columns[3].rsplit(':', 1)
				if int(listening_port) == port_number:
					processes_found.append(local_address)
	if processes_found:
		print "OK. %s found listening on port %d for the following address(es): [%s] | '%s'=%d;;;;" % \
			(process_name, port_number, ', '.join(processes_found), metric_name, 1)
		sys.exit(0)
	else:
		print "CRITICAL - No process named %s could be found listening on port %d | '%s'=%d;;;;" % \
			(process_name, port_number, metric_name, 0)
		sys.exit(2)


if __name__ == '__main__':
	main()
