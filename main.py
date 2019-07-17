#!/usr/bin/python

import re
import urllib2
import MySQLdb
import time
from BeautifulSoup import BeautifulSoup
from selenium import webdriver
#------------------------------------------------------------
driver = webdriver.Firefox()

#if loglevel is 1 then print out log, o then print nothing
LOGLEVEL = 0

BASE	= 'http://www.whitepages.com/ind/'
conn = None
SUFFIX	= ['a', 'b', 'c', 'd', 'e', 'f', 'g',
	   'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
	   'q', 'r', 's', 't', 'u', 'v', 'w','x','y','z']

def LOG(msg):
    global LOGLEVEL
    if LOGLEVEL == 1: print msg
#------------------------------------------------------------
# MySQL database connection
conn = MySQLdb.connect("localhost")
dbcur = conn.cursor()
dbcur.execute('SET NAMES utf8;')
dbcur.execute('SET CHARACTER SET utf8;')
dbcur.execute('SET character_set_connection=utf8;')
if 0:
    if dbcur.execute('CREATE DATABASE IF NOT EXISTS whitepage;') == 0L:
	dbcur.execute("use whitepage;")
	dbcur.execute('CREATE TABLE peoples(inx INT, name VARCHAR(20), address VARCHAR(100), phonenum VARCHAR(20), url VARCHAR(100));')

dbcur.execute("use whitepage;")
#-----------------------------------------------------------
# Main
for iter in SUFFIX:
    url_level1 = BASE + iter
    req1 = urllib2.urlopen(url_level1)
    res1 = req1.read()
    soup1 = BeautifulSoup(res1)
    pattern1 = "/ind/%s-" %(iter)
    candidates_level2 = soup1.findAll(href=re.compile(pattern1))
    for link1 in candidates_level2:
	suffix1 = link1.get('href')
	url_level2 = BASE[:-5] + suffix1

	req2 = urllib2.urlopen(url_level2)
	res2 = req2.read()
	soup2 = BeautifulSoup(res2)
	pattern2 = "%s-" %(suffix1)
	candidates_level3 = soup2.findAll(href=re.compile(pattern2))
	for link2 in candidates_level3:
	    suffix2 = link2.get('href')
	    url_level3 = BASE[:-5] + suffix2
	    LOG("Find next step Url : %s" %(url_level3))
	    #TODO: tweek to avoid auto-robot detection on servier-side.
	    time.sleep(3)

	    req3 = urllib2.urlopen(url_level3)
	    res3 = req3.read()
	    soup3 = BeautifulSoup(res3)
	    candidates_level3 = soup3.findAll(href=re.compile("/name/"))
	    for link3 in candidates_level3:
		suffix3 = link3.get('href')
		url_level4 = BASE[:-5] + suffix3
		LOG("Find second next step Url : %s" %(url_level4))
		#TODO: tweek to avoid auto-robot detection on servier-side.
		time.sleep(3)
		driver.get(url_level4)
		soup4 = BeautifulSoup(driver.page_source)

		pattern4 = r"%s/\w[A-Za-z]+" %(suffix3)
		candidates_level4 = soup4.findAll(href=re.compile(pattern4))
		if candidates_level4.__len__() == 0:
		    print "pass"
		    continue
		for link4 in candidates_level4:
		    url_level5 = BASE[:-5] + link4.get('href')
		    # if the url was already scraped then skip next step
		    dbcur.execute("select * from peoples where url like \"%s\";" % url_level5)
		    result = dbcur.fetchone()
		    if result <> None: continue

		    LOG("Find third next step Url : %s" %(url_level5))
		    #TODO: tweek to avoid auto-robot detection on servier-side.
		    time.sleep(3)
		    driver.get(url_level5)
		    soup5 = BeautifulSoup(driver.page_source)
		    name = soup5.find("span", "name block").text.encode('utf-8')
		    phonenum_ = soup5.find(href=re.compile("tel:"))
		    if phonenum_ == None:
			phonenum = ""
		    else:
			phonenum = phonenum_.get('href').encode('utf-8')
			phonenum = phonenum[4:]
			phonenum = "%s-%s-%s" %(phonenum[:3], phonenum[3:6], phonenum[6:])
		    address_ = soup5.find("address")
		    if address_ == None:
			address == ""
		    else:
			address = address_.text.encode('utf-8')
		    url = url_level5

		    dbcur.execute("INSERT INTO peoples (name, address, phonenum, url) VALUES (\"%s\", \"%s\", \"%s\", \"%s\");" % (name, address, phonenum, url))
		    conn.commit()
conn.close()
