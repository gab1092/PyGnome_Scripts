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

from gnome.utilities.distributions import UniformDistribution, WeibullDistribution

from datetime import datetime, timedelta

import gnome.scripting as gs

from gnome.outputters import NetCDFOutput

from gnome.weatherers import Evaporation, NaturalDispersion, Emulsification, Biodegradation, Dissolution
from gnome.environment import Water, Waves
#from gnome.movers import c_GridCurrentMover, c_GridWindMover
from gnome.movers import RandomMover3D, RiseVelocityMover

import numpy as np

# #%%
# mes=np.arange(1,13)
# anio=2019

mes=1
anio=2019


for ff in mes:
  
  nombre='Mistle_EXP1'

  start_time = datetime(anio, ff, 1, 3, 0, 0)
##cargando el archivo de costa 
  mymap = gs.MapFromBNA('/media/gabriela/WDBlue_2/CIGOM/GNOME/Costa.bna', refloat_halflife=1)
##cargando al modelo archivo de costa , viento etc
  model = gs.Model(start_time=start_time,
                 duration=timedelta(days=45),
                 time_step=gs.minutes(180),
                 map=mymap)


#%% MOVERS


  from gnome.movers import PyCurrentMover, PyWindMover

  # c_mover=PyCurrentMover.from_netCDF()


  # c_mover=PyCurrentMover.from_netCDF(files[12:13])


  model.movers += c_mover


  w_mover = PyWindMover.from_netCDF('/media/gabriela/WDBlue_2/CIGOM/GNOME/NCEP/ncep_global_2021.nc')

  model.movers += w_mover


#%% wind object para waves, evap, etc. MIsmo archivo, diferente forma de cargarlo.

  w_obj = gs.GridWind.from_netCDF('/media/gabriela/WDBlue_2/CIGOM/GNOME/NCEP/ncep_global_2021.nc')
  water = Water(temperature=300.0, salinity=35.0) #temperature in Kelvin, salinity in psu
  waves = Waves(wind=w_obj,water=water)

  model.environment += waves

  model.weatherers += Evaporation(wind=w_obj,water=water)
#model.weatherers += NaturalDispersion()
#model.weatherers += Emulsification(waves=waves)
#model.weatherers += Biodegradation(waves=waves)
# model.weatherers += Dissolution(waves,w_obj)



  random_mover = gs.RandomMover(diffusion_coef=100000, uncertain_factor=2) 
  model.movers += random_mover      


  random_mover_3d = RandomMover3D(vertical_diffusion_coef_above_ml=30,vertical_diffusion_coef_below_ml=0.22,
                                horizontal_diffusion_coef_above_ml=100000,horizontal_diffusion_coef_below_ml=126,
                                mixed_layer_depth=20,surface_is_allowed=True) # Default is False 
  model.movers += random_mover_3d

  rise_vel_mover = RiseVelocityMover()
  model.movers += rise_vel_mover

#%% DATOS DEL DERRAME

  substance=gs.GnomeOil(filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/isthmus-phillips_AD00577.json')


  spill= gs.surface_point_line_spill(substance=gs.GnomeOil(filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/isthmus-phillips_AD00577.json'), num_elements=9000, amount=90000, units='bbls',
                                      release_time=start_time,start_position=(-94.0592,18.8572,400),end_release_time=start_time+timedelta(days=10))

# wd = WeibullDistribution(alpha=1.8,
#                               lambda_=.00456,
#                               min_=.0002)  # 200 micron min
#ud = UniformDistribution(10e-6,300e-6) #droplets in the range 10-300 microns
# spill = gs.subsurface_plume_spill(num_elements=10000,
#                                     start_position=(-94.0592,18.8572,15),
#                                      release_time=start_time,
#                                     distribution=wd,
#                                     end_release_time= start_time + timedelta(days=10),
#                                     amount=30000,
#                                      substance=gs.GnomeOil(filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/isthmus_AD00578.json'),
#                                      units='bbl',
#                                      name='My spill')
# #filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/maya-exxon_AD00734.json'



  model.spills += spill


#%%para guardarlo



  salida1='/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/' + nombre + '_' + str(ff) + '_' + str(anio)

  cond=os.path.isdir(salida1)

  if cond==True:
    
     print('El directorio ya existe, se va a sobreescribir')

  else:
        os.mkdir('/media/gabriela/WDBlue_2/CIGOM/GNOME/Resultados/' + nombre + '_' + str(ff) + '_' + str(anio))
        print('Nuevo directorio creado')
        
        
  os.chdir(salida1)

  renderer = gs.Renderer(output_dir=salida1,
                       map_filename=('/media/gabriela/WDBlue_2/CIGOM/GNOME/Costa.bna'),
                       output_timestep=gs.hours(6))
  model.outputters += renderer

#Esta salida genera un shape para que pueda cargarse en un zip
  shape_file = os.path.join(salida1 + '/'+ nombre + '_' + str(ff) + '_' + str(anio) +'shape')

  model.outputters += gs.ShapeOutput(shape_file,
                                zip_output=True,surface_conc='kde',
                                output_timestep=gs.hours(6))


##Esta salida genera un netcdf
  model.outputters += renderer
  netcdf_file = os.path.join(salida1 + '/'+ nombre + '_' + str(ff) + '_' + str(anio) + '.nc')
                           
  gs.remove_netcdf(netcdf_file)
  model.outputters += NetCDFOutput(netcdf_file,
                                     which_data='most',
                                     # output most of the data associated with the elements
                                     output_timestep=timedelta(hours=6))

  model.outputters += gs.OilBudgetOutput()
  model.outputters += gs.WeatheringOutput(os.path.join(salida1, 'WeatheringOutput'))


#%%Para correr el modelo
  model.full_run()














