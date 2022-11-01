#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 10:46:03 2022

@author: gabriela
"""

##Código para correr la simulación de derrame con PyGnome considerando biodegradación, emulsificación, 
##dispersión natural y evaporación

 #%%

 
import os



from datetime import datetime, timedelta
import gnome
import gnome.scripting as gs
from gnome.outputters import NetCDFOutput
from gnome.weatherers import Evaporation, NaturalDispersion, Emulsification, Biodegradation
from gnome.environment import Water, Waves
from gnome.movers import GridCurrentMover, GridWindMover
from gnome.movers import Ran/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/domMover, RandomMover3D

 
#%%
anio=2021

start_time = datetime(anio, 1, 1, 0, 0, 0)
##cargando el archivo de costa 
mymap = gs.MapFromBNA('/media/gabriela/WDBlue_2/CIGOM/GNOME/Costa.bna', refloat_halflife=1)
##cargando al modelo archivo de costa , viento etc
model = gs.Model(start_time=start_time,
                 duration=timedelta(days=10),
                 time_step=90*10,
                 map=mymap)


#%% MOVERS
#para un archivo netcdf:
c_mover=GridCurrentMover('/media/gabriela/WDBlue_2/CIGOM/datos_NCOM3km/NCOM-GAMSEAS-DAILY-20210101.nc')
model.movers += c_mover
##para una lista de archivos y funciona de forma similar para viento
file=gs.get_datafile(r'/media/gabriela/WDBlue_2/CIGOM/NCOM_3km.txt')
c_mover = GridCurrentMover(file)
model.movers += c_mover


w_mover = GridWindMover('/media/gabriela/WDBlue_2/CIGOM/GNOME/NCEP/ncep_global_c651_b4fe_659c.nc')
model.movers += w_mover

#%% wind object para waves, evap, etc. MIsmo archivo, diferente forma de cargarlo.

w_obj = gs.GridWind.from_netCDF('/media/gabriela/WDBlue_2/CIGOM/GNOME/NCEP/ncep_global_c651_b4fe_659c.nc')
water = Water(300,35) #temperature in Kelvin, salinity in psu
waves = Waves(wind=w_obj,water=water)

model.weatherers += Evaporat/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/ion(wind=w_obj,water=water)
model.weatherers += NaturalDispersion(waves=waves,water=water)
model.weatherers += Emulsification(waves=waves)
model.weatherers += Biodegradation(waves=waves)

random_mover = RandomMover(diffusion_coef=10000) 
model.movers += random_mover

random_mover_3d = RandomMover3D(vertical_diffusion_coef_above_ml=10,vertical_diffusion_coef_below_ml=0.2,\
mixed_layer_depth=10) #diffusion coefficients in cm/s, MLD in meters
model.movers += random_mover_3d

#%% DATOS DEL DERRAME


release= gnome.spill.spill.surface_point_line_spill(substance='AD00730',
                                     amount=10000,num_elements=2000, units='bbls',
                                     release_time=start_time,
                                     start_position=(-92.154299,19.378562,57),
                                     end_release_time=start_time+timedelta(days=3))

model.spills += release


#%%para guardarlo


os.chdir('/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/')

salida1='/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/'+str(anio)

renderer = gs.Renderer(output_dir=salida1,
                       map_filename=('/media/gabriela/WDBlue_2/CIGOM/GNOME/Costa.bna'),
                       output_timestep=gs.hours(1))

#Esta salida genera un shape para que pueda cargarse en un zip
model.outputters += renderer
model.outputters += gs.ShapeOutput(('/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/'+str(anio)+'shape'),
                                zip_output=True,
                                output_timestep=gs.hours(1))


##Esta salida genera un netcdf
model.outputters += renderer
netcdf_file = os.path.join('/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/'+str(anio)+'.nc')
                           
gs.remove_netcdf(netcdf_file)
model.outputters += NetCDFOutput(netcdf_file,
                                     which_data='most',
                                     # output most of the data associated with the elements
                                     output_timestep=timedelta(hours=1))

#%%Para correr el modelo
model.full_run()














