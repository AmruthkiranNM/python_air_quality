import pandas as pd

def process_pollutant_data(pollutants):
    df = pd.DataFrame(pollutants, index=[0])

    readable_names = {
        'co': 'Carbon Monoxide (CO)',
        'no': 'Nitric Oxide (NO)',
        'no2': 'Nitrogen Dioxide (NO₂)',
        'o3': 'Ozone (O₃)',
        'so2': 'Sulfur Dioxide (SO₂)',
        'pm2_5': 'Particulate Matter <2.5µm (PM2.5)',
        'pm10': 'Particulate Matter <10µm (PM10)',
        'nh3': 'Ammonia (NH₃)'
    }

    df.rename(columns=readable_names, inplace=True)
    return df.round(2)
