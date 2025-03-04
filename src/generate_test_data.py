import numpy as np
import xarray as xr
import s3fs
import zarr
from datetime import datetime, timedelta

def generate_test_data():
    # Create coordinates
    lat = np.linspace(30, 40, 100)  # 30°N to 40°N
    lon = np.linspace(130, 140, 100)  # 130°E to 140°E
    
    # Create time array with daily resolution first
    daily_times = np.arange('2023-01-01', '2024-01-01', dtype='datetime64[D]')
    # Convert to nanosecond precision after creating the array
    time = daily_times.astype('datetime64[ns]')

    # Create grid and adjust dimensions for broadcasting
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    lat_grid = lat_grid[np.newaxis, :, :]
    lon_grid = lon_grid[np.newaxis, :, :]

    # Calculate time component using daily resolution
    days = np.arange(len(daily_times)) % 365
    time_component = np.sin(2 * np.pi * days / 365)[:, np.newaxis, np.newaxis]

    # Generate temperature data with correct broadcasting
    temperature = (15 + 
                  10 * time_component +
                  5 * np.cos(np.pi * (lat_grid - 35) / 10) +
                  2 * np.sin(np.pi * (lon_grid - 135) / 10))

    # Generate humidity data
    humidity = (65 + 
               15 * time_component +
               10 * np.cos(np.pi * (lat_grid - 35) / 10) +
               5 * np.sin(np.pi * (lon_grid - 135) / 10))

    # Generate pressure data
    pressure = (1013 + 
               10 * time_component +
               5 * np.cos(np.pi * (lat_grid - 35) / 10))

    # Create dataset
    ds = xr.Dataset(
        {
            'temperature': (['time', 'latitude', 'longitude'], temperature),
            'humidity': (['time', 'latitude', 'longitude'], humidity),
            'pressure': (['time', 'latitude', 'longitude'], pressure)
        },
        coords={
            'time': time,
            'latitude': lat,
            'longitude': lon
        },
        attrs={
            'description': 'Example Weather Dataset',
            'creator': 'Test Data Generator',
            'created_at': datetime.now().isoformat(),
            'variables': {
                'temperature': 'Temperature (°C)',
                'humidity': 'Relative Humidity (%)',
                'pressure': 'Pressure (hPa)'
            }
        }
    )

    return ds

if __name__ == "__main__":
    # Generate data
    ds = generate_test_data()

    # Configure MinIO connection
    fs = s3fs.S3FileSystem(
        endpoint_url="http://minio:9000",
        key="minioadmin",
        secret="minioadmin",
        use_ssl=False
    )

    # Ensure bucket exists
    bucket = "testdata"
    try:
        fs.mkdir(bucket)
    except:
        pass

    # Save as Zarr format
    store = s3fs.S3Map(f"{bucket}/weather.zarr", s3=fs)
    ds.to_zarr(store, mode='w')

    print("Test data has been generated and uploaded to MinIO")