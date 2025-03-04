# Weather Data Service with MinIO, FastAPI, and Zarr
A prototype service demonstrating distributed storage and querying of meteorological data using modern technology stack.

## Overview
This project explores the integration of:
- MinIO : Distributed object storage
- Zarr : Efficient multi-dimensional array format
- FastAPI : High-performance REST API framework

## Features
- Distributed data storage with MinIO
- Parallel data access with Zarr format
- RESTful API with automatic documentation
- Nearest neighbor interpolation
- Multi-variable and time-series queries
- Docker containerization

## Steps
### 1. Prerequisites Installation
Install Docker
Install docker-compose

### 2. Project Setup
Create project directory and Create sub-directory of src 
weather-zarr-minio
├── src/
│   ├── main.py              # FastAPI application
│   └── generate_test_data.py # Test data generator
├── Dockerfile               # Container configuration
├── docker-compose.yml      # Multi-container setup
├── requirements.txt        # Python dependencies
└── README.md              # Documentation

Create required files
- Place main.py and generate_test_data.py in the src directory
- Create requirements.txt in the project root

### 3. Docker Configuration
In the project directory:

Create Dockerfile

Create docker-compose.yml

### 4. Deployment Steps
1. Create project directory and copy all files to appropriate locations.
2. Start services:
   docker-compose up --build

### 5. Service Access
After services start, you can access through the following addresses:

- MinIO Console: http://localhost:9001
  - Username: minioadmin
  - Password: minioadmin
- API Service: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 6. API Usage Examples
1. Query all data for a specific location:
curl "http://localhost:8000/data/testdata/weather.zarr?lat=35.6762&lon=139.6503"
2. Query specific variables:
curl "http://localhost:8000/data/testdata/weather.zarr?lat=35.6762&lon=139.6503&variables=temperature,humidity"
3. Query data for a specific time:
curl "http://localhost:8000/data/testdata/weather.zarr?lat=35.6762&lon=139.6503&time=2023-07-01"
4. View dataset metadata:
curl "http://localhost:8000/metadata/testdata/weather.zarr"

### 7. Dataset Characteristics
The generated test dataset includes:

1. Spatial Coverage:   
   - Latitude: 30°N - 40°N (100 points)
   - Longitude: 130°E - 140°E (100 points)
2. Temporal Coverage:   
   - Daily data for the entire year 2023
3. Variables:   
   - temperature: baseline 15°C, annual variation ±10°C
   - humidity: baseline 65%, annual variation ±15%
   - pressure: baseline 1013hPa, annual variation ±10hPa
4. Data Characteristics:   
   - Includes seasonal variations
   - Includes spatial gradients
   - Data resolution: 100x100 grid points
   
### 8. Important Notes
1. Ensure Docker and Docker Compose are properly installed
2. Test data will be automatically generated on first startup
3. Data queries support nearest neighbor interpolation
4. API supports cross-time and multi-variable queries
5. All data is stored in MinIO and persisted

## 🔧 Use Cases
- Weather data distribution systems
- Climate analysis applications
- Environmental monitoring services
- Scientific data platforms
- Geospatial data services
## 📝 License
MIT License
