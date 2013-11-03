#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Program pro testování webové aplikace, který z ní sesbírá linky
# rekurzivně do určité úrovně a následně simuluje klienty tak, že ve vláknech
# tyto odkazy navštěvuje a zaznamenává čas odezvy a stavový kód odpovědi

# import konfigura4n9ho souboru
import config

# import dalsich komponent
import sys,os,time,urllib,lxml

import urllib2
import re

# modul pro nahodna cisla
import random

# modul pro zpracovani procesu
import multiprocessing

# funkce, ktera simuluje chovani klienta
def client(urls,delay=0,randomdelay=False,mindelay=1,maxdelay=10):
	# ziskame jmeno processu
	name = multiprocessing.current_process().name
	# pockame nahodne zvolenou dobu pred zacatkem prohlizeni
	time.sleep(random.randint(mindelay,maxdelay))
	# zacneme s generovanim requestu
	for x in range(config.requestperclient):
		# vybereme nahodnou url k navsteve
		url = random.choice(urls)
		# pokud mame pockat nahodny cas, vygenerujeme jej, pokud ne, pockame definovany cas
		if randomdelay:
			delay = random.randint(mindelay,maxdelay)
		time.sleep(delay)
		# zacatek simulovaneho klinuti
		starttime = time.time()
		# stahneme si obsah stranky ev. ulozime chybovy kod
		statuscode = 0
		try:
			page = urllib2.urlopen(url)
			page = page.read()
		except urllib2.HTTPError, e:
			statuscode = e.code
		except urllib2.URLError, e:
			statuscode = e.reason[0]	
		# konec simulovaneho requestu a vypis informaci
		endtime = time.time()
		# pokud nemame chybovy kod, je vse OK
		if statuscode == 0:
			statuscode = 200
		print '%s;%d;%d;%.4f;%d;%s' % (name,x,delay,endtime-starttime,statuscode,url)
		

# hlavni program, kde nejdrive naplnime pole s url adresami a pak spustime vlakna

# pole pro url adresy
# hlavni pole uchovavajici vysledky
urls = []
# pole cerstve nalezenych adres, ktere se pak pridaji do hlavniho pole
addurls = []
# pole url, ktere se maji v dalsim kroku prohledat
searchurls = []

# cas startu programu
starttime = time.time()

# dalsi promenne
urlcounter = 0

print 'Zahajuji hledani url adres do urovne %d od %s' % (config.searchlevel,config.baseurl)
# projdeme v urcitem poctu kroku vsechny url a hledame dalsi nastevou tech nalezenych
for x in range(config.searchlevel):
	# pri prvnim pruchodu zacneme od zakladni adresy
	if x == 0:
		searchurls.append(config.baseurl)
	for url in searchurls:
		urlcounter += 1
		
		try:
			page = urllib2.urlopen(url)
			page = page.read()
		except urllib2.HTTPError, e:
			urls.remove(url)
			continue
		except urllib2.URLError, e:
			urls.remove(url)
			continue

		links = re.findall(r"<a.*?\s*href=\"(.*?)\".*?>.*?</a>", page)
		for link in links:
			print('href: %s' % (link))
			
			# ignorujeme odkazy na maily
			if link.find('mailto') > 0:
				continue
			
			# pokud link neobsahuje baseurl a nejedna se o relativni adresu, preskocime jej
			if link.find(config.baseurl) < 0:
				# print('link neobsahuje baseurl')
				# pokud link zacina teckou, jedna se o relativni adresu a v tom pripade ji prevedeme na absolutni
				if link.find('.') == 0:
					link = link.replace('.',config.baseurl,1)
					# print('jedna se o relativni adresu')
					# a pridame do pole, pokud tam jiz neni
					if link not in addurls:
						addurls.append(link)
				# pokud link zacina lomitkem, jedna se o relativni adresu a v tom pripade ji spojime s baseurl
				if link.find('/') == 0:
					link = config.baseurl + link
					# print('jedna se o relativni adresu')
					# a pridame do pole, pokud tam jiz neni
					if link not in addurls:
						addurls.append(link)
			else:
				# ty, ktere baseurl obsahuji priradime do seznamu hned
				if link not in addurls:
					addurls.append(link)
							
	# pridame nove url do hlavniho pole
	for url in addurls:
		if url not in urls:
			urls.append(url)
			
	# sestavime pole pro vyhledavani v dalsi iteraci
	searchurls = []
	for url in addurls:
		searchurls.append(url)
	
#print urls
# vytiskneme informace o zpracovanych adresach
print 'Celkem prohledano %d url adres a nalezeno %d pouzitelnych' % (urlcounter,len(urls))
print 'Hledani url do %d urovne trval %.4f sekund' % (config.searchlevel, time.time() - starttime)
response = raw_input("Pro pokracovani stiskni Enter")
print 'Spoustim simulaci %d klientu.' % (config.clientscount)

# spustime processy, ktere simuluji klienty
if __name__ == '__main__':
	processes = []
	for x in range(config.clientscount):
		p = multiprocessing.Process(name=str(x), target=client, args=(urls,config.delay,config.randomdelay,config.mindelay,config.maxdelay))
		processes.append(p)
		print 'Spoustim process cislo %d' % (x)
		p.start()
