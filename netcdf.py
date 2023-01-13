#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Archivo para preparar los datos diarios de HYCOM en archivos mensuales, sin datos duplicados para poder usarlos en PyGnome

Created on Wed Nov 30 09:43:01 2022

@author: gabriela
"""

# import netCDF4
# import numpy
import numpy as np
import xarray as xr

mes=np.arange(1,13)

anio=np.arange(2018,2023)

for anio1 in anio:


 for ff in mes:

   ds = xr.open_mfdataset('/media/gabriela/DATOS_RESENDIZ1/CIGOM/hycom_4km/HYCOM-DAILY-' + str(anio1) + ('{:02}'.format(ff))+ '*.nc',
                           combine='nested',concat_dim='time')

   ds2=ds.drop_duplicates(dim="time")
   
   lon=ds2['longitude'].values-360
   ds2['longitude']=lon

   ds2.to_netcdf('/media/gabriela/WDBlue_2/CIGOM/HYCOM_MENSUALES/HYCOM_' + str(anio1) + ('{:02}'.format(ff)) + '.nc',format='NETCDF3_64BIT')
   ds2.close()


#revisando las longitudes en el netcdf


#ds=xr.open_dataset('/media/gabriela/WDBlue_2/CIGOM/HYCOM_MENSUALES/HYCOM_' + str(anio1) + ('{:02}'.format(ff)) + '.nc')

# lon=ds['longitude'].values-360
# ds['longitude']=lon

# ds.to_netcdf('/media/gabriela/WDBlue_2/CIGOM/HYCOM_MENSUALES/HYCOM_' + str(anio1) + str(ff) + '.nc',format='NETCDF3_64BIT')
# ds.close()

