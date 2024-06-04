#!/usr/bin/env python

from copy import deepcopy
from project2_base import *
from filterpy.kalman import KalmanFilter
import numpy as np

from traffic.drawing import countries
from traffic.core.projection import Mercator

from geopy.distance import geodesic

import matplotlib.pyplot as plt

#############################

dt = 10 # radar measure sample time in seconds

def initFilter():
    sigma_p = 1.5 # Acceleration is a Gaussian random vars with a stdev of 1.5 m/s^2
    sigma_o = 100 # Measurement uniform standard deviation

    # Transition matrix (see state in dt seconds)
    F = np.array([
        [ 1, 0, dt, 0 ],
        [ 0, 1, 0, dt ],
        [ 0, 0, 1, 0 ],
        [ 0, 0, 0, 1 ]
    ])

    # Observation transformation matrix
    H = np.array([
        [ 1, 0, 0, 0 ],
        [ 0, 1, 0, 0 ]
    ])

    # Process noise matrix
    Q = np.array([
        [ 0.25*pow(dt, 4), 0, 0.5*pow(dt, 3), 0 ],
        [ 0, 0.25*pow(dt, 4), 0, 0.5*pow(dt, 3) ],
        [ 0.5*pow(dt, 3), 0, pow(dt, 2), 0 ],
        [ 0, 0.5*pow(dt, 3), 0, pow(dt, 2) ]
    ]) * pow(sigma_p, 2)

    # Observation noise matrix
    R = np.array([
        [ pow(sigma_o, 2), 0 ],
        [ 0, pow(sigma_o, 2) ]
    ])

    # Initial Covariance Matrix
    P = np.eye(F.shape[1]) * pow(sigma_o, 2)

    filter = KalmanFilter(dim_x=4, dim_z=2)
    filter.F = F
    filter.Q = Q
    filter.H = H
    filter.R = R
    filter.P = P

    return filter


class Flight():
    def __init__(self, flight, radar):
        self.flight = flight
        self.radar = radar
        self.filter = initFilter()
        self.radar_data = None
        self.smoothed_flight = None
        self.filtered_flight = None

    # Task 6
    def measure_distance(self, flight_compare):
        true_lat = self.flight.data["latitude"]
        true_lon = self.flight.data["longitude"]
        lat = flight_compare.data["latitude"]
        lon = flight_compare.data["longitude"]

        dist_max = 0
        cum_means = []
        for i, _ in enumerate(lat):
            dist = geodesic((lat[i], lon[i]), (true_lat[i], true_lon[i])).m
            dist_max = max(dist, dist_max)
            cum_means.append(dist)

            dist_mean = sum(cum_means) / len(cum_means)

        return dist_mean, dist_max


    # Task 9 - smooth the data
    def smooth_flight(self, xs, cov):
        smoothed_flight = deepcopy(self.flight)
        smooth_xs, smooth_cov, _, _ = self.filter.rts_smoother(xs, cov)

        for i in range(len(smooth_xs)):
            smoothed_flight.data.loc[i, 'x'] = smooth_xs[i][0]
            smoothed_flight.data.loc[i, 'y'] = smooth_xs[i][1]

        smoothed_flight = set_lat_lon_from_x_y(smoothed_flight)

        return smoothed_flight


    def kalman_something(self, smooth = False):
        filtered_flight = deepcopy(self.radar)
        zs = []
        # arrange radar observations in list to feed into batch filter
        for i in range(len(filtered_flight.data.x)):
            zn = np.array([
                [filtered_flight.data.x[i]],
                [filtered_flight.data.y[i]]
            ])
            zs.append(zn)
        # set initial state
        x0 = np.array([
        # [ 'x_coord', 'y_coord', 'x_velocity', 'y_velocity' ]
            [ filtered_flight.data.x[0] ],
            [ filtered_flight.data.y[0] ],
            [ 0 ],
            [ 0 ]
        ])
        self.filter.x = x0

        xs, cov, _, _ = self.filter.batch_filter(zs)

        # read back the filtered data and set latitude and longitude
        for i in range(len(xs)):
            filtered_flight.data.loc[i, 'x'] = xs[i][0]
            filtered_flight.data.loc[i, 'y'] = xs[i][1]
        self.filtered_flight = set_lat_lon_from_x_y(filtered_flight)

        # Task 9 - smooth the data
        self.smoothed_flight = self.smooth_flight(xs, cov) if smooth == True else None

        return self.filtered_flight, self.smoothed_flight

    def plot(self, second_line = None):
        second_line = second_line if second_line else self.filtered_flight
        with plt.style.context("traffic"):
            # plt.figure()
            ax = plt.axes(projection=Mercator())
            ax.add_feature(countries())
            # X.first(minutes=30)
            self.flight.plot(ax, color='blue', label='flight')
            second_line.plot(ax, color='red', label='filter', alpha=0.75)
            plt.xlabel("Latitude")
            plt.ylabel("Longitude")
            ax.set_xlabel('Latitude')
            ax.set_ylabel('Longitude')
            legend = ax.legend(loc='upper left', fontsize='small')
            # Put a nicer background color on the legend.
            legend.get_frame().set_facecolor('w')
            ax.set_title(self.flight.flight_id)
            plt.show()


