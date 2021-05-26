#!/usr/bin/python
# -*- coding: utf-8 -*-


#baixar dados meteo-oceanograficos
#do siodoc

# 1 - baixar os dados 1 vez por dia, e enviar a mensagem as 6 hrs da manha
# 1.1 - rodar o programa em shell, chamando o python no crontab
# 2 - criar um programa para listar os arquivos do diretorio e trabalhar
# com o utlimo arquivo baixado
# 3 - mandar as estatisticas de onda
# 3.1 -  corrigir a declinacao

#baixar dados pem shell - terminal
# /usr/bin/wget http://metocean.fugrogeos.com/marinha/Members/Data_month.csv -O /home/hp/Google\ Drive/siodoc/dados/boia_wavescan_`date +\%Y\%m\%d`.txt

import numpy as np
import datetime as dt
import urllib2
from collections import defaultdict
import csv
import os
from twilio.rest import TwilioRestClient

#from datetime as dt

def Download_Datamonth(site_adress,pathname):

	site = urllib2.urlopen(site_adress)

	#actual date (string)
	y = dt.date.today().year
	m = dt.date.today().month
	d = dt.date.today().day

	datefile = '%02d%02d%02d' %(y,m,d)
	filename = "arraial_cabo_"+datefile+".csv"
	
	#create .csv file
	csv = open(pathname + filename,"w")	
	csv.write(site.read())
	csv.close()

	return

def list_csv(pathname):

	''' Lista arquivos com extensao .csv 
	que estao dentro do diretorio 'pathname' '''

	listcsv = []
	# Lista arquivos do diretorio atual
	for f in os.listdir(pathname):
		if f.endswith('.csv'):
			listcsv.append(f)
	listcsv=np.sort(listcsv)

	return listcsv

def InfoWaves(number,text):

	# Your Account Sid and Auth Token from twilio.com/user/account
	account_sid = "AC38697260cb5b9f971abd976df6ca0dd4"
	auth_token  = "b362117fc09df0469a3709476b8316d4"
	client = TwilioRestClient(account_sid, auth_token)
	 
	message = client.messages.create(body=text,
	    to=number,    # Replace with your phone number
	    from_="+14158010218") # Replace with your Twilio number
	print message.sid
	return

############################################################################


site_adress = 'http://metocean.fugrogeos.com/marinha/Members/Data_month.csv'
pathname = os.environ['HOME'] + '/Google Drive/infowaves/dados/'

#download file from site
Download_Datamonth(site_adress,pathname)

#list files .csv
filename = list_csv(pathname)[-1]

#data = time, hm0, tp, dp
data = np.loadtxt(pathname+filename,skiprows=2, delimiter=',',
	usecols=(0,22,52,33), unpack=True,dtype=str)

timea = data[0,:]
ponda = np.array([data[1,:],data[2,:],data[3,:]]).T.astype(np.float)

#acha indice das 6 da manha
#aux = filename[-6:-4] + '.' + filename[-8:-6] + '.' + filename[-12:-8] + ' 06:00:00'
aux = data[0,-1][0:2] + '.' + filename[-8:-6] + '.' + filename[-12:-8] + ' ' + data[0,-1][-8:]
ind = np.where(timea==aux)[0][0]

#parametros das 6 horas
hm0, tp, dp = ponda[ind,:]

#corrige declinacao magnetica (-24 graus)
dp = dp - 24
if dp > 360:
	dp = dp - 360
elif dp < 0:
	dp = dp + 360

#corrige utc para local
# hora = data[0,-1] - 3

DATE = dt.datetime.strptime(data[0,-1], '%d.%m.%Y %H:%M:%S')
date_str = '%s/%s/%s/' %(DATE.day, DATE.month, DATE.year)

aux = DATE.hour-3 
time_str = '%sh' %aux

text = ("InfoWaves : \n" 
	+ date_str + ' at ' + time_str + '\n' +
	"Arraial do Cabo/RJ - SIODOC" + '\n' +
	"Hs = " + str(hm0)[0:4] + " m" + '\n' +
	"Tp = " + str(tp)[0:4] + " s" + '\n' +
	"Dp = " + str(dp)[0:5] + " g" )

# text = 'dae isa, tamo fazendo um teste com o nobru'

#envia mensagem para os telefones cadastrados
number = []
number.append("+5521969131601") #henrique 
# number.append("+5521997818323") #isadora
# number.append("+5512981490195") #maria silvia (mae)
number.append("+5512981055353") #phellipe
# numper.append("+554899454025") #joao clezar - ainda nao cadastrado
# number.append("+554899316240") #rafinha
# number.append("+5521999878587") #fabio nascimento
# number.append("+554797772666") #ricardo cechet
# number.append("+5522999552914") #uggo pinho
# number.append("+5521995103136") #bruno movido


#pi
#parente
#ricardo
#izabel
#marcelo dilello
# ..

#envia mensagem para os telefones da lista number
for i in range(len(number)):

	InfoWaves(number[i],text)

print 'Message sent successfully'
