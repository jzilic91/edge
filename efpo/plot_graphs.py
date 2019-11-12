import numpy as np
import matplotlib.pyplot as plt

def stacked_bar(data, series_labels, category_labels = None, 
                show_values = False, value_format = "{}", y_label = None, 
                grid = False, reverse = False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    category_labels -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will 
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_label         -- Label for y-axis (str)
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis=1)
        category_labels = reversed(category_labels)

    for i, row_data in enumerate(data):
        axes.append(plt.bar(ind, row_data, bottom=cum_size,
                            label=series_labels[i]))
        cum_size += row_data

    if category_labels:
        plt.xticks(ind, category_labels)

    if y_label:
        plt.ylabel(y_label)

    plt.legend()

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                if h != 0.0:
	                plt.text(bar.get_x() + w/2, bar.get_y() + h/2, 
	                         value_format.format(h), ha="center", 
	                         va="center")

def plot_offloading_distribution(data):	
	plt.rcParams.update({'font.size': 14})
	plt.figure(figsize=(6, 4))

	series_labels = ['Mobile', 'E Data', 'E Comp', 'E Regular', 'Cloud DC']

	category_labels = ['LOCAL', 'MC', 'EE', 'EFPO']

	stacked_bar(
	    data, 
	    series_labels, 
	    category_labels=category_labels, 
	    show_values=True, 
	    value_format="{:.2f}",
	    y_label="Quantity (units)"
	)

	plt.xlabel('Offloading decision engines')
	plt.ylabel('Distribution (%)')
	plt.ylim(0, 110)
	plt.show()

def plot_failure_rates(data):
	offloading_sites = ['MOBILE', 'E DATA', 'E COMP', 'E REG', 'CLOUD']

	x = np.arange(len(offloading_sites))

	plt.rcParams.update({'font.size': 14})
	ax = plt.subplot(111)
	ax.bar(x - 0.4, data[0], width = 0.2, color = 'b', align = 'center', label = 'Local')
	ax.bar(x - 0.2, data[1], width = 0.2, color = 'g', align = 'center', label = 'Mobile Cloud')
	ax.bar(x, data[2], width = 0.2, color = 'r', align = 'center', label = 'Energy Efficient')
	ax.bar(x + 0.2, data[3], width = 0.2, color = 'm', align = 'center', label = 'EFPO')

	plt.xlabel('Offloading sites')
	plt.ylabel('Offloading failure rates (%)')
	plt.xticks(x, offloading_sites, fontsize = 14)
	plt.legend()
	plt.show()

# Facerecognizer mobile application data
data = [
#  LOCAL MC   EE  EFPO
    [100, 81, 40, 40],   # MD
    [0, 0, 22, 21],    # E1
    [0, 0, 11, 17],    # E2
    [0, 0, 0, 18],       # E3
    [0, 19, 27, 4]  # CD
]

plot_offloading_distribution(data)

# Facerecognizer mobile application data
data = [
#  LOCAL MC   EE  EFPO
    [100, 68, 50, 50],   # MD
    [0, 0, 15, 13],    # E1
    [0, 0, 10, 16],    # E2
    [0, 0, 1, 16],    # E3
    [0, 32, 24, 5]  # CD
]

plot_offloading_distribution(data)

# Facerecognizer mobile application data
data = [
#  LOCAL MC   EE  EFPO
    [100, 84, 50, 50],   # MD
    [0, 0, 23, 17],    # E1
    [0, 0, 13, 16],    # E2
    [0, 0, 0, 15],       # E3
    [0, 16, 14, 2]  # CD
]

plot_offloading_distribution(data)

# Facerecognizer mobile application data
data = [
#   MD  E1 E2 E3 CD
    [0, 0, 0, 0, 0],                  # LOCAL
    [0, 0, 0, 0, 0],    		      # MC
    [0, 13, 3.8, 0.14, 1.5],  # EE
    [0, 5, 0.3, 0.01, 0],      # EFPO
]

plot_failure_rates(data)

# Facerecognizer mobile application data
data = [
#   MD  E1 E2 E3 CD
    [0, 0, 0, 0, 0],                  # LOCAL
    [0, 0, 0, 0, 1],    		      # MC
    [0, 15, 10, 0.16, 1.5],    # EE
    [0, 3, 0.3, 0, 0],           # EFPO
]

plot_failure_rates(data)

# Facerecognizer mobile application data
data = [
#   MD  E1 E2 E3 CD
    [0, 0, 0, 0, 0],                  # LOCAL
    [0, 0, 0, 0, 0],    		      # MC
    [0, 14, 4, 0.3, 1.4],    # EE
    [0, 5, 0.3, 0.01, 0],      # EFPO
]

plot_failure_rates(data)