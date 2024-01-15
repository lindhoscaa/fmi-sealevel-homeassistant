from FMIMareoLibrary import get_sea_level_data
import matplotlib.pyplot as plt

seaLevelData = get_sea_level_data(fmisid=134253, observationLengthHours=2, forecastLengthHours=2, timeZone="AUTO")

print(f"Current MW: {seaLevelData['CurrentMW']}, Current N2000: {seaLevelData['CurrentN2000']}")
print("ObservationsMW:")
for i in seaLevelData['Observations']['SeaLevelMW']:
    print(i)

print("ObservationsN2000:")
for i in seaLevelData['Observations']['SeaLevelN2000']:
    print(i)

print("ForecastsMW:")
for i in seaLevelData['Forecasts']['SeaLevelMW']:
    print(i)

print("ForecastsN2000:")
for i in seaLevelData['Forecasts']['SeaLevelN2000']:
    print(i)

#Plotting
plt.plot([i[0] for i in seaLevelData['Observations']['SeaLevelMW']], [i[1] for i in seaLevelData['Observations']['SeaLevelMW']], label="Observations MW")
plt.plot([i[0] for i in seaLevelData['Observations']['SeaLevelN2000']], [i[1] for i in seaLevelData['Observations']['SeaLevelN2000']], label="Observations N2000")
plt.plot([i[0] for i in seaLevelData['Forecasts']['SeaLevelMW']], [i[1] for i in seaLevelData['Forecasts']['SeaLevelMW']], label="Forecasts MW")
plt.plot([i[0] for i in seaLevelData['Forecasts']['SeaLevelN2000']], [i[1] for i in seaLevelData['Forecasts']['SeaLevelN2000']], label="Forecasts N2000")
plt.legend()
plt.show()



