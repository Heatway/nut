#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import time
import json
import Title
import operator
import Config
import Print
import threading

global titles
titles = {}

def data():
	return titles

def items():
	return titles.items()

def get(key):
	return titles[key]
	
def contains(key):
	return key in titles
	
def set(key, value):
	titles[key] = value
	
#def titles():
#	return titles
	
def keys():
	return titles.keys()
	
def loadTitleFile(path, silent = False):
	timestamp = time.clock()
	with open(path, encoding="utf-8-sig") as f:
		loadTitleBuffer(f.read(), silent)
	Print.info('loaded ' + path + ' in ' + str(time.clock() - timestamp) + ' seconds')
	
def loadTitleBuffer(buffer, silent = False):
	firstLine = True
	map = ['id', 'key', 'name']
	for line in buffer.split('\n'):
		line = line.strip()
		if len(line) == 0 or line[0] == '#':
			continue
		if firstLine:
			firstLine = False
			if re.match('[A-Za-z\|\s]+', line, re.I):
				map = line.split('|')
				continue
		
		t = Title.Title()
		t.loadCsv(line, map)

		if not t.id in keys():
			titles[t.id] = Title.Title()
			
		titleKey = titles[t.id].key
		titles[t.id].loadCsv(line, map)

		if not silent and titleKey != titles[t.id].key:
			Print.info('Added new title key for ' + str(titles[t.id].name) + '[' + t.id + ']')

	
def load():
	if os.path.isfile("titles.txt"):
		loadTitleFile('titles.txt', True)

	try:
		files = [f for f in os.listdir(Config.paths.titleDatabase) if f.endswith('.txt')]
		files.sort()
	
		for file in files:
			loadTitleFile(Config.paths.titleDatabase + '/' + file, False)
	except BaseException as e:
		Print.error(str(e))

	
def save(fileName = 'titles.txt', map = ['id', 'rightsId', 'key', 'isUpdate', 'isDLC', 'isDemo', 'name', 'version', 'region', 'retailOnly']):
	buffer = ''
	
	buffer += '|'.join(map) + '\n'
	for t in sorted(list(titles.values())):
		buffer += t.serialize(map) + '\n'
		
	with open(fileName, 'w', encoding='utf-8') as csv:
		csv.write(buffer)

class Queue:
	def __init__(self):
		self.queue = []
		self.lock = threading.Lock()
		self.i = 0

	def add(self, id):
		self.lock.acquire()
		id = id.upper()
		if not id in self.queue and self.isValid(id):
			self.queue.append(id)
		self.lock.release()

	def shift(self):
		self.lock.acquire()
		if self.i >= len(self.queue):
			self.lock.release()
			return None

		self.i += 1

		r =self.queue[self.i-1]
		self.lock.release()
		return r

	def empty(self):
		return bool(self.size() == 0)

	def get(self):
		return self.queue

	def isValid(self, id):
		return contains(id)

	def load(self):
		try:
			with open('queue.txt', encoding="utf-8-sig") as f:
				for line in f.read().split('\n'):
					self.add(line.strip())
		except BaseException as e:
			Print.error(str(e))
			pass

	def size(self):
		return len(self.queue) - self.i

	def save(self):
		self.lock.acquire()
		try:
			with open('queue.txt', 'w', encoding='utf-8') as f:
				for id in self.queue:
					f.write(id + '\n')
		except:
			pass
		self.lock.release()

global queue
queue = Queue()