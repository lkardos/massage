#!/bin/python

import os, sys
import subprocess
import getopt
import json
#import datetime
import time

#TODO slots too soon to make changes
#TODO watch for new changes
#TODO limit count, priorities
#TODO timezone? UTC?
#TODO add slots, set data, whoami
#TODO let user choose time interval to list

def list_massages():
	year = 365*24*60*60
	response = send_request("get_data_timestamp?start=" + str(int(time.time()) - year) + "&end=" + str(int(time.time()) + year))
	if not response:
		print "Could not get correct data from server"
		return None
	if not "massages" in response:
		print "Not a single massage is scheduled"
		return None
	for slot in response["massages"]:
		if not show_free_only or not slot["name"] or slot["offered"]:
			print str(slot["id"]) + " starting " + time.ctime(slot["start"]),
			#datetime.date.fromtimestamp(slot["start"]).isoformat()
			print " " + slot["name"],
		if slot["offered"]:
			print " offered"
		else:
			print
	#print response
	return "ok"

def send_request(request):
	try:
		response = os.tmpfile();
		return_code = subprocess.Popen(["curl", "-q", "--negotiate", "-s",
		"-u", ":", "--insecure", "-w", "", "--url", server + request],
		bufsize=0,
		executable=None,
		stdin=None,
		stdout=response,
		stderr=subprocess.STDOUT,
		preexec_fn=None,
		close_fds=True,
		shell=False,
		cwd=None,
		env=None,
		universal_newlines=False,
		startupinfo=None,
		creationflags=0).wait()
	except:
		print "Could not run curl"
		raise
	if return_code:
		print "Communication with server failed"
		return None
	response.seek(0)
	response = json.load(response)
	if not "status" in response:
		print 'Strange json response without "status"'
		print response
		return None
	if response["status"] == "error":
		print "Server responded with error status"
		print response
		return None
	if response["status"] != "ok":
		print "Server responded with strange status"
		print response
		return None
	return response

def usage(*args):
	#TODO help
	print "Usage:"
	print "massage [options]"
	print
	print "options (in getopt format):"
	print longargs
	print "options (short variant): " + str(shortargs)
	return "ok"

def reserve():
	#TODO check status after request automatically
	response = send_request("take?massage_id=" + str(massage_id))
	if not response:
		print "Reservation failed, check the status of your chosen slot again"
		return None
	print "Reserved"
	return "ok"

def offer():
	#TODO check status after request automatically
	#TODO url to offer
	response = send_request("offer?massage_id=" + str(massage_id))
	if not response:
		print "Transaction failed, check the status of your chosen slot again"
		return None
	print "Offered"
	return "ok"

if __name__ == "__main__":
	shortargs = "s:lhtr:o:"
	longargs = ["server=", "list", "help", "show-taken", "reserve=", "offer="]
	try:
		options, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(1)
	server = "https://server.mrproject/"
	action = "list"
	show_free_only = True
	for option, value in options:
		if option in ("-s", "--server"):
			server = value
		elif option in ("-l", "--list"):
			action = list_massages
		elif option in ("-h", "--help"):
			action = usage
		elif option in ("-t", "--show-taken"):
			show_free_only = False
		elif option in ("-r", "--reserve"):
			action = reserve
			massage_id = value
		elif option in ("-o", "--offer"):
			action = offer
			massage_id = value
		else:
			print "Unknown option " + option
			usage()
			sys.exit(1)
	if action():
		sys.exit(0)
	else:
		print "Something went wrong"
		sys.exit(1)
