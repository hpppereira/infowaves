

################
# IMPORT MODULES
################

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import urllib2
import numpy as np
import csv
import datetime as dt
import matplotlib.dates as mdates
from intdir2uv import intdir2uv
#from matplotlib.font_manager import FontProperties
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict
from matplotlib.dates import date2num
from convert_coord import interpret_coord



################
# SOME FUNCTIONS
################
def smooth(x, window_len=200, window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
    s = np.r_[2*x[0]-x[window_len-1::-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w = np.ones(window_len, 'd')
    else:  
        w = eval('np.' + window + '(window_len)')
        x = np.convolve(w / w.sum(), s, mode='same')
    return x[window_len : -window_len+1]


def VarIndex(columns,varname):
	
	v, i = [], []
	for k in range(len(columns.keys())):
		if columns.keys()[k][:len(varname)] == varname:
			v.append(columns.keys()[k])
			i.append(k)
			print columns.keys()[k], 'index:', k


def DateWindow(datearray, di, mi, yi, df, mf, yf ):
	ti = dt.datetime(yi,mi,di)
	tf = dt.datetime(yf,mf,df)

	for k in range(len(datearray)):
		if datearray[k] == ti:
			fi = k 
		elif datearray[k] == tf:
			ff = k 
	
	return fi, ff


################
# LOADING DATA
################

wave_filename = 'UFPRWaves.csv'
met_filename  = 'UFPRMet.csv'

waves = defaultdict(list) 
with open(wave_filename,'rU') as f:
    reader = csv.DictReader(f) 
    for row in reader: 
        for (k,v) in row.items(): 
            waves[k].append(v)

met = defaultdict(list) 
with open(met_filename,'rU') as f:
    reader = csv.DictReader(f) 
    for row in reader: 
        for (k,v) in row.items(): 
            met[k].append(v)

files = [waves, met]
for f in files:
    for k in range( len(f.keys()) ):
    	for v in range( len(f.values()[k]) ):
    		if f.values()[k][v] == '':
    			f.values()[k][v] = np.nan
    		else:
    			pass

MET = [k.upper()  for k in met.keys()]                	

################
# DATE WINDOW
################

date_window = 7
tlim = 24 * date_window   # put date_window as function argument  

################
# DATES
################

wave_DateTimeStamp = waves.values()[8][:tlim]
wave_Dates = [dt.datetime.strptime(k, '%m/%d/%Y %I:%M:%S %p') for k in wave_DateTimeStamp]
wave_datesnum = date2num(wave_Dates)

met_DateTimeStamp = met.values()[6][:tlim]
met_Dates = [dt.datetime.strptime(k, '%m/%d/%y %H:%M') for k in met_DateTimeStamp]
met_datesnum = date2num(met_Dates)

################
## COORDINATE
################

#VarIndex('Curr') 

lon, lat = met.values()[4], met.values()[0]
coord = [lon, lat]

for c in coord:
    for k in range(len(c)):
        if type(c[k])==str:
            c[k] = c[k][:-1]
        else:
            pass    

lon = map(float, lon)
lat = map(float, lat)

for l in lon:
    a = interpret_coord(l)



################
# WAVES
################
IDmsg = map(int, waves.values()[10] )

#VarIndex('H')   

Hvar = 5    # número de variáveis relativas a altura de onda
Tvar = 6    # número de variáveis relativas ao periodo de onda
Dvar = 1    # número de variáveis relativas a direcao de onda 
Svar = 1    # número de variáveis relativas ao espalhamento espectral

WAVEh = np.zeros((Hvar, len(wave_Dates[:tlim]) ))
WAVEt = np.zeros((Tvar, len(wave_Dates[:tlim])))
WAVEdir = np.zeros((Dvar, len(wave_Dates[:tlim])))
WAVEsp = np.zeros((Svar, len(wave_Dates[:tlim])))
WAVEzc = np.zeros((Svar, len(wave_Dates[:tlim])))

c = 0
for t in range(len(wave_Dates[:tlim])):
    WAVEh[0,c] = float(waves.values()[2][t])  # altura significativa (m)   
    WAVEh[1,c] = float(waves.values()[1][t])  # altura média (m)
    WAVEh[2,c] = float(waves.values()[4][t])  # Significant Wave Height Spectral Moment (m) 
    WAVEh[3,c] = float(waves.values()[12][t]) # altura maxima (m) - (onda individual)
    WAVEh[4,c] = float(waves.values()[15][t]) # Highest 10th of Waves (m)
    c += 1 

c = 0
for t in range(len(wave_Dates[:tlim])):
    WAVEdir[0,c] = float(waves.values()[5][t]) # Mean Wave Direction (deg) 
    c += 1 

c = 0
for t in range(len(wave_Dates[:tlim])):
    WAVEt[0,c] = float(waves.values()[0][t])   # Tz - mean spectral period (seconds)
    WAVEt[1,c] = float(waves.values()[3][t])   # Tp5 - Peak Period Read Method (seconds)
    WAVEt[2,c] = float(waves.values()[7][t])   # TP - Peak Period (seconds) 
    WAVEt[3,c] = float(waves.values()[9][t])   # TAvg - Average Wave Period (seconds) 
    WAVEt[4,c] = float(waves.values()[13][t])  # Tsig - Significant Period (seconds)
    WAVEt[5,c] = float(waves.values()[14][t])  # T10 - Average Period of Highest 10th of Waves (seconds)
    c += 1 

c = 0
for t in range(len(wave_Dates[:tlim])):
    WAVEsp[0,c] = float(waves.values()[11][t]) # Mean Spread (deg)    
    c += 1 

c = 0
for t in range(len(wave_Dates[:tlim])):
    WAVEzc[0,c] = float(waves.values()[6][t]) # Zero Crossing  
    c += 1       


###########
## METEO...
###########

#VarIndex(met,'Data')

met[met.keys()[6]] = [dt.datetime.strptime(k, '%m/%d/%y %H:%M') for k in met[met.keys()[6]]]

# met[met.keys()[0]] = map(float,met.values()[0])

met[met.keys()[2]] = map(float, met.values()[2])


met[met.keys()[-4]] = map(float, met.values()[-4])
met[met.keys()[-3]] = map(float, met.values()[-3])
met[met.keys()[-2]] = map(float, met.values()[-2])
met[met.keys()[-1]] = map(float, met.values()[-1])

wind_dir = map(float, met['Average wind direction'])
wind_int = map(float, met['Average wind speed'])

wind_dir, wind_int = np.array(wind_dir), np.array(wind_int)

Uwind, Vwind = intdir2uv(wind_int[:tlim], wind_dir[:tlim], 0, 0)




  



###########
## PANDAS TEST
###########

# data = pd.read_csv(filename, parse_dates=True)
# a = data.convert_objects(convert_numeric=True)