def main():
     # TODO: put your code here

    # Flights to run, chosen at random
    random_flights = [
        # "ADA4_025",
        # "BOE004_046",
        # "CALIBRA_021",
        # "D-KWFW_017",
        # "FGALN_005",
        # "IGRAD_000",
        # "PSWRD35_010",
        # "VHOMS_054",
        # "VOR05_034",
        "ZEROG_048",
    ]

    # Task 8
    sigma_p_list = [
        0.5, 1.0, 1.5, 2.0, 2.5,
        1.5, 1.5, 1.5, 1.5, 1.5,
        0.5, 1.0, 1.5, 2.0, 2.5,
        0.5, 1.0, 1.5, 2.0, 2.5
    ]
    sigma_o_list = [
        100, 100, 100, 100, 100,
        10, 50, 100, 150, 200,
        10, 50, 100, 150, 200,
        200, 150, 100, 50, 10
    ]
    sigma_lists = zip(sigma_p_list, sigma_o_list)

    def q(var_sigmap):
        return np.array([
            [ 0.25 * pow(dt, 4), 0, 0.5 * pow(dt, 3), 0 ],
            [ 0, 0.25 * pow(dt, 4), 0, 0.5 * pow(dt, 3) ],
            [ 0.5 * pow(dt, 3), 0, pow(dt, 2), 0 ],
            [ 0, 0.5 * pow(dt, 3), 0, pow(dt, 2) ]
        ]) * pow(var_sigmap, 2)

    def r(var_sigmao):
        return np.array([
            [ pow(var_sigmao, 2), 0 ],
            [ 0, pow(var_sigmao, 2) ]
        ])

    ground_truth = get_ground_truth_data()

    # Run EVERYTHING
    for random_flight in random_flights:
        flight_data = ground_truth[random_flight].resample("10s")
        radar_data = get_radar_data_for_flight(flight_data)
        flight = Flight(flight_data, radar_data)
        filtered_radar, smoothed_radar = flight.kalman_something(smooth=True)

        # Task 6
        dist_mean, dist_max = flight.measure_distance(filtered_radar)
        print(
            f'>>> measure distance in meters ({flight_data.flight_id}):',
            '\n>>> mean:', dist_mean,
            '\n>>> max:', dist_max
        )

        # Task 9
        dist_mean, dist_max = flight.measure_distance(smoothed_radar)
        print(
            '>>> measure distance in meters (smoothed error):',
            '\n>>> mean:', dist_mean,
            '\n>>> max:', dist_max
        )

        # Task 8
        for var_sigmap, var_sigmao in sigma_lists:
            flight.filter.Q = q(var_sigmap)
            flight.filter.R = r(var_sigmao)

            var_filtered_radar, _ = flight.kalman_something(smooth=False)
            var_dist_mean, var_dist_max = flight.measure_distance(var_filtered_radar)

            print(
                '>>> Sigma_p:', var_sigmap,
                'Sigma_o:', var_sigmao,
                'mean:', var_dist_mean,
                'max:', var_dist_max
            )

        flight.plot()

        # flight.plot(smoothed_radar)


#############################

if __name__ == "__main__":
    main()
