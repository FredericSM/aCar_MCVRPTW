import pandas as pd
from typing import List,Dict
import numpy as np
import matplotlib.pyplot as plt


def plot_statistics()- >None:
    """show the mean objective value (with the standart deviation) according to the number of iterations"""
    color = ['b' ,'g' ,'r' ,'c' ,'m' ,'y']
    color_for_standart_deviation = []
    _, ax = plt.subplots()
    for index_value in range(len(self.Different_values)):
        print(self.Different_values[index_value])
        ax.plot(self.Iterations, self.Average[index_value], color = color[index_value])
        ax.plot(self.Iterations, self.Average_minus_Standart_deviation[index_value], color[index_value], alpha = 0.4)
        ax.plot(self.Iterations, self.Average_plus_Standart_deviation[index_value], color[index_value], alpha = 0.4)
        ax.fill_between(self.Iterations, self.Average_plus_Standart_deviation[index_value], self.Average_minus_Standart_deviation[index_value], facecolor= color[index_value], alpha = 0.2)

    ax.set_title(self.tuning_hyperparameter)
    ax.set_ylabel("Objective value")
    ax.set_xlabel("Iteration (#)")
    ax.legend(self.Different_values, loc="upper right")
    # plt.draw_if_interactive()
    plt.xlim(1, self.number_of_iterations)
    plt.show()