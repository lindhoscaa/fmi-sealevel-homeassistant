import datetime
from io import StringIO
from xml.etree import ElementTree as ET
import requests
import math

OBSERVATION_QUERY_ID = "fmi::observations::mareograph::instant::simple"
FORECAST_QUERY_ID = "fmi::forecast::sealevel::point::simple"

API_TIMEOUT_IN_SECS = 10

BASE_URL = "http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature"

FORECAST_TIME_STEP = 5
OBSERVATION_TIME_STEP = 5

OBSERVATION_LENGTH_HOURS = 72
FORECAST_LENGTH_HOURS = 72

OBSERVATION_OVERLAP_HOURS = 1
FORECAST_OVERLAP_HOURS = 1

DEFAULT_UNIT = "cm"

DEFAULT_FMISID = 134253

def get_forecast(fmisid: int = DEFAULT_FMISID, unit: str = DEFAULT_UNIT, forecastOverlapHours: int = FORECAST_OVERLAP_HOURS, apiTimeout: int = API_TIMEOUT_IN_SECS, forecastTimeStep: int = FORECAST_TIME_STEP, forecastLengthHours: int = FORECAST_LENGTH_HOURS,):
    timeNow = datetime.datetime.utcnow()
    startTime = timeNow - datetime.timedelta(hours=forecastOverlapHours)
    endTime = timeNow + datetime.timedelta(hours=forecastLengthHours)
    startTimeString = startTime.isoformat(timespec="seconds") + "Z"
    endTimeString = endTime.isoformat(timespec="seconds") + "Z"

    url = BASE_URL + "&storedquery_id=" + FORECAST_QUERY_ID + "&fmisid=" + str(fmisid) + "&starttime=" + startTimeString + "&endtime=" + endTimeString + "&timestep=" + str(forecastTimeStep)
    response = requests.get(url, timeout=apiTimeout)

    rootMareoData = ET.fromstring(response.content)

    rawSeaLevelForecastMW = []
    rawSeaLevelForecastN2000 = []
    for i in range(len(rootMareoData)):
        try:
            if rootMareoData[i][0][2].text == 'SeaLevel':
                timeValueTuple = (rootMareoData[i][0][1].text, rootMareoData[i][0][3].text)
                rawSeaLevelForecastMW.append(timeValueTuple)
            elif rootMareoData[i][0][2].text == 'SeaLevelN2000':
                timeValueTuple = (rootMareoData[i][0][1].text, rootMareoData[i][0][3].text)
                rawSeaLevelForecastN2000.append(timeValueTuple)
            else:
                continue
        except:
            pass
    seaLevelForecastMW = []
    seaLevelForecastN2000 = []

    for i in rawSeaLevelForecastMW:
        time = datetime.datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%SZ")
        value = float(i[1])
        if not math.isnan(value):
            if unit == "mm":
                value = value * 100
            seaLevelForecastMW.append((time, value))

    for i in rawSeaLevelForecastN2000:
        time = datetime.datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%SZ")
        value = float(i[1])
        if not math.isnan(value):
            if unit == "mm":
                value = value * 100
            seaLevelForecastN2000.append((time, value))
    dataDict = {"SeaLevelMW": seaLevelForecastMW, "SeaLevelN2000": seaLevelForecastN2000}

    return dataDict

def get_observation(fmisid: int = DEFAULT_FMISID, unit: str = DEFAULT_UNIT, apiTimeout: int = API_TIMEOUT_IN_SECS, observationTimeStep: int = OBSERVATION_TIME_STEP, observationLengthHours: int = OBSERVATION_LENGTH_HOURS, observationOverlapHours: int = OBSERVATION_OVERLAP_HOURS):
    timeNow = datetime.datetime.utcnow()
    endTime = timeNow - datetime.timedelta(hours=observationOverlapHours)
    startTime = timeNow - datetime.timedelta(hours=observationLengthHours)
    startTimeString = startTime.isoformat(timespec="seconds") + "Z"
    endTimeString = endTime.isoformat(timespec="seconds") + "Z"

    url = BASE_URL + "&storedquery_id=" + OBSERVATION_QUERY_ID + "&fmisid=" + str(fmisid) + "&starttime=" + startTimeString + "&endtime=" + endTimeString + "&timestep=" + str(observationTimeStep)

    response = requests.get(url, timeout=apiTimeout)

    rootMareoData = ET.fromstring(response.content)

    rawSeaLevelObservationMW = []
    rawSeaLevelObservationN2000 = []
    for i in range(len(rootMareoData)):
        try:
            if rootMareoData[i][0][2].text == 'WATLEV':
                timeValueTuple = (rootMareoData[i][0][1].text, rootMareoData[i][0][3].text)
                rawSeaLevelObservationMW.append(timeValueTuple)
            elif rootMareoData[i][0][2].text == 'WLEVN2K_PT1S_INSTANT':
                timeValueTuple = (rootMareoData[i][0][1].text, rootMareoData[i][0][3].text)
                rawSeaLevelObservationN2000.append(timeValueTuple)
                #Ignoring N2000 data for now
                continue
            elif rootMareoData[i][0][2].text == 'TW':
                #Ignoring sea water temperature for now
                continue
            else:
                continue
        except:
            pass
    seaLevelObservationMW = []
    seaLevelObservationN2000 = []

    #Clean data and convert from mm to cm
    for i in rawSeaLevelObservationMW:
        time = datetime.datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%SZ")
        value = float(i[1])
        if not math.isnan(value):
            if unit == "cm":
                value = value / 10
            seaLevelObservationMW.append((time, value))
    
    for i in rawSeaLevelObservationN2000:
        time = datetime.datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%SZ")
        value = float(i[1])
        if not math.isnan(value):
            if unit == "cm":
                value = value / 10
            seaLevelObservationN2000.append((time, value))
    
    dataDict = {"SeaLevelMW": seaLevelObservationMW, "SeaLevelN2000": seaLevelObservationN2000}

    return dataDict

def get_sea_level_data(fmisid: int = DEFAULT_FMISID, unit: str = DEFAULT_UNIT, apiTimeout: int = API_TIMEOUT_IN_SECS, observationTimeStep: int = OBSERVATION_TIME_STEP, observationLengthHours: int = OBSERVATION_LENGTH_HOURS, observationOverlapHours: int = OBSERVATION_OVERLAP_HOURS, forecastTimeStep: int = FORECAST_TIME_STEP, forecastLengthHours: int = FORECAST_LENGTH_HOURS, forecastOverlapHours: int = FORECAST_OVERLAP_HOURS):
    observations = get_observation(fmisid, unit, apiTimeout, observationTimeStep, observationLengthHours, observationOverlapHours)
    forecasts = get_forecast(fmisid, unit, forecastOverlapHours, apiTimeout, forecastTimeStep, forecastLengthHours)
    seaLevelData = {"Forecasts": forecasts, "Observations": observations, "CurrentMW": observations["SeaLevelMW"][-1], "CurrentN2000": observations["SeaLevelN2000"][-1]}
    return seaLevelData




