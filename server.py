
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Made by Vasile2k. See LICENSE

import os
import socket
import argparse

# MIME types for most common files used on a web server

MIME_TYPES = {

	"txt"  : "text/plain",
	"html" : "text/html",
	"css"  : "text/css",
	"js"   : "text/javascript",
	"xml"  : "text/xml",

	"gif"  : "image/gif",
	"png"  : "image/png",
	"jpg"  : "image/jpeg",
	"jpeg" : "image/jpeg",
	"bmp"  : "image/bmp",
	"webp" : "image/webp",

	"mid"  : "audio/midi",
	"midi" : "audio/midi",
	"mpg"  : "audio/mpeg",
	"mpeg" : "audio/mpeg",
	"mp1"  : "audio/mpeg",
	"mp2"  : "audio/mpeg",
	"mp3"  : "audio/mpeg",
	"m1v"  : "audio/mpeg",
	"m1a"  : "audio/mpeg",
	"m2a"  : "audio/mpeg",
	"mpa"  : "audio/mpeg",
	"mpv"  : "audio/mpeg",
	# "webm" : "audio/webm",
	# "ogg"  : "audio/ogg",
	"wav"  : "audio/wav",

	"webm" : "video/webm",
	"ogg"  : "video/ogg",
	"flv"  : "video/x-flv",
	"mp4"  : "video/mp4",
	"3gp"  : "video/3gpp",
	"mov"  : "video/quicktime",
	"avi"  : "video/x-msvideo",
	"wmv"  : "video/x-ms-wmv",

	"pdf"  : "application/pdf",

}

if not __name__ == "__main__":
	print("Execute this as main module or it won't work!")
	exit(-1)

class Parameters():
	GET = ""
	POST = ""

class Headers():
	_headers = []

	def __init__(self):
		self._headers = []

	def add(self, object):
		self._headers.append(object)

	def getHeaders(self):
		return self._headers


def parseArgs():
	parser = argparse.ArgumentParser(description = "Simple python webserver")
	parser.add_argument("-p", "--port", help = "Sets port")
	parser.add_argument("-dir", "--directory", help = "Sets website directory")

	args = parser.parse_args()

	if not args.port:
		print("Port was not specified!")
		exit(-1)


	if not args.directory:
		print("Website directory was not specified!")
		exit(-1)
	elif not os.path.isdir(args.directory):
		print("Specified directory is not present on your drive, are you drunk?")
		exit(-1)

	port = args.port
	directory = args.directory
	if directory.endswith("/"):
		directory = directory[:-1]
	return port, directory

def bindSocketAndListen(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# The SO_REUSEADDR flag tells the kernel to reuse a local
	# socket in TIME_WAIT state, without waiting for its
	# natural timeout to expire.

	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	addr = ("0.0.0.0", int(port))
	sock.bind(addr)

	sock.listen(1)
	return sock


def main():

	port, directory = parseArgs()

	if __debug__:
		print("Good! Everything seems to be ready! Let's start!")


	sock = bindSocketAndListen(port)

	if __debug__:
		print("Listening for browsers...")

	while True:
		try:
			connection, client_addr = sock.accept()
			data = connection.recv(512)
			talkToBrowser(connection, directory, data)
			if __debug__:
				print("Sent some website!")
		finally:
			connection.close()
			if __debug__:
				print("Closed connection!")

	sock.close()

def getFileExtension(filename):
	if "." not in filename:
		return ""
	return filename.rsplit(".", 1)[-1]

def talkToBrowser(connection, directory, data):
	browser_headers = parseBrowserData(data)

	requestedFile = browser_headers.GET
	if requestedFile == "/":
		requestedFile = "/index.html"

	headers = Headers()
	absolutePath = directory + requestedFile
	fileExtension = getFileExtension(requestedFile)

	message = 0

	if os.path.isfile(absolutePath):
		headers.add("HTTP/1.1 200 OK")
		headers.add("Content-type: " + getMimeTypeForFile(fileExtension))
		message = open(absolutePath)
	else:
		headers.add("HTTP/1.1 404 Not Found")
		headers.add("Content-type: " + getMimeTypeForFile("txt"))

	sendData(connection, headers, message)

def sendData(connection, headers, message):
	for header in headers.getHeaders():
		connection.send(header)
		# Headers separator
		connection.send("\r\n")

	# Finish with headers and go to message
	# Headers to message separator is actually 2 '\n', but one
	# is already sent with last header separator(4 lines up)
	connection.send("\n")

	if message == 0:
		connection.send("Not Found!")
	else:
		connection.send(message.read())

def parseBrowserData(data):
	lines = data.splitlines()
	result = Parameters()
	for line in lines:
		if line.startswith("GET"):
			result.GET = line.split(" ")[1]
			break
	return result

def getMimeTypeForFile(extension):
	try:
		return MIME_TYPES[extension]
	except KeyError:
		return "text/plain"

main()

