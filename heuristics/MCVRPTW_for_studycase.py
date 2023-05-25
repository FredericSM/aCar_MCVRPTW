import numpy as np
import random as rnd
import math as mt
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, TypeVar

Customer = TypeVar('Customer')
Index = TypeVar('Index')
#useful for describing the inputs


class MCVRPTW():
    """
     -----
    Input :
    # exemple : for 10 customers and  5 different products
    Coordinate : dict --> {0: (-4, -6), 1: (-3, -10), 2: (0, -6), 3: (-6, 5), 4: (1, -2), 5: (-9, 8), 6: (10, -9), 7: (5, 7), 8: (-9, 9), 9: (6, -3), 10: (-7, -5)}
    Customer_demands : dict --> {0: [0,0,0,0,0], 1: [6, 8, 3, 2, 4], 2: [4, 8, 5, 7, 2], 3: [7, 1, 4, 9, 3], 4: [8, 3, 2, 9, 1], 5: [7, 2, 1, 5, 8], 6: [1, 7, 5, 8, 9], 7: [7, 9, 1, 6, 3], 8: [1, 3, 9, 6, 5], 9: [9, 4, 2, 1, 7], 10: [2, 5, 9, 7, 8]}
    Vehicle_parameter : dict --> {'lenght_capacity' : 100, 'speed' : 100, 'product_capacity' : {0:50,1:50,2:50,3:50,4:50}}
    Distance_between_customers : List --> Distance_between_customer[i][j] gives the distance between customer i and j
                                            [[0.0, 5.0990195135927845, 11.40175425099138, 5.830951894845301, 8.54400374531753, 13.038404810405298, 10.295630140987, 27.294688127912362, 24.515301344262525, 5.0990195135927845, 37.21558813185679], [5.0990195135927845, 0.0, 12.165525060596439, 10.198039027185569, 9.219544457292887, 14.560219778561036, 15.231546211727817, 28.0178514522438, 26.92582403567252, 10.0, 39.05124837953327], [11.40175425099138, 12.165525060596439, 0.0, 16.1245154965971, 3.0, 2.8284271247461903, 13.416407864998739, 16.0312195418814, 15.264337522473747, 14.422205101855956, 26.92582403567252], [5.830951894845301, 10.198039027185569, 16.1245154965971, 0.0, 13.601470508735444, 17.08800749063506, 8.94427190999916, 31.32091952673165, 27.0, 2.0, 40.01249804748511], [8.54400374531753, 9.219544457292887, 3.0, 13.601470508735444, 0.0, 5.385164807134504, 12.36931687685298, 19.026297590440446, 17.88854381999832, 12.041594578792296, 29.832867780352597], [13.038404810405298, 14.560219778561036, 2.8284271247461903, 17.08800749063506, 5.385164807134504, 0.0, 12.806248474865697, 14.317821063276353, 12.529964086141668, 15.231546211727817, 24.515301344262525], [10.295630140987, 15.231546211727817, 13.416407864998739, 8.94427190999916, 12.36931687685298, 12.806248474865697, 0.0, 25.553864678361276, 19.4164878389476, 7.211102550927978, 32.38826948140329], [27.294688127912362, 28.0178514522438, 16.0312195418814, 31.32091952673165, 19.026297590440446, 14.317821063276353, 25.553864678361276, 0.0, 9.486832980505138, 29.410882339705484, 12.806248474865697], [24.515301344262525, 26.92582403567252, 15.264337522473747, 27.0, 17.88854381999832, 12.529964086141668, 19.4164878389476, 9.486832980505138, 0.0, 25.0, 13.038404810405298], [5.0990195135927845, 10.0, 14.422205101855956, 2.0, 12.041594578792296, 15.231546211727817, 7.211102550927978, 29.410882339705484, 25.0, 0.0, 38.01315561749642], [37.21558813185679, 39.05124837953327, 26.92582403567252, 40.01249804748511, 29.832867780352597, 24.515301344262525, 32.38826948140329, 12.806248474865697, 13.038404810405298, 38.01315561749642, 0.0]]
    Earliest_service_time : dict --> Earliest_serice_time[i] gives the lower bound of the arrival time for the delivery for customer i
                                    [0, 779, 499, 749, 131, 439, 16, 409, 73, 498, 532, 0]
                                    the first value indicates when the vehicle can leave at first the depot to deliver the first client
                                    the last value of Earliest_serice_time is necessery. 0 is a good choice. We could get ride of it but it is usefull to avoid to make case disjunctions according to the fact we are at the end of the route or not
    Latest_service_time : dict --> Latest_serice_time[i] gives the upper bound of the arrival time for the delivery for customer i
                                    [1000, 923, 549, 841, 254, 588, 86, 533, 161, 621, 671, 1000]
                                    the first value is not veru important but I set it up as the maximal value of the set in order to avoid any problems
                                    the last value of Latest_service_time is useless but it allows to have the same lenght than Earliest_serice_time
    Service_time : List --> [s1,s2,...,sp] give for each products the time needed for delivering for one unit of product
                            [10,1,15,35,5]
    -----
    Remarks :
    Arrival_time : list --> Arrival_time[i] refers to the arrival time of vehicle i
    Feasible_insertion_places : list --> (Ir) set of all feasible insertion places of customer u into route r
    -----
    Hyperparameters :
    hyperparameter_impact1
    hyperparameter_impact2
    hyperparameter_impact3
    hyperparameter_impact4
    --> hyperparameter_impact1 + hyperparameter_impact2 + hyperparameter_impact3 + hyperparameter_impact4 = 1
    hyperparameter_metric1
    hyperparameter_metric2
    hyperparameter_metric3
    --> hyperparameter_metric1 + hyperparameter_metric2 + hyperparameter_metric3 = 1
    -----
    Impact functions :
    Impact1_time_window_coverage (ISu)
    Impact2_total_waiting_time (IWu)
    Impact3_non_routed_customers (IUu)
    Impact4_metrics_summation (LDu)
    Impact4_already_assigned_customers (IRu)

    Metrics functions :
    metric1_distance_increase (c1u : Clark & Wrighte)
    metric2_time_delay (c2u : time delay for customer j after inserting a new customer u between customer i and j)
    metric3_time_gap (c3u : define a time gap between the latest service time lu of the customer u and the time of the vehicle arrival at customer u)
    ---------------------
    ---------------------
    Output:
    self.number_of_vehicle
    self.Routes --> give each route one by one (0 is the depot, so the begining and the end of each route is 0)
    self.Routes_arrival_time --> Arrival time of the vehicle at each cluster of the route
    self.Capacity_per_vehicle --> Products Capacity needed by each vehicle
    self.TDistance --> Traveled Distance by each vehicle
    self.traveled_distance --> total traveled distance
    -----
    if you just need to run the algorithm without understanding it, just run the function all_run
    -----
    """

    def __init__(self,Coordinates,Distance,Travel_time,Customer_demands, Vehicle_parameters, Earliest_service_time, Latest_service_time,
                 Service_time, Index_to_id, hyperparameter_impact1 = 0.1, hyperparameter_impact2 = 0.2, hyperparameter_impact3 = 0.1, hyperparameter_impact4 = 0.6):

        # Input :
        self.number_of_customer = len(Customer_demands) - 1
        self.Coordinates = Coordinates
        self.Distance_between_customers = Distance
        self.Travel_time = Travel_time
        self.number_of_products = len(Customer_demands[1])
        self.customer_demands = Customer_demands
        self.Vehicle_parameters = Vehicle_parameters
        self.Earliest_service_time = Earliest_service_time
        self.Latest_service_time = Latest_service_time
        self.Service_time = Service_time
        # self.Service_time = {i:sum(Service_time[p]*self.customer_demands[i][p] for p in range(len(self.number_of_products))) for i in range(len(self.number_of_customer)+1}
        # dict --> Service_time[i] gives the needed time for delivering the services and goods at location of customer i (it has to be approximated) {0:0, 1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10, 10: 10}

        # Eu <= Au & Au + Su <= Lu

        # additional Set
        self.J_non_routed_customers_set = [i for i in range(1, self.number_of_customer + 1) if
                                           sum(self.customer_demands[i]) > 0]
        # we do not add a customer to the non routed_customers_set if it does not need to be delivered
        self.Routes = [] #[[#route1],[#route2],...]
        self.Routes_arrival_time = []
        self.number_of_vehicle = 0
        ### ___ output
        self.Capacity_related_to_Routes = []  # [[[products],distance]#route1,...]
        ### ___ output : give the required capacity and distance traveled for each vehicle to deliver each customer of the route
        self.Feasible_insertion_places = []
        self.number_of_max_stop = 4

        # additional Variable :
        self.Arrival_time = [self.Earliest_service_time[0]] + [self.Latest_service_time[-1] for i in range(self.number_of_customer)] + [max(self.Latest_service_time)]
        self.Arrival_time_with_same_order_than_Routes = []
        self.number_of_customer_with_needs = len(self.J_non_routed_customers_set)
        self.Distance_done = [0,[]]
        self.traveled_distance= 0
        self.Index_to_id = Index_to_id
        ### ___ output : give the distance traveled [global distance done,[distance traveled by vehicle 1,distance traveled by vehicle 2,...]
        self.Problems = []
        self.TDistance = []
        self.Capacity_per_vehicle = []
        # geometry
        # self.average_distance_between_two_customers = sum(self.Distance_between_customers)/2/self.number_of_customer**2
        # self.estimation_number_vehicles_regarding_demand = sum(self.customer_demands)/(0.9*self.Vehicle_parameters['product_capacity'])
        # self.estimation_number_vehicles_regarding_distance = int(self.Vehicle_parameters['lenght_capacity']/self.average_distance_between_two_customers)
        self.Barycenter = self.barycenter()
        self.Customers_polar_coordinates_set = []
        self.angle_rotation_for_new_route = 0
        self.hyperparameter_angle_window = np.pi / 6
        self.current_angle_for_route = 0

        # Parameter :
        self.hyperparameter_metric1 = 1 / 3
        self.hyperparameter_metric2 = 1 / 3
        self.hyperparameter_metric3 = 1 / 3
        self.hyperparameter_impact1 = hyperparameter_impact1
        self.hyperparameter_impact3 = hyperparameter_impact3
        self.hyperparameter_impact2 = hyperparameter_impact2  # [0.2 - 0.4]
        self.hyperparameter_impact4 = hyperparameter_impact4  # [0.3 - 0.6]

    # % Plot
    def display_customers(self)->None:
        """if needed, this function can be useful for showing only the customers"""
        annotation_treshold = 1 / 60 * (max([self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]) - min(
            [self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]))
        plt.scatter([self.Coordinates[i][0] for i in range(1, self.number_of_customer + 1)],
                    [self.Coordinates[i][1] for i in range(1, self.number_of_customer + 1)], c='b')
        # for i in range(1, self.number_of_customer + 1):
        #     plt.annotate(self.customer_demands[i],
        #                  (self.Coordinates[i][0] + annotation_treshold, self.Coordinates[i][1]))
        plt.plot(self.Coordinates[0][0], self.Coordinates[0][1], c='r', marker='s')
        plt.annotate('Depot', (self.Coordinates[0][0] + annotation_treshold, self.Coordinates[0][1]))
        # plt.axis('equal')
        plt.show()

    def display_some_clients(self, Set : list)->None:
        """show only the customers you want to see """
        plt.plot(self.loc_x[0], self.loc_y[0], c='r', marker='s')
        for i in Set:
            plt.scatter(self.loc_x[i], self.loc_y[i], c='g')
            plt.annotate('$q_{%d}=%d$' % (i, self.q[str(i)]), (self.loc_x[i] + 2, self.loc_y[i]))
        plt.axis('equal')

    def display_solution(self)->None:
        "diplay the solution"
        plt.figure(dpi=100)
        annotation_treshold = 1 / 60 * (max([self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]) - min(
            [self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]))
        N = [i for i in range(1, self.number_of_customer + 1)]
        plt.scatter([self.Coordinates[i][0] for i in range(1, self.number_of_customer + 1)],
                    [self.Coordinates[i][1] for i in range(1, self.number_of_customer + 1)], c='b')
        active_arcs = []
        color_ind = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color = []
        for i in range(20):
            color += color_ind[:(int(len(self.Routes) / 5) + 1)]
        color_index = 0
        for route in self.Routes:
            active_arcs.append([color[color_index]])
            for index_route in range(0, len(route) - 1):
                active_arcs[color_index].append((route[index_route], route[index_route + 1]))
            color_index += 1
        Id_to_index = {v: k for k, v in self.Index_to_id.items()}
        for i in N:
            if sum(self.customer_demands[i])!=0:
                plt.annotate(Id_to_index[i],
                         (self.Coordinates[i][0] + annotation_treshold, self.Coordinates[i][1]))
        for arc in active_arcs:
            for i, j in arc[1:]:
                plt.plot([self.Coordinates[i % (self.number_of_customer + 1)][0],
                          self.Coordinates[j % (self.number_of_customer + 1)][0]],
                         [self.Coordinates[i % (self.number_of_customer + 1)][1],
                          self.Coordinates[j % (self.number_of_customer + 1)][1]], c=arc[0], alpha=0.3)
        plt.plot(self.Coordinates[0][0], self.Coordinates[0][1], c='r', marker='s')
        plt.xlabel("xcoord (lat)")
        plt.ylabel("ycoor (long)")
        plt.annotate('Depot', (self.Coordinates[0][0] + annotation_treshold, self.Coordinates[0][1]))
        plt.axis('equal')
        plt.show()

    def display_current_solution(self,route)->None:
        "diplay the current solution to help understanding the construction"
        plt.close('all')
        Route = self.Routes + [route]
        plt.figure(dpi=100)
        annotation_treshold = 1 / 60 * (max([self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]) - min(
            [self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]))
        N = [i for i in range(1, self.number_of_customer + 1)]
        plt.scatter([self.Coordinates[i][0] for i in range(1, self.number_of_customer + 1)],
                    [self.Coordinates[i][1] for i in range(1, self.number_of_customer + 1)], c='b')
        active_arcs = []
        color_ind = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color = []
        for i in range(5):
            color+= color_ind[:(int(len(self.Routes)/5)+1)]
        color_index = 0
        for route in Route:
            active_arcs.append([color[color_index]])
            for index_route in range(0, len(route) - 1):
                active_arcs[color_index].append((route[index_route], route[index_route + 1]))
            color_index += 1
        for i in N:
            plt.annotate(self.customer_demands[i],
                         (self.Coordinates[i][0] + annotation_treshold, self.Coordinates[i][1]))
        for arc in active_arcs:
            for i, j in arc[1:]:
                plt.plot([self.Coordinates[i % (self.number_of_customer + 1)][0],
                          self.Coordinates[j % (self.number_of_customer + 1)][0]],
                         [self.Coordinates[i % (self.number_of_customer + 1)][1],
                          self.Coordinates[j % (self.number_of_customer + 1)][1]], c=arc[0], alpha=0.3)
        plt.plot(self.Coordinates[0][0], self.Coordinates[0][1], c='r', marker='s')
        plt.annotate('Depot', (self.Coordinates[0][0] + annotation_treshold, self.Coordinates[0][1]))
        plt.axis('equal')
        plt.show()

    def display_one_route(self,route)->None:
        "diplay one chosen route to help understanding the construction"
        plt.figure(dpi=100)
        annotation_treshold = 1 / 60 * (max([self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]) - min(
            [self.Coordinates[i][1] for i in range(self.number_of_customer + 1)]))
        N = [i for i in range(1, self.number_of_customer + 1)]
        plt.scatter([self.Coordinates[i][0] for i in range(1, self.number_of_customer + 1)],
                    [self.Coordinates[i][1] for i in range(1, self.number_of_customer + 1)], c='b')
        active_arcs = []
        color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'b', 'g', 'r', 'c', 'm', 'y',
                 'k', 'b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_index = 0

        active_arcs.append([color[color_index]])
        for index_route in range(0, len(route) - 1):
            active_arcs[color_index].append((route[index_route], route[index_route + 1]))
        color_index += 1
        for i in N:
            plt.annotate(self.customer_demands[i],
                         (self.Coordinates[i][0] + annotation_treshold, self.Coordinates[i][1]))
        for arc in active_arcs:
            for i, j in arc[1:]:
                plt.plot([self.Coordinates[i % (self.number_of_customer + 1)][0],
                          self.Coordinates[j % (self.number_of_customer + 1)][0]],
                         [self.Coordinates[i % (self.number_of_customer + 1)][1],
                          self.Coordinates[j % (self.number_of_customer + 1)][1]], c=arc[0], alpha=0.3)
        plt.plot(self.Coordinates[0][0], self.Coordinates[0][1], c='r', marker='s')
        plt.annotate('Depot', (self.Coordinates[0][0] + annotation_treshold, self.Coordinates[0][1]))
        plt.axis('equal')
        plt.show()

    # % geometry
    def change_to_polar_coordinate_with_given_center(self, center: tuple, point: tuple) -> tuple:
        """
        Inputs :
        center : tuple of coordinates of the point which will be the center for the polar coordinates of the other point
        point : tuple of coordinates of the point which we want to know the polar coordinates according to the center
        -----
        return the radius and the angle
        """
        x_relativ = point[0] - center[0]
        y_relativ = point[1] - center[1]
        radius = np.hypot(x_relativ, y_relativ)
        theta = self.theta(x_relativ, y_relativ)
        return (radius, theta)

    def furthest_from_the_depot(self) -> None:
        """
        compute the customers_polar_coordinates_set for all customer with the depot as center
        self.Customers_polar_coordinates_set give the following table : [[polar coordinates,index of customer],...]
        """
        self.Customers_polar_coordinates_set = []
        Customers_polar_coordinates_set = []
        for u in range(1, self.number_of_customer + 1):
            if u in self.J_non_routed_customers_set:
                Customers_polar_coordinates_set.append(
                    [self.change_to_polar_coordinate_with_given_center(self.Coordinates[0], self.Coordinates[u]), u])
        self.Customers_polar_coordinates_set = Customers_polar_coordinates_set
        # [[polar coordinates,index of customer],...]

    def theta(self, x:float, y:float)->float:
        """compute the angle component of the polar coordinates
        (x,y) is the cartesian coordinate
        """
        if x == 0 and y != 0:
            return y / abs(y) * np.pi / 2
        elif x != 0 and y != 0:
            if x > 0:
                return np.arctan(y / x)
            else:
                return np.arctan(-y / x) + y / abs(y) * np.pi / 2
        elif y == 0:
            if x >= 0:
                return 0
            else:
                return np.pi

    def barycenter(self) -> tuple:
        """return the barycenter of all customers weighted by their demands"""
        mean_x = 0
        mean_y = 0
        sum_customers_demands = 0
        for i in range(1, len(self.customer_demands)):
            sum_customers_demands += sum(self.customer_demands[i])
        for i in range(1, self.number_of_customer + 1):
            mean_x += sum(self.customer_demands[i]) * self.Coordinates[i][0]
            mean_y += sum(self.customer_demands[i]) * self.Coordinates[i][1]
        return (mean_x / sum_customers_demands, mean_y / sum_customers_demands)

    def depot_as_barycenter(self)->None:
        """change the coordinate of the depot to those of the barycenter"""
        self.Coordinates[0] = self.Barycenter

    def Distance(self) -> List[List[float]]:
        """return the distance between two customers (includes the depot) : D[i][j] is the distance between customers i and j"""
        Distance = []
        for i in range(self.number_of_customer + 1):
            distance = []
            for j in range(self.number_of_customer + 1):
                distance.append(np.hypot(self.Coordinates[i][0] - self.Coordinates[j][0],
                                         self.Coordinates[i][1] - self.Coordinates[j][1]))
            Distance.append(distance)
        return Distance

    def next_seed_customer(self)->list:
        """
        compute the next customer which has to be picked according to the current "seed" customer
        the next customer to be chosed is the one which has the biggest radius and which angle is not closer
        than self.hyperparameter_angle_window to the current "seed" customer
        return the furthest one with the following format : [polar coordinates,index of customer]
        """
        Next_customers = []
        for customer in self.Customers_polar_coordinates_set:
            #for all customers, we check if it is too close to the "seed" customer
            if self.current_angle_for_route + self.hyperparameter_angle_window > np.pi:
                if customer[0][1] >= (self.current_angle_for_route + self.hyperparameter_angle_window - 2 * np.pi) or \
                        customer[0][1] <= (self.current_angle_for_route - self.hyperparameter_angle_window):
                    Next_customers.append(customer)
            elif self.current_angle_for_route - self.hyperparameter_angle_window <= -np.pi:
                if customer[0][1] >= (self.current_angle_for_route + self.hyperparameter_angle_window) or customer[0][
                    1] <= (self.current_angle_for_route - self.hyperparameter_angle_window + 2 * np.pi):
                    Next_customers.append(customer)
            else:
                if customer[0][1] >= (self.current_angle_for_route + self.hyperparameter_angle_window) or customer[0][
                    1] <= (self.current_angle_for_route - self.hyperparameter_angle_window):
                    Next_customers.append(customer)
        if Next_customers == []:
            #then the angle constraints does not make sens anymore
            if self.Customers_polar_coordinates_set==[]:
                return [0,0]
            else:
                return max(self.Customers_polar_coordinates_set)
        return max(Next_customers)
        #[polar coordinates,index of customer]

    def get_arrival_time_from_previous_customer(self,previous_customer : Customer, current_customer : Customer)->float:
        """
        simplify the text in making it shorter. It computes the arrival time of a selected customer according to the last one
        :param previous_customer: the index of the customer which is the last one before the current customer
        :param current_customer: the index of the customer we need the arrival time
        :return: Acurrent_customer
        """
        return max(self.Earliest_service_time[current_customer],
                                 self.Arrival_time[previous_customer] + self.Service_time[previous_customer] +
                                 self.Travel_time[previous_customer][current_customer % (self.number_of_customer + 1)]
                / self.Vehicle_parameters['speed'])

    def update_Feasible_insertion_places(self, u: Customer, route: list,route_arrival_time) -> None:
        """
        update self.Feasible_insertion_places for a specific route with the feasible insertion location index of u in the route.
        index = i => customer u is insert after customer route[i]
        -----
        condition for feasible insertion :
        -Ai + Si + Dui/v + Su < Lu
        -capacity condition
        -distance condition
        -max(Eu,Ai + Si + Diu/v) + Du(i+1)/v + Su < A(i+1)
        -Anc + Su + (Dui + Du(i+1) - Di(i+1))/v < Lnc
        -----
        Eu <= Au & Au + Su <= Lu
        """
        self.Feasible_insertion_places = []
        self.arrival_time_has_to_be_update = []
        for index in range(len(route) - 1):
            Arrival_time_u = self.get_arrival_time_from_previous_customer(previous_customer=route[index],current_customer=u)
            # Au = max(Eu,Ai + Si + Diu/v)
            if Arrival_time_u <= self.Latest_service_time[u]:
            # Au <= Lu => there is time for delivering customer u after customer i (here we work with index so customer i is route[index])
                if self.check_products_constraints(u, route):
                # the capacity has to be check next
                    if self.Capacity_related_to_Routes[-1][1] + self.Distance_between_customers[route[index]][u] + \
                            self.Distance_between_customers[route[index + 1] % (self.number_of_customer + 1)][u] - \
                            self.Distance_between_customers[route[index]][
                                route[index + 1] % (self.number_of_customer + 1)] <= self.Vehicle_parameters[
                        'lenght_capacity']:
                    # the distance constraint has to be check also
                    # total distance traveled by the vehicle + Diu + Du(i+1) - Di(i+1) <= max capacity
                        # test if it will disturb the next customer already assigned to the route
                        i1 = route[index]
                        i2 = route[index + 1]
                        ti1 = self.Arrival_time[i1]
                        tu = max(self.Earliest_service_time[u],ti1 + self.Service_time[i1] +
                                  self.Travel_time[u][i1]
                                  / self.Vehicle_parameters['speed'])
                        ti2_u = max(self.Earliest_service_time[i2],tu + self.Service_time[u] +
                                  self.Travel_time[u][
                                      i2 % (self.number_of_customer + 1)]
                                  / self.Vehicle_parameters['speed'])
                        ti2 = max(self.Earliest_service_time[i2],ti1 + self.Service_time[i1] +
                                  self.Travel_time[i1][
                                      i2 % (self.number_of_customer + 1)]
                                  / self.Vehicle_parameters['speed'])
                        delta = ti2_u - ti1 - ti2 + ti1
                        # delta = i->u + u->i+1 - i->i+1
                        # max between E and A is very important !!!!
                        # ti2 = max(Ei+1,ti1 + Si + Dii+1/v)
                        # tu = max(Eu, ti1 + Si + Diu/v)
                        # ti2_u = max(Eu, ti1 + Si + Diu/v)
                        sumation = 0
                        for next_customer in range(index + 1, len(route) - 1):
                            # we have to check next if all following customers, route[-1] is the depot again
                            if delta <= self.Latest_service_time[route[next_customer]] - self.Arrival_time[
                                route[next_customer]]:
                                # delta < Lnc - Anc  (nc= next customer)
                                # we have to check if for all next customer, the additional time is smaller than Lnc - Anc
                                sumation += 1
                        if sumation == len(route) - index - 2 and delta <= (self.Latest_service_time[-1] - route_arrival_time[-1]):
                            # the condition has to be checked for all next customer, ie len(route) - 2 - (index + 1 - 1)
                            # at the end of the route, len(route) - index - 2 = 0, so all customers can be accepted
                            self.Feasible_insertion_places.append(index)




    # % Metric functions
    def metric1_distance_increase(self, u: Customer, i: Customer, j: Customer) -> float:
        """return the distance increase by adding customer u between customer i and customer j"""
        return self.Distance_between_customers[i][u] + self.Distance_between_customers[u][j] - \
            self.Distance_between_customers[i][j]

    def metric2_time_delay(self, u: Customer, i: Customer, j: Customer) -> float:
        """return the time increase regarding customer j by adding customer u between customers i and j. This time delay, expresses the marginal time feasibility of customer u"""
        # return (Au + Su + Duj/v) - (Ai + Si + Dij/v)
        return self.get_arrival_time_from_previous_customer(i,u) + self.Service_time[u] + (self.Distance_between_customers[u][j] -
                                       self.Travel_time[i][j]) / self.Vehicle_parameters['speed'] - \
            self.Arrival_time[i] - self.Service_time[i]

    def metric3_time_gap(self, u: Customer, i: Customer, j: Customer) -> float:
        """Return the time margin (by adding customer u between customers i and j) between the arrival of the vehicle at customer j and its upper bound of service time (it can be negative, which means it is too late). This measure expresses the compatibility of the time window of the selected customer with respect to a particular insertion position of the current route."""
        # return Lu - (Ai + Si + Diu/v)
        return self.Latest_service_time[u] - (self.Arrival_time[i] +
            self.Service_time[i] + self.Travel_time[i][u] / self.Vehicle_parameters['speed'])

    # % Impact functions
    def Impact1_time_window_coverage(self, u: Customer, i: Customer) -> float:
        """provides a measure of the coverage of the selected customer’s time window, which results from the insertion of u into the partial constructed route. The goal is to minimize this difference in order to come as close as possible at the lower bound service time.
        customer u is inserted just after customer i"""
        return self.Arrival_time[i] + self.Service_time[i] + self.Travel_time[u][i] / \
            self.Vehicle_parameters['speed'] - self.Earliest_service_time[u]

    def Impact2_total_waiting_time(self, u: Customer, route: list) -> float:
        """represents the waiting time if the arrival time for each customer is below the lower bound of service time after having inserted customer u ."""
        sum = 0
        for i in route:
            if self.Earliest_service_time[i] - self.Arrival_time[i] > 0:
                sum += self.Earliest_service_time[i] - self.Arrival_time[i]
                # sum (Ei-Ai)+
        return sum

    def Impact3_non_routed_customers(self, u: Customer) -> float:
        """return the impact of inserting non-routed customer u on the other non-routed customer, goal : minimizing the sum of the difference between the lower bound of service time + distance of customer u to j and the upper bound of service time of customer j"""
        sum = 0
        if len(self.J_non_routed_customers_set) == 1:
            return 0
        for j in self.J_non_routed_customers_set:
            if j != u:
                sum += max(
                    self.Latest_service_time[j] - self.Earliest_service_time[u] - self.Travel_time[u][
                        j] / self.Vehicle_parameters['speed'],
                    self.Latest_service_time[u] - self.Earliest_service_time[j] - self.Travel_time[u][
                        j] / self.Vehicle_parameters['speed'])
                # sum j!= u (max(Lj - Eu -Duj/v), Lu - Ej - Duj/v))
        return sum / (len(self.J_non_routed_customers_set) - 1)

    def Impact4_metrics_summation(self, u: Customer, i: Customer, j: Customer) -> float:
        """return the summation of all metric functions with weights (local disturbances)"""
        return self.hyperparameter_metric1 * self.metric1_distance_increase(u, i,
                                                                            j) + self.hyperparameter_metric2 * self.metric2_time_delay(
            u, i, j) + self.hyperparameter_metric3 * self.metric3_time_gap(u, i, j)

    def Impact4_already_assigned_customers(self, u: int) -> float:
        """return the summation of all local disturbances divided by the number of feasible insertion places"""
        sum = 0
        for i in self.Feasible_insertion_places:
            sum += self.Impact4_metrics_summation(u, i, i + 1)
        return sum / len(self.Feasible_insertion_places)

    def Impact(self, u: int) -> float:
        """return the global impact of inserting customer u. goal : minimize the output """
        return self.hyperparameter_impact1 * self.Impact1_time_window_coverage(
            u) + self.hyperparameter_impact3 * self.Impact3_non_routed_customers(
            u) + self.hyperparameter_impact2 * self.Impact2_total_waiting_time(
            u) + self.hyperparameter_impact4 * self.Impact4_already_assigned_customers(u)

    # % other

    def get_number_of_customer_in_Routes(self) -> int:
        """return the number of customer in Routes (set of all routes)"""
        counter = 0
        for R in self.Routes:
            for r in R[1:-1]:
                counter += 1
        return counter

    def compute_done_distance(self)->None:
        """compute the distance which has been done by all vehicles and pro vehicles
        [total distance,[distance vehicle 1,distance vehicle 1,....]]
        """
        done_distance = 0
        for route in self.Routes:
            self.Distance_done[1].append(sum(
                self.Distance_between_customers[route[i]][route[(i + 1)] % (self.number_of_customer + 1)] for i in
                range(len(route) - 1)))
        self.Distance_done[0] = sum([i for i in self.Distance_done[1]])

    def update_Capacity_related_to_Routes(self, i: Index, u: Customer, route: list)->None:
        """update the capacity needed to deliver the current customers part of the current route"""
        for product in range(self.number_of_products):
            self.Capacity_related_to_Routes[-1][0][product] += self.customer_demands[u][product]
        self.Capacity_related_to_Routes[-1][1] += self.Distance_between_customers[route[i]][u] + \
                                                  self.Distance_between_customers[
                                                      route[i + 1] % (self.number_of_customer + 1)][u] - \
                                                  self.Distance_between_customers[route[i]][
                                                      route[i + 1] % (self.number_of_customer + 1)]

    def check_products_constraints(self, u: Customer, route: list) -> None:
        """check if the constraint about the products is respected"""
        for product in range(self.number_of_products):
            if self.Capacity_related_to_Routes[-1][0][product] + self.customer_demands[u][product] > \
                    self.Vehicle_parameters['product_capacity'][product]:
                return False
        return True

    def compute_route_arrival_time(self,route,time_begin):
        arrival_time_route = [time_begin]
        for i in range(1, len(route)):
            arrival_time_route.append(max(self.Earliest_service_time[route[i]], arrival_time_route[-1] + \
                                          self.Service_time[route[i-1]% (self.number_of_customer + 1)] + \
                                          self.Travel_time[route[i - 1]][
                                              route[i] % (self.number_of_customer + 1)] / self.Vehicle_parameters[
                                              'speed']))
        return arrival_time_route

    def condition_last_one_to_depot(self,seed_customer,route,arrival_time_route):
        time = max(self.Earliest_service_time[seed_customer], arrival_time_route[-1]+0.5 + \
                   self.Service_time[route[-1] % (self.number_of_customer + 1)] + \
                   self.Travel_time[seed_customer][
                       route[-1] % (self.number_of_customer + 1)] / self.Vehicle_parameters[
                       'speed'])
        time2 = time + \
                   self.Service_time[seed_customer] + \
                   self.Travel_time[seed_customer][0] / self.Vehicle_parameters[
                       'speed']
        return self.Latest_service_time[-1] < time2

    def condition_seed_customer_new_route(self,seed_customer,route,arrival_time_route):
        time = max(self.Earliest_service_time[seed_customer], arrival_time_route[-1]+0.5 + \
                                          self.Service_time[route[-1]% (self.number_of_customer + 1)] + \
                                          self.Travel_time[seed_customer][
                                              route[-1] % (self.number_of_customer + 1)] / self.Vehicle_parameters[
                                              'speed'])
        return self.Latest_service_time[seed_customer]<time


    def update_Arrival_time_with_same_order_than_Routes(self):
        """based on the customer order of the route, it show instead the arrival time. It is usefull to check if the is no time window constraint violation"""
        self.Arrival_time_with_same_order_than_Routes = []
        for i in range(len(self.Routes)):
            self.Arrival_time_with_same_order_than_Routes.append([self.Arrival_time[i] for i in self.Routes[i]])
            self.Arrival_time_with_same_order_than_Routes[-1][-1] = self.Arrival_time_with_same_order_than_Routes[-1][-2] + \
                    self.Service_time[self.Routes[i][-2]] + \
                    self.Travel_time[self.Routes[i][-2]][self.Routes[i][0]] / self.Vehicle_parameters['speed']

    def update_arrival_time(self, route_arrival_time, route: list) -> None:
        """shift the arrival time of all customer after customer u_best"""
        for index in range(len(route)):
            if route[index]!=0:
                self.Arrival_time[route[index]] = route_arrival_time[index]

    def check_all_is_allright(self) -> None:
        Capactity = []
        TDistance = []
        for r in range(len(self.Routes)):
            route = self.Routes[r]
            capacity = [0 for p in range(self.number_of_products)]
            capa = []
            for i in route[1:]:
                for product in range(self.number_of_products):
                    capacity[product] += self.customer_demands[i][product]
                if i == 0:
                    capa.append(capacity)
                    capacity = [0 for p in range(self.number_of_products)]
            Capactity.append(capa)

        """function to check if everything is right"""
        number_of_customers = 0
        for r in range(len(self.Routes)):
            route = self.Routes[r]
            capacity = [0 for i in range(self.number_of_products)]
            number_of_customers += sum([1 for i in route if i!=0])
            somme = 0
            for i in range(1,len(route)):
                somme += self.Distance_between_customers[route[i]][route[i -1] % (self.number_of_customer + 1)]
                if route[i]==0:
                    if somme >self.Vehicle_parameters['lenght_capacity']:
                        print('the lenght capacity is overwhelmed')
                        self.Problems.append('the lenght capacity is overwhelmed')
                    somme = 0
            if max([self.Routes_arrival_time[r][i] - self.Routes_arrival_time[r][i+1] for i in range(len(route) - 2)]) > 0:
                print('error timing between customers')
                self.Problems.append('error timing between customers')
            for i in range(len(route)):
                customer=route[i]
                if self.Routes_arrival_time[r][i] < self.Earliest_service_time[customer] or self.Routes_arrival_time[r][i] > \
                   self.Latest_service_time[customer]:
                    print('error timing',customer)
                    self.Problems.append(['error timing',customer,route])
                    print(self.Earliest_service_time[customer], self.Arrival_time[customer],
                          self.Latest_service_time[customer],route,self.Routes.index(route))
            for i in route[1:]:
                for product in range(self.number_of_products):
                    capacity[product] += self.customer_demands[i][product]
                if i==0:
                    for product in range(self.number_of_products):
                        if capacity[product] >self.Vehicle_parameters['product_capacity'][product]:
                            print('the capacity is overwhelmed')
                            self.Problems.append('the capacity is overwhelmed')
                    capacity = [0 for i in range(self.number_of_products)]


        if number_of_customers != self.number_of_customer_with_needs:
            print('the number of routed customers does not match with the number of customer')
            self.Problems.append('the number of routed customers does not match with the number of customer')
        for customer in [i for i in range(1, self.number_of_customer + 1) if
                                           sum(self.customer_demands[i]) > 0]:
            sumation = 0
            for route in self.Routes:
                if customer in route:
                    sumation+=1
            if sumation!=1:
                print('there is a problem with customer %f'%customer)
                self.Problems.append('there is a problem with customer %f'%customer)

    def change_last_by_0(self)->None:
        """to make it easier to understand, the last index of each route is replaced by 0"""
        for r in range(len(self.Routes)):
            self.Routes[r][-1]=self.Routes[r][-1]%(self.number_of_customer+1)

    def heuristic(self):
        """
        Methodology :
        Step 0 : Initialization
        Step 1 : Select a ‘seed’ customer to start a router.
        Step 2 : Find the feasible non-routed customer u that minimizes the composite criterion Impact(u):
            Step2 a : Examine all possible feasible insertions i of customer u into the current route under construction
            Step 2b : Calculate local disturbances LDu (extra distance, marginal time feasibility and time window compatibility)
            Step 2c : Calculate global disturbance IRu of customer u
            Step 2d : Calculate the coverage customer u time window ISu
            Step 2e : Calculate the real coverage of time windows of the non-routed customers result- ing from the insertion of u into the current route IUu
            Step 2f : Calculate the total waiting time of route IWu
            Step 2g : Calculate Impact(u)
            Step 2h : Select insertion location i that results in minimum LDu for customer u
            Step 2i : Select customer u with minimum Impact(u)
        Step 3 : Insert the selected customer u to the insertion location with minimum local disturbance LDu of the current route r. Update the route and set u as a routed customer and remove u from set J
        Step 4 : If there are non-routed customers that are feasible for insertion in to the current router,return to Step1; otherwise proceed to Step5
        Step 5 : If all customers have been scheduled, go to Step6. Otherwise, go to Step 1 - initiate new route
        Step 6 : Terminate Output number of routes (active vehicles), sequence of customers visited by each vehicle, total distance (time) travelled and total cost.
        """
        # step0 : creating of a 'seed' customer set in which all customer are far from the depot because they are the most difficult to insert in a route
        self.furthest_from_the_depot()
        # compute self.customers_polar_coordinates_set
        return_to_step1_with_new_route = 2
        index_for_seed_customer_choice = 0
        seed_customer = [[0,0],0]
        seed_customer_history = seed_customer
        while self.J_non_routed_customers_set != []:  # while not all customers are served :
            if return_to_step1_with_new_route == 0:
                if len(route)==self.number_of_max_stop+2:
                    return_to_step1_with_new_route = 1
            ### step 1 : Select a‘seed’customer to start a router
            if return_to_step1_with_new_route == 1:

                self.current_angle_for_route += seed_customer[0][1]
                # as there is a new route (or not for the begining but it doesn't matter where we start), the currant_angle_for_new_route has to be set as the previous "seed" customer angle
                if self.current_angle_for_route > np.pi:
                    self.current_angle_for_route -= 2 * np.pi
                # we have to check if the current angle is in (-pi,pi]
                self.furthest_from_the_depot()
                # compute self.customers_polar_coordinates_set
                seed_customer = self.next_seed_customer()
                # the seed_customer will create the new route because it is one of the furthest one from the depot and it is always difficult at the end to integer them in the route
                # we choose the customer which has the largest radius and an angle between self.current_angle_for_route and self.current_angle_for_route+self.angle_rotation_for_new_route

                seed_customer_history = seed_customer
                while (seed_customer[1] not in self.J_non_routed_customers_set or self.condition_seed_customer_new_route(seed_customer[1],route,route_arrival_time) or self.condition_last_one_to_depot(seed_customer[1],route,route_arrival_time)) and self.Customers_polar_coordinates_set!=[]:
                    # we have to check if the customer picked in the 'seed' customer set is not already assigned to a route
                    self.Customers_polar_coordinates_set = [element for element in self.Customers_polar_coordinates_set
                                                            if element[1] != seed_customer[1]]
                    # we remove the current seed_customer as it is not J_non_routed_customer_set
                    seed_customer = self.next_seed_customer()
                if self.Customers_polar_coordinates_set!=[]:
                    seed_customer_history = seed_customer
                    if route_begin == []:
                        route_begin = route
                        route_arrival_time_begin = self.compute_route_arrival_time(route, route_arrival_time[0])
                    else:
                        route_begin += route[1:]
                        route_arrival_time_begin += self.compute_route_arrival_time(route, route_arrival_time[0])[1:]
                    route_begin[-1]=0
                    route = [0, seed_customer[1], self.number_of_customer + 1]
                    route_arrival_time = self.compute_route_arrival_time(route,route_arrival_time_begin[-1]+0.5)
                    self.update_arrival_time(route_arrival_time,route)


                    # self.number_of_customer+1 | self.number_of_customer + 1 = 0
                    self.Capacity_related_to_Routes.append(
                        [[self.customer_demands[seed_customer[1]][product] for product in range(self.number_of_products)],
                         2 * self.Distance_between_customers[0][seed_customer[1]]])
                    self.J_non_routed_customers_set.remove(seed_customer[1])
                    # the picked 'seed' customer is not anymore non-routed
                    self.Arrival_time[seed_customer[1]] = max(self.Earliest_service_time[seed_customer[1]],
                                                              self.Arrival_time[0]+self.Travel_time[0][route[1]]/self.Vehicle_parameters['speed'])
                else:
                    if route_begin == []:
                        route_begin = route
                        route_arrival_time_begin = route_arrival_time
                    else:
                        route_begin += route[1:]
                        route_arrival_time_begin += route_arrival_time[1:]
                    route_begin[-1] = 0
                    if route_arrival_time_begin == []:
                        route_arrival_time = self.compute_route_arrival_time(route, self.Earliest_service_time[0])
                    else:
                        route_arrival_time = self.compute_route_arrival_time(route, route_arrival_time_begin[-1] + 0.5)
                    self.Routes.append(route_begin)
                    self.Routes_arrival_time.append(route_arrival_time_begin)
                    if self.J_non_routed_customers_set == []:
                        return self.Routes
                    else:
                        return_to_step1_with_new_route = 2
            if return_to_step1_with_new_route == 2:
                self.current_angle_for_route += seed_customer_history[0][1]
                # as there is a new route (or not for the begining but it doesn't matter where we start), the currant_angle_for_new_route has to be set as the previous "seed" customer angle
                if self.current_angle_for_route > np.pi:
                    self.current_angle_for_route -= 2 * np.pi
                # we have to check if the current angle is in (-pi,pi]
                self.furthest_from_the_depot()
                # compute self.customers_polar_coordinates_set
                seed_customer = self.next_seed_customer()
                # the seed_customer will create the new route because it is one of the furthest one from the depot and it is always difficult at the end to integer them in the route
                # we choose the customer which has the largest radius and an angle between self.current_angle_for_route and self.current_angle_for_route+self.angle_rotation_for_new_route
                while seed_customer[1] not in self.J_non_routed_customers_set:
                    if seed_customer == [0,0]:
                        return self.Routes
                    # we have to check if the customer picked in the 'seed' customer set is not already assigned to a route
                    self.Customers_polar_coordinates_set = [element for element in self.Customers_polar_coordinates_set
                                                            if element[1] != seed_customer[1]]
                    # we remove the current seed_customer as it is not J_non_routed_customer_set
                    seed_customer = self.next_seed_customer()
                route =[0, seed_customer[1], self.number_of_customer + 1]
                route_begin = []
                route_arrival_time_begin = []
                route_arrival_time = self.compute_route_arrival_time(route,self.Earliest_service_time[0])
                self.update_arrival_time(route_arrival_time, route)

                # self.number_of_customer+1 | self.number_of_customer + 1 = 0
                self.Capacity_related_to_Routes.append(
                    [[self.customer_demands[seed_customer[1]][product] for product in range(self.number_of_products)],
                     2 * self.Distance_between_customers[0][seed_customer[1]]])
                self.J_non_routed_customers_set.remove(seed_customer[1])
                # the picked 'seed' customer is not anymore non-routed
                self.Arrival_time[seed_customer[1]] = max(self.Earliest_service_time[seed_customer[1]],
                                                          self.Arrival_time[0]+self.Travel_time[0][route[1]]/self.Vehicle_parameters['speed'])
                # for this 'seed' customer, the best is when there it starts at its lower bound of service time to let as much as possible time for other customers
                if self.Arrival_time[seed_customer[1]] > self.Latest_service_time[seed_customer[1]]:
                    print('the vehicle is too slow to deliver customer %f'% int(seed_customer[1]))
                if 2*self.Distance_between_customers[0][seed_customer[1]]>self.Vehicle_parameters['lenght_capacity']:
                    print('the distance capacity of the vehicle does not allow to reach the customer %f'% int(seed_customer[1]))
                # we have to check if it feasible to reach the "seed" customer regarding the time windows. If not, either the speed is too low or the customer is too far
            Impact_table = []
            # creation of an Impact table to save all value in order to be able to choose the minimal one
            if not (self.J_non_routed_customers_set):
                ### step 6
                if route_begin == []:
                    route_begin = route
                    route_arrival_time_begin = route_arrival_time
                else:
                    route_begin += route[1:]
                    route_arrival_time_begin+= route_arrival_time[1:]
                route_begin[-1] = 0
                self.Routes.append(route_begin)
                self.Routes_arrival_time.append(route_arrival_time_begin)
                self.update_Arrival_time_with_same_order_than_Routes()
                self.number_of_vehicle = len(self.Routes)
                return self.Routes
            ### Step2:Find the feasible non-routed customer u that minimizes the composite criterion Impact(u):
            for u in self.J_non_routed_customers_set:
                self.update_Feasible_insertion_places(u, route, route_arrival_time)
                ## Step 2a : Examine all possible feasible insertions i of customer u into the current route under construction
                if not (self.Feasible_insertion_places):
                    Impact_table.append((10 ** 5, 0, u))
                else:
                    Impact4__metrics_summation__table = []
                    # table for local disturbances
                    for insertion_place in self.Feasible_insertion_places:
                        ## Step 2b : Calculate local disturbances LDu for each position
                        Impact4__metrics_summation__table.append(
                            self.Impact4_metrics_summation(u, route[insertion_place],
                                                           route[insertion_place + 1] % (self.number_of_customer + 1)))
                        # saving of the value in this table
                    Impact4_already_assigned_customers = sum(Impact4__metrics_summation__table) / len(
                        self.Feasible_insertion_places)
                    # computation of the global disturbances
                    insertion_index = self.Feasible_insertion_places[
                        Impact4__metrics_summation__table.index(min(Impact4__metrics_summation__table))]
                    # looking for the insertion index of the minimum value related to the global disturbance
                    Impact_table.append((self.hyperparameter_impact1 * self.Impact1_time_window_coverage(u, route[
                        insertion_index]) + self.hyperparameter_impact3 * self.Impact3_non_routed_customers(
                        u) + self.hyperparameter_impact2 * self.Impact2_total_waiting_time(u,
                                                                                           route) + self.hyperparameter_impact4 * Impact4_already_assigned_customers,
                                         insertion_index, u))
                    # computation of the Impact with at the end the index of insertion and u
            if min(Impact_table)[0] != 10 ** 5:
                u_best_customer = Impact_table[Impact_table.index(min(Impact_table))][2]
                i_best_index = Impact_table[Impact_table.index(min(Impact_table))][1]  # insertion between i and i+1 element
                ### step 3 : Insert the selected customer u to the insertion location with minimum local disturbance LDu of the current route r. Update the route and set u as a routed customer and remove u from set J
                self.J_non_routed_customers_set.remove(u_best_customer)
                self.update_Capacity_related_to_Routes(i_best_index, u_best_customer, route)
                route.insert(i_best_index + 1, u_best_customer)
                route_arrival_time = self.compute_route_arrival_time(route, route_arrival_time[0])
                # self.display_current_solution(route)
                self.update_arrival_time(route_arrival_time, route)
                # step 4 : test if there are non-routed customers that are feasible for insertion into the current router
                compt = 0
                for u in self.J_non_routed_customers_set:
                    self.update_Feasible_insertion_places(u, route,route_arrival_time)
                    if self.Feasible_insertion_places != []:
                        break
                    else:
                        compt += 1
                if compt == len(self.J_non_routed_customers_set):
                    # it means that there is no feasible insertion for route "route"
                    # route is closed
                    if not (self.J_non_routed_customers_set):
                        ### step 6 beacuse there is now more non-routed customers
                        if route_begin == []:
                            route_begin = route
                            route_arrival_time_begin = route_arrival_time
                        else:
                            route_begin += route[1:]
                            route_arrival_time_begin += route_arrival_time[1:]
                        route_begin[-1] = 0
                        self.Routes.append(route_begin)
                        self.Routes_arrival_time.append(route_arrival_time_begin)
                        self.update_Arrival_time_with_same_order_than_Routes()
                        self.number_of_vehicle = len(self.Routes)
                        return self.Routes
                    else:
                        # back to step 1 with new route

                        return_to_step1_with_new_route = 1
                        # needed for picking the next 'seed' customer
                else:
                    # back to step 1 without new route
                    return_to_step1_with_new_route = 0
            else:
                # back to step 1 with new route
                return_to_step1_with_new_route = 1
                # needed for picking the next 'seed' customer
        self.update_Arrival_time_with_same_order_than_Routes()
        self.number_of_vehicle = len(self.Routes)
        # while loop is over, it means it is the end



    def all_run(self):
        self.heuristic()
        self.compute_done_distance()
        self.change_last_by_0()
        # self.check_all_is_allright()
        print('Value from the heuristic:')
        print('Number of Vehicles:',self.number_of_vehicle)
        print('Routes with heuristics id:',self.Routes)
        print('Arrival time at each cluster of the route:',self.Routes_arrival_time)
        self.Capacity_per_vehicle = []
        self.TDistance = []
        for r in range(len(self.Routes)):
            route = self.Routes[r]
            capacity = [0 for p in range(self.number_of_products)]
            capa = []
            for i in route[1:]:
                for product in range(self.number_of_products):
                    capacity[product] += self.customer_demands[i][product]
                if i == 0:
                    capa = capacity
                    capacity = [0 for p in range(self.number_of_products)]
            self.Capacity_per_vehicle.append(capa)

            distance = []
            somme = 0
            for i in range(1,len(route)):
                somme += self.Distance_between_customers[route[i]][route[i - 1]]
                if route[i] == 0:
                    distance.append(somme)
                    somme = 0
            self.TDistance.append(distance)
        self.traveled_distance = sum([sum(self.TDistance[i]) for i in range(len(self.TDistance))])
        print('Products Capacity needed by each vehicle:',self.Capacity_per_vehicle)
        print('Traveled Distance by each vehicle:',self.TDistance)
        print('Traveled Distance:', self.traveled_distance)



# n = 10
# p = 5
# Coordinates = {i: (rnd.randint(-10, 10), rnd.randint(-10, 10)) for i in range(n + 1)}
# Customer_demands = {i: [10 for product in range(p)] for i in range(1, n + 1)}
# Customer_demands[0] = [0 for product in range(p)]
# Vehicle_parameters = {'lenght_capacity': 50, 'speed': 100,
#                       'product_capacity': {product: 50 for product in range(p)}}
# Earliest_service_time = [8] + [8 for i in range(n)] + [8]
# Latest_service_time = [16] + [Earliest_service_time[i + 1] + 8 for i in range(n)] + [16]
# Service_time = {i: 1 for i in range(1, n + 1)}
# Service_time[0] = 0
# VRP = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
#                Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
#                Service_time=Service_time)
# VRP.all_run()
# VRP.display_solution()
# #


