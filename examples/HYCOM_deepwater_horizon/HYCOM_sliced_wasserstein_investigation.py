import os
from datetime import date, timedelta
from configparser import ConfigParser
import h5py
import numpy as np
import matplotlib.pyplot as plt

from PYOPATRA import *


if __name__ == '__main__':
    # Configuration settings
    # In hours
    time_delta = 1
    # Particle release per timedelta
    num_particles = 10
    # True particle release location
    true_particle_lon = -88.365997
    true_particle_lat = 28.736628
    # Starting particle release location
    particle_lon = -88.0
    particle_lat = 28.6
    prev_loc = np.array((particle_lat, particle_lon))
    proposed_loc = np.array((particle_lat, particle_lon))
    # Time elapsed
    total_days = 8 * 7
    total_time_steps = int(24 / time_delta * total_days) - 4
    # When to add particles (time steps, not hours)
    add_particles_time_step_interval = 3
    # How frequently to save particles (time steps, not hours)
    particle_save_interval = 3
    # Number of Particles at the end
    total_particles = (total_time_steps // add_particles_time_step_interval + 1) * num_particles
    # Frame interval
    frame_interval = 3
    # For the Wasserstein investigation
    num_to_try = 1000
    obj_values = np.zeros(num_to_try)
    num_proj = 5000

    times = ['000', '003', '006', '009', '012', '015', '018', '021']
    start_date = date(2010, 4, 20)

    file_prefix = os.path.dirname(os.path.realpath(__file__))
    hycom_files = []

    for days_since_start in range(total_days):
        date = start_date + timedelta(days=days_since_start)

        for time_index, time_str in enumerate(times):
            file = '{}/data/hycom_gomu_501_{}{:02d}{:02d}00_t{}.nc'.format(file_prefix, date.year, date.month, date.day, time_str)
            hycom_files.append(file)

    print('Reading HYCOM files....')
    # Read HYCOM files
    hfp = HYCOMFileParser()
    hfp.read(hycom_files, diffusion_coefficient=10.0)

    print('Setting up mesh...')
    # Set up 2D Triangular Mesh
    tm2d = TriangularMesh2D()
    tm2d.setup_mesh(hfp, 2)

    # Set up objective function
    with h5py.File("{}/data/observed_particles.hdf5".format(file_prefix), "r") as fp:
        obs_particles_temp = fp['particles'][:, :]

    obs_particles = obs_particles_temp[~np.all(obs_particles_temp == 0, axis=1)]
    tm2d.setup_objective_function(obs_particles,
                                  num_bins_lat_long=[700, 1000],
                                  bounds=[hfp.latitude[0], hfp.latitude[-1], hfp.longitude[0], hfp.longitude[-1]],
                                  num_proj=num_proj)

    previous_log_likelihood = 0
    previous_obj_value = 0
    accepted = 0

    print('Time stepping...')
    current_num_particles = 0
    frame = 0
    # Time stepping
    for i in range(total_time_steps):
        # print('Time step {}'.format(i))

        # Inject more particles
        if i % add_particles_time_step_interval == 0:
            for j in range(num_particles):
                tm2d.append_particle(proposed_loc)
                current_num_particles += 1

        tm2d.time_step(time_delta)

    for i in range(num_to_try):
        print(i)
        obj_values[i] = tm2d.get_objective_value()

    plt.hist(obj_values)

    plt.savefig('wasserstein_hist_{}_proj.png'.format(num_proj), dpi=300)