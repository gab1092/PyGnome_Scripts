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
from gnome.utilities.distributions import UniformDistribution
from datetime import datetime, timedelta
import gnome.scripting as gs
from gnome.outputters import NetCDFOutput
from gnome.weatherers import Evaporation, NaturalDispersion, Emulsification, Biodegradation, Dissolution
from gnome.environment import Water, Waves
#from gnome.movers import c_GridCurrentMover, c_GridWindMover
from gnome.movers import RandomMover3D, RiseVelocityMover



#%%
anio=2022

start_time = datetime(anio, 1, 1, 12, 0, 0)
##cargando el archivo de costa 
mymap = gs.MapFromBNA('/media/gabriela/WDBlue_2/CIGOM/GNOME/Costa.bna', refloat_halflife=1)
##cargando al modelo archivo de costa , viento etc
model = gs.Model(start_time=start_time,
                 duration=timedelta(days=4),
                 time_step=gs.minutes(60),
                 map=mymap)


#%% MOVERS
#para un archivo netcdf:
# file=gs.get_datafile(r'/media/gabriela/WDBlue_2/CIGOM/NCOM_3km.txt')
# c_mover =c_GridCurrentMover(files)
# c_mover=PyCurrentMover(files)

# mover = gs.PyGridCurrentMover(fidef list_full_paths(directory):

    
# def list_full_paths(directory):
#     return [os.path.join(directory, file) for file in os.listdir(directory)]

# files=(list_full_paths((r'/media/gabriela/WDBlue_2/CIGOM/hycom_4km/')))
# files.reverse()


from gnome.movers import PyCurrentMover, PyWindMover

c_mover=PyCurrentMover.from_netCDF('/media/gabriela/WDBlue_2/CIGOM/HYCOM_combined.nc')
model.movers += c_mover


w_mover = PyWindMover.from_netCDF('/media/gabriela/WDBlue_2/CIGOM/GNOME/NCEP/ncep_global_c651_b4fe_659c.nc')

model.movers += w_mover


#%% wind object para waves, evap, etc. MIsmo archivo, diferente forma de cargarlo.
w_obj = gs.GridWind.from_netCDF('/media/gabriela/WDBlue_2/CIGOM/GNOME/NCEP/ncep_global_c651_b4fe_659c.nc')
water = Water(temperature=300.0, salinity=35.0) #temperature in Kelvin, salinity in psu
waves = Waves(wind=w_obj,water=water)

model.environment += waves

model.weatherers += Evaporation(wind=w_obj,water=water)
model.weatherers += NaturalDispersion(waves=waves,water=water)
model.weatherers += Emulsification(waves=waves)
model.weatherers += Biodegradation(waves=waves)
model.weatherers += Dissolution(waves,w_obj)



random_mover = gs.RandomMover(diffusion_coef=100000, uncertain_factor=2) 
model.movers += random_mover      


random_mover_3d = RandomMover3D(vertical_diffusion_coef_above_ml=10,vertical_diffusion_coef_below_ml=0.22,
                                horizontal_diffusion_coef_above_ml=100000,horizontal_diffusion_coef_below_ml=126,
                                mixed_layer_depth=15,surface_is_allowed=True) # Default is False 
model.movers += random_mover_3d

rise_vel_mover = RiseVelocityMover()
model.movers += rise_vel_mover

#%% DATOS DEL DERRAME

substance=gs.GnomeOil(filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/alaska-north-slope_AD00020.json')

spill= gs.surface_point_line_spill(substance=substance, num_elements=1000, amount=1000, units='bbls',
                                       release_time=start_time,start_position=(-92.154299,19.378562,0),
                                      end_release_time=start_time+timedelta(days=3))

# ud = UniformDistribution(10e-6,300e-6) #droplets in the range 10-300 microns
# spill = gs.subsurface_plume_spill(num_elements=10000,
#                                 start_position=(-94.0592,18.8572,20),
#                                 release_time=start_time,
#                                 distribution=ud,
#                                 distribution_type='droplet_size',
#                                 end_release_time= start_time + timedelta(days=3),
#                                 amount=10000,
#                                 substance=gs.GnomeOil(filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/isthmus_AD00578.json'),
#                                 units='bbl',
#                                 name='My spill')
# #filename='/media/gabriela/WDBlue_2/CIGOM/GNOME/maya-exxon_AD00734.json'

model.spills += spill


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














