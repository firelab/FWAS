# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 16:21:11 2017

@author: tanner

PRIMARY ALERT CREATOR FOR HRRR
"""

import HR
import calcTime

import numpy

"""
The commented stuff is for debugging
"""
#unitLib={'temperature_units': '2', 'wind_speed_units': '2'}
#thresholdsLib={'relative_humidity': '5',
# 'temperature': '75',
# 'wind_gust': '10',
# 'wind_speed': '15'}
#headerLib={'alert_name': 'Alert',
# 'alert_time': '2017-06-06 19:50:01',
# 'carrier': 'NaN',
# 'email': 'fsweather1@usa.com',
# 'expires_after': '24',
# 'latitude': '46.92',
# 'limit': '0',
# 'longitude': '-114.1',
# 'phone': 'NaN',
# 'radius': '12',
# 'time_zone': '2'}
#HRRRLib={'forecast_on': '1',
# 'reflectivity': '1',
# 'relative_humidity': '1',
# 'temperature': '1',
# 'wind_speed': '1'}
#
#unitLimits={'spd': 'miles_per_hour', 'spdABV': 'mph', 'temp': 'Farenheit', 'tempABV': 'F'}

#samDat=[HR.reflectivity(),HR.temperature(),HR.RH(),HR.Empty(),HR.Empty(),HR.Wind()]
#samDat2=[HR.reflectivity(),HR.temperature(),HR.RH(),HR.Empty(),HR.Empty(),HR.Wind()]
#vecDat=[samDat,samDat2,samDat,samDat,samDat,samDat,samDat]
#
#vecDat[1][0].average=45 #Simulates storms
#vecDat[1][0].limBool=True
#vecDat[1][0].pctCovered=0.80
#vecDat[1][0].eDist=5
#vecDat[1][0].eBearing=180
#vecDat[1][0].fBear='S'
#vecDat[1][0].eVal=45
#
#vecDat[1][1].average=85
#vecDat[1][1].limBool=True
#vecDat[1][1].pctCovered=0.55
#vecDat[1][1].exceedQuad='W'
#vecDat[1][1].eDist=0
#vecDat[1][1].eBearing=0
#vecDat[1][1].fBear=''
#vecDat[1][1].eVal=85
#
#vecDat[1][2].average=3
#vecDat[1][2].limBool=True
#vecDat[1][2].pctCovered=0.85
#vecDat[1][2].exceedQuad=''
#vecDat[1][2].eDist=0
#vecDat[1][2].eBearing=245
#vecDat[1][2].fBear='SW'
#vecDat[1][2].eVal=15
#
#vecDat[1][5].average=25
#vecDat[1][5].limBool=True
#vecDat[1][5].pctCovered=0.10
#vecDat[1][5].exceedQuad=''

#zone='2' #This imitates the headerLib TZ which will be fed leader

aTitle="FWAS Forecast Alert:\n\n"

def getLocalTimes(headerLib):
    """
    Returns Local Times from header Lib and calctime
    """
    timeList=calcTime.calcForecastTimes()

    localTimeList=[]
    
    lTZ=calcTime.convertTimeZone(int(headerLib['time_zone']))
    
    for i in range(len(timeList)):
        lT=calcTime.utcToLocal(timeList[i],lTZ)
        localTimeList.append(lT)
    return localTimeList

def getQualRadar(radFloat):
    """
    https://en.wikipedia.org/wiki/DBZ_(meteorology), Rough qualitative approx of radar 
    """
    radStr=''
    if radFloat<20:
        radStr='NaN'
    if radFloat>=20:
        radStr='Very light'
    if radFloat>=25:
        radStr='Light'
    if radFloat>=30:
        radStr='Light to moderate'
    if radFloat>=35:
        radStr='Moderate (with Rain)'
    if radFloat>=45:
        radStr='Moderate to heavy'
    if radFloat>=50:
        radStr='Heavy'
    if radFloat>=55:
        radStr='Very heavy/small hail'
    if radFloat>=60:
        radStr='Extreme/moderate hail'
    if radFloat>=65:
        radStr='Extreme/large hail'
    if radFloat>=70:
        radStr='Extreme'
    return radStr


def createAlert(vecDat,time,headerLib,unitLimits,thresholdsLib):
    """
    DEPRECATED. Don't use 
    """
    localTimeList=getLocalTimes(headerLib)
    p=time
    aHeader='The HRRR Forecast within a '+headerLib['radius']+' mi radius of your location for '+\
    localTimeList[p].strftime('%H:%M, %Y-%m-%d')+' has exceeded set Thresholds\n\n'
    
    aQuads=[]
    for i in range(len(vecDat[p])):
        if vecDat[p][i].exceedQuad!='':
            aQuads.append(' Largely '+vecDat[p][i].exceedQuad+' of your Location.')
        else:
            aQuads.append('')
    
    aReflec=''
    aTemp=''
    aRH=''
    aWind=''
    if vecDat[p][0].limBool==True:
        aReflec='Weather Intensity: '+getQualRadar(vecDat[p][0].average)+\
        ' in '+str(round(vecDat[p][0].pctCovered*100,3))+' % of the area.'+aQuads[0]+'\n\n'
    #    print aReflec
        
    if vecDat[p][1].limBool==True:
        aTemp='Temperature exceeds: '+thresholdsLib['temperature']+' '+unitLimits['tempABV']+\
        ' in '+str(round(vecDat[p][1].pctCovered*100,1))+' % of the area (Average: '+str(round(vecDat[p][1].average,1))+\
        ' '+unitLimits['tempABV']+' ).'+aQuads[1]+'\n\n'
    #    print aTemp
        
    if vecDat[p][2].limBool==True:
        aRH='Relative Humidity is below: '+thresholdsLib['relative_humidity']+\
        ' % in '+str(round(vecDat[p][2].pctCovered*100,1))+' % of the area (Average: '+str(round(vecDat[p][2].average,1))+\
        ' % ).'+aQuads[2]+'\n\n'
    #    print aRH
        
    if vecDat[p][5].limBool==True:
        aWind='Wind Speeds exceed: '+thresholdsLib['wind_speed']+' '+unitLimits['spdABV']+\
        ' in '+str(round(vecDat[p][5].pctCovered*100,1))+' % of the area (Average: '+str(round(vecDat[p][5].average,1))+\
        ' '+unitLimits['spdABV']+' ).'+aQuads[5]+'\n\n'
    #    print aWind

    if aReflec=='' and aTemp=='' and aRH=='' and aWind=='':
        aTitle=''
        aHeader=''
    
    aString=aHeader+aReflec+aTemp+aRH+aWind
    return aString
    
    
#print createAlert(vecDat,1,headerLib,unitLimits,thresholdsLib)    


def chainAlerts(fCast,hList,headerLib,unitLimits,thresholdsLib):
    """
    Deprecated, Don't Use!
    """
    timeList=calcTime.calcForecastTimes()
#    print calcTime.datetime.datetime.utcnow()
    tRange=[]
    alertList=[]
    late=calcTime.datetime.datetime.now()-calcTime.datetime.timedelta(minutes=59)
    hList[1]=hList[1]
    for i in range(len(timeList)):
        if timeList[i]>late:
            tRange.append(i)
    print tRange 
    for i in tRange:
#        print timeList[i]
        sAlert=createAlert(fCast,i,headerLib,unitLimits,thresholdsLib)
        alertList.append(sAlert)
    
    
    
#    puce=0
    return alertList    

"""
Most of the above is now deprecated
"""

def createReflecLine(fCasts,tList):
    """
    Creates Alert for Reflectivity, reports general area storms storms closest to your location
    """
#    qSpec={'NaN':0,'Very light':0,'Light':0,'Light to moderate':0,'Moderate Rain':0,'Moderate to heavy':0,'Heavy':0,'Very heavy/small hail':0,'Extreme/moderate hail':0,'Extreme/large hail':0,'Extreme':0}
#    qSpotA={'NaN':0,'Very light':0,'Light':0,'Light to moderate':0,'Moderate Rain':0,'Moderate to heavy':0,'Heavy':0,'Very heavy/small hail':0,'Extreme/moderate hail':0,'Extreme/large hail':0,'Extreme':0}
    
    nAv=[]
    nSpot=[]
#    qAv=[]
#    qSpot=[]
#    qATime=[]
#    qSTime=[]
    for i in range(len(fCasts)):
        nAv.append(fCasts[i][0].average)
        nSpot.append(fCasts[i][0].eVal)
    
    nAv=numpy.array(nAv)
    nSpot=numpy.array(nSpot)
    
    maxAv=nAv.max()
    maxSpot=nSpot.max()
    
    locAv=nAv.argmax()
    locSpot=nSpot.argmax()
    qA=getQualRadar(maxAv)
    qS=getQualRadar(maxSpot)

    aReflec='Weather Intensity in the general area is FORECASTED to be\n'
    bReflec='Closest to Your Location: \n'
    refecSing=''
    befecSing=''
    
    refecSing=qA+' from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
#    refecSing=qAv[0]+' at '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+qAv[-1]+' at '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    befecSing=qS+' from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    return aReflec+refecSing+bReflec+befecSing

def createLtngLine(fCast,tList):
    """
    Creates Lightning Alert, reports anything above 1.0 flashes/km^2/5 min in the general area and the closest strikes to you!
    """
    n=[]
    dist=[]
    for i in range(len(fCast)):
        dist.append(fCast[i][3].eDist)
    dist=numpy.array(dist)
    vMin=numpy.min(dist[numpy.nonzero(dist)])
    aMin=numpy.argmin(dist[numpy.nonzero(dist)])
    
    line='FORECASTED Strong Chance of Lightning from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    cLine='Closest Strikes to Your Location: '+str(round(vMin,1))+' miles '+str(fCast[aMin][3].fBear)+' at '+tList[aMin].strftime('%H:%M, %Y-%m-%d')+'\n'
    return line+cLine

def createPrecipLine(fCast,tList):
    """
    Creates Precipitation Alert, reports precip in length/hour 
    """
    n=[]
#    dist=[]
    for i in range(len(fCast)):
        n.append(fCast[i][4].average)
#        dist.append(fCast[i][4].eDist)
#    dist=numpy.array(dist)
    n=numpy.array(n)
    nMin=numpy.average(n[numpy.nonzero(n)])       
    line='Precipitation in the general area is FORECASTED to be greater than '+str(round(nMin,2))+' '+fCast[0][4].units+' from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    return line    
    
def createTempLine(thresholdsLib,fCasts,tList):
    """
    Creates HRRR Temperature Alert, reports general info about temp
    """
    line='The temperature is FORECASTED to exceed '+str(thresholdsLib['temperature'])+' '+str(fCasts[0][1].units)+' from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    return line

def createSpeedLine(thresholdsLib,fCasts,tList):
    """
    Reports general info about Wind speed
    """
    line='The wind speed is FORECASTED to exceed '+str(thresholdsLib['wind_speed'])+' '+str(fCasts[0][5].units)+' from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    return line

def createRHLine(thresholdsLib,fCasts,tList):
    """
    Creates Relative Humidity alert, general info only
    """
    line='The relative humidity is FORECASTED to be less than '+str(thresholdsLib['relative_humidity'])+' '+str(fCasts[0][2].units)+' from '+tList[0].strftime('%H:%M, %Y-%m-%d')+' to '+tList[-1].strftime('%H:%M, %Y-%m-%d')+'\n'
    return line

def createVarAlert(fCast,headerLib,unitLimits,thresholdsLib):
    """
    Compiles above alerts into one list and figures out local Times
    """
    vList=[[],[],[],[],[],[]]
    localTimeList=getLocalTimes(headerLib)
    localTimeList.sort()
    for i in range(len(fCast)):
        for j in range(len(fCast[i])):
            if fCast[i][j].limBool==True:
                vList[j].append(i)
                
    reflecAlert=''
    tAlert=''
    spdAlert=''
    rhAlert=''
    ltAlert=''
    ppAlert=''
       
    if any(vList[0]):
        print 'HRRR REFEC Threshold Reached...'
        reflecAlert=createReflecLine(fCast[vList[0][0]:vList[0][-1]+1],localTimeList[vList[0][0]:vList[0][-1]+1])
    if any(vList[1]):
        print 'HRRR TMP Threshold Reached...'
        tAlert=createTempLine(thresholdsLib,fCast[vList[1][0]:vList[1][-1]+1],localTimeList[vList[1][0]:vList[1][-1]+1])
    if any(vList[5]):
        print 'HRRR WSPD Threshold Reached...'
        spdAlert=createSpeedLine(thresholdsLib,fCast[vList[5][0]:vList[5][-1]+1],localTimeList[vList[5][0]:vList[5][-1]+1])
    if any(vList[2]):
        print 'HRRR RH Threshold Reached...'
        rhAlert=createRHLine(thresholdsLib,fCast[vList[2][0]:vList[2][-1]+1],localTimeList[vList[2][0]:vList[2][-1]+1])
    if any(vList[3]):
        print 'HRRR LGTNG Threshold Reached...'
        ltAlert=createLtngLine(fCast[vList[3][0]:vList[3][-1]+1],localTimeList[vList[3][0]:vList[3][-1]+1])
    if any(vList[4]):
        print 'HRRR PRATE Threshold Reached...'
        ppAlert=createPrecipLine(fCast[vList[4][0]:vList[4][-1]+1],localTimeList[vList[4][0]:vList[4][-1]+1])
        
    return [reflecAlert,tAlert,rhAlert,ltAlert,ppAlert,spdAlert]






