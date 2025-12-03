import cdsapi

dataset = "reanalysis-era5-pressure-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": ["geopotential"],
    "year": ["2024"],
    "month": ["04"],
    "day": ["01"],
    "time": ["13:00"],
    "pressure_level": ["1000"],
    "data_format": "grib",
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
