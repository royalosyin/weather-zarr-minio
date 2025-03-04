from fastapi import FastAPI, HTTPException, Query
import xarray as xr
import s3fs
import zarr
import numpy as np
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Weather Data Query Service")

# Configure MinIO connection
fs = s3fs.S3FileSystem(
    endpoint_url="http://minio:9000",
    key="minioadmin",
    secret="minioadmin",
    use_ssl=False
)

@app.get("/data/{bucket}/{zarr_path}")
async def get_point_data(
    bucket: str,
    zarr_path: str,
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    variables: str = Query(None, description="List of variables to query (comma-separated)"),
    time: Optional[str] = Query(None, description="Time (YYYY-MM-DD)")
):
    try:
        store_path = f"{bucket}/{zarr_path}"
        store = s3fs.S3Map(store_path, s3=fs)
        ds = xr.open_zarr(store)
        
        # Handle variables input
        if variables is None:
            variables_list = list(ds.data_vars)
        else:
            variables_list = [v.strip() for v in variables.split(',')]
            invalid_vars = [var for var in variables_list if var not in ds.data_vars]
            if invalid_vars:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid variables: {', '.join(invalid_vars)}. Available variables are: {', '.join(ds.data_vars)}"
                )

        # Get nearest coordinates first
        nearest_lat = float(ds.latitude.sel(latitude=lat, method="nearest").item())
        nearest_lon = float(ds.longitude.sel(longitude=lon, method="nearest").item())
        
        # Extract data
        result = {
            "latitude": nearest_lat,
            "longitude": nearest_lon,
            "values": {}
        }
        
        for var in variables_list: 
            try:
                data = ds[var].sel(
                    latitude=lat,
                    longitude=lon,
                    method="nearest"
                )
                
                if 'time' in data.dims:
                    if time is None:
                        result["values"][var] = {
                            str(t.item()): float(data.sel(time=t).item())
                            for t in data.time
                        }
                    else:
                        try:
                            time_data = data.sel(time=np.datetime64(time))
                            result["values"][var] = float(time_data.item())
                        except ValueError as e:
                            raise HTTPException(status_code=400, detail=f"Invalid time format: {str(e)}")
                else:
                    result["values"][var] = float(data.item())
            except Exception as e:
                result["values"][var] = f"Failed to get data: {str(e)}"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata/{bucket}/{zarr_path}")
async def get_metadata(bucket: str, zarr_path: str):
    try:
        store_path = f"{bucket}/{zarr_path}"
        store = s3fs.S3Map(store_path, s3=fs)
        ds = xr.open_zarr(store)
        
        return {
            "variables": list(ds.data_vars),
            "dimensions": {dim: len(ds[dim]) for dim in ds.dims},
            "coordinates": {
                "latitude": {
                    "min": float(ds.latitude.min()),
                    "max": float(ds.latitude.max())
                },
                "longitude": {
                    "min": float(ds.longitude.min()),
                    "max": float(ds.longitude.max())
                },
                "time": {
                    "start": str(ds.time[0].item()),
                    "end": str(ds.time[-1].item())
                } if 'time' in ds.dims else None
            },
            "attributes": ds.attrs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise
