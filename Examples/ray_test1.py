#!/usr/bin/env python3
#M
#M Old Name :
#M   ray_test1.m
#M
#M New Name ray_test1.py
#M
#M Purpose :
#M   Example of using raytrace_2d for a fan of rays. Ray trajectories are
#M   plotted over the ionosphere which has been generated by IRI 2016.
#M
#M Calling sequence :
#M   ray_test1
#M
#M Inputs :
#M   None
#M
#M Outputs :
#M   None
#M
#M Change log:
#M   V1.0  M.A. Cervera  18/04/2008
#M     Initial Version
#M
#M   V1.1  M.A. Cervera  13/05/2008
#M     Rays and ionosphere plotted on an arc to preserved curved Earth
#M     geometry. Image printed to encapsulated postscript and PNG.
#M
#M   V1.2  M.A. Cervera  15/12/2008
#M     Now uses IRI 2007 to generate the ionosphere.
#M
#M   V1.3  M.A. Cervera  19/05/2011
#M      More efficient handling of ionospheric grids in call to raytrace_2d
#M
#M   V1.4  M.A. Cervera  02/05/2016
#M      Updated to use IRI2016
#M
#M   V1.5  M.A. Cervera  20/05/2016
#M      Updated to use multi-threaded raytrace_2d
#M
#   Change to python W. C. Liles 08/06/2020
#       All original comments have been kept an are marked as #M
#         New comments start with #
#       All ; were remove
#       
#M
#M
import numpy as np  # py
import time
import ctypes as c


from pylap.raytrace_2d import raytrace_2d 
from Ionosphere import gen_iono_grid_2d as gen_iono
from Plotting import plot_ray_iono_slice as plot_iono

#import raytrace_2d as raytrace
import matplotlib.pyplot as plt
#M
#M setup general stuff
#M
UT = [2001, 3, 15, 7, 0]#2001,3,15,14,15 makes 7:00UT    #M UT - year, month, day, hour, minute
#  The above is not a standare Python datetime object but leaving unchanged
R12 = 100                    #M R12 index
speed_of_light = 2.99792458e8
  
#elevs = [2:2:60]             #M initial ray elevation
elevs = np.arange(2, 62, 2, dtype = float) # py
# num_elevs = length(elevs)
num_elevs = len(elevs)
freq = 15.0                  #M ray frequency (MHz)
# freqs = freq.*ones(size(elevs))
freqs = freq * np.ones(num_elevs, dtype = float) # py
ray_bear = 324.7             #M bearing of rays
origin_lat = -23.5           #M latitude of the start point of ray
origin_long = 133.7          #M longitude of the start point of ray
#tol = [1e-7 .01 10]          #M ODE tolerance and min/max step sizes
tol = [1e-7, 0.01, 10] # py
nhops = 1                    #M number of hops to raytrace
doppler_flag = 1             #M generate ionosphere 5 minutes later so that
                             #M Doppler shift can be calculated
irregs_flag = 0              #M no irregularities - not interested in
                             #M Doppler spread or field aligned irregularities
kp = 0                       #M kp not used as irregs_flag = 0. Set it to a
                             #M dummy value

#fprintf( ['\n' ...
#  'Example of 2D numerical raytracing for a fan of rays for a WGS84 ellipsoidal' ...
#  ' Earth\n\n'])
print('\n'
       'Example of 2D numerical raytracing for a fan of rays for a WGS84'
       ' ellipsoidal Earth\n\n') # py

#M
#M generate ionospheric, geomagnetic and irregularity grids
#M
max_range = 10000       #M maximum range for sampling the ionosphere (km)
num_range = 201        #M number of ranges (must be < 2000)
# range_inc = max_range ./ (num_range - 1)   #M range cell size (km)
range_inc = max_range / (num_range - 1) # py
start_height = 0        #M start height for ionospheric grid (km)
height_inc = 3          #M height increment (km)
num_heights = 200      #M number of  heights (must be < 2000)

# clear iri_options
#iri_options.Ne_B0B1_model = 'Bil-2000'  #M this is a non-standard setting for
                                        #M IRI but is used as an example
# implement the above by means of dictionay
iri_options = {
               'Ne_B0B1_model': 'Bil-2000'
              }   # py
# tic
tic = time.time() # py
print('Generating ionospheric grid... ')
iono_pf_grid, iono_pf_grid_5, collision_freq, irreg, iono_te_grid = \
    gen_iono.gen_iono_grid_2d(origin_lat, origin_long, R12, UT, ray_bear,
             max_range, num_range, range_inc, start_height,
		     height_inc, num_heights, kp, doppler_flag, 'iri2016',
		     iri_options)

# toc

#M convert plasma frequency grid to  electron density in electrons/cm^3
iono_en_grid = (iono_pf_grid ** 2) / 80.6164e-6
iono_en_grid_5 = (iono_pf_grid_5 ** 2) / 80.6164e-6


toc = time.time() # py
elasped_time = toc - tic


#M
#M Example 1 - Fan of rays, 10 MHz, single hop. Print to encapsulated
#M postscript and PNG. Note the transition from E-low to E-High to F2-low modes.
#M

#M call raytrace for a fan of rays
#M first call to raytrace so pass in the ionospheric and geomagnetic grids
print('Generating {} 2D NRT rays ...'.format(num_elevs))
tic = time.time()

ray_data, ray_path_data, ray_path_state = \
   raytrace_2d(origin_lat, origin_long, elevs, ray_bear, freqs, nhops,
               tol, irregs_flag, iono_en_grid, iono_en_grid_5,
 	       collision_freq, start_height, height_inc, range_inc, irreg)

toc = time.time()

start_range = 0
start_range_idx = int(start_range/range_inc)
end_range = 3000
end_range_idx = int((end_range) / range_inc) + 1
start_ht = start_height
start_ht_idx = 0
end_ht = 400
end_ht_idx = int(end_ht / height_inc) + 1
iono_pf_subgrid = iono_pf_grid[start_ht_idx:end_ht_idx,start_range_idx:end_range_idx]


ax, ray_handle = plot_iono.plot_ray_iono_slice(iono_pf_subgrid, start_range,
                      end_range, range_inc, start_ht, end_ht, height_inc,
                      ray_path_data,linewidth=1.5, color=[1, 1, 0.99])
# 

fig_str_a = '{}/{}/{}  {:02d}:{:02d}UT   {}MHz   R12 = {}'.format(
              UT[1], UT[2], UT[0], UT[3], UT[4], freq, R12)
fig_str_b = '   lat = {}, lon = {}, bearing = {}'.format(
             origin_lat, origin_long, ray_bear)

fig_str = fig_str_a + fig_str_b

ax.set_title(fig_str)
plt.show()




#M
#M Example 2 - Fan of rays, 3 hops, 30 MHz
#M

#M call raytrace
# nhops = 3            #M number of hops
# freqs = 30 *np.ones(elevs.size)
# ray_data, ray_path_data,ray_path_state = \
#     raytrace_2d(origin_lat, origin_long, elevs, ray_bear, freqs, 
#     nhops, tol, irregs_flag)
       
# #M plot the rays

# start_range = 0
# start_range_idx = int(start_range / range_inc) + 1
# end_range = 7000
# end_range_idx = int(end_range / range_inc) + 1
# start_ht = start_height
# start_ht_idx = 1
# end_ht = 597
# end_ht_idx = int(end_ht / height_inc) + 1
# iono_pf_subgrid = iono_pf_grid[start_ht_idx:end_ht_idx,start_range_idx:end_range_idx]

# ax2, ray_handle2 = plot_iono.plot_ray_iono_slice(iono_pf_subgrid, start_range,
#                       end_range, range_inc, start_ht, end_ht, height_inc,
#                       ray_path_data,linewidth=1.5, color='w')

# freq = freqs[0]
# fig_str_a = '{}/{}/{}  {:02d}:{:02d}UT   {}MHz   R12 = {}'.format(
#               UT[2], UT[1], UT[0], UT[3], UT[4], freq, R12)
# fig_str_b = '   lat = {}, lon = {}, bearing = {}'.format(
#              origin_lat, origin_long, ray_bear)
# fig_str = fig_str_a + fig_str_b
# ax2.set_title(fig_str)


# #M plot three rays only


# # iono_pf_subgrid = iono_pf_grid[start_ht_idx:end_ht_idx,start_range_idx:end_range_idx]
# # ax3, ray_handle3 = plot_iono.plot_ray_iono_slice(iono_pf_subgrid, start_range,
# #                     end_range, range_inc, start_ht, end_ht, height_inc,
# #                     ray_path_data[0:3],linewidth=1.5, color='w')
# # ray_handle3[0][0].set_linestyle('--')
# # ray_handle3[1][0].set_linestyle(':')
# # ax3.set_title(fig_str)

# # print('\n')
# #  plt.show()
