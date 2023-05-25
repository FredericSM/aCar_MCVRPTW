Heuristic for the MCVRPTW

This project contains an heuristic for solving the Multi-Compartiment Vehicle Routing Problem with Time Window but also the test for evaluating it and its application to study case.

Dataset --> folder with csv file containing benchmarking data, study case data and resulting test data

heuristic_test --> all python files used to do run the heuristic evaluation tests

heuristic --> contains the heuristic used for the benchmarking dataset, the heuristic used for the study case and the bayesian optimisation

study_case --> contains the files used for Côte d'Ivoire and Ethiopya

others --> all other files like for exemple the files used for scrapping


Heuristics: there is 3 files in the folder heuristics:
-MCVRPTW is the basic heuristic used to test the performance of the algorithm. As soon as a vehicle is back to the depot, it can not go back to do delivery
-MCVRPTW_for_studycase is a modified version of MCVRPTW adapted for our study case. We added two more constraintes. the delivery time can't be longer than 8 hours (unless it is longer than a few minutes) and the maximal number of stop is 4 (it means that there is maximal 4 customers per routes). Moreover when a vehicle is back to the depot and has still time to visit other customers, it can do it (we assumed that the vehicle had to take a 30 min break before leaving)
-Bayesian_optimisation is an extra algorithm to improve the quality of the route. It can be used but it make the runtime much longer

For the heuristic, if you do not want to understand the code, you can just run the function all_run


