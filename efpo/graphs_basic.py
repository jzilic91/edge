import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Rectangle

# def opt2(x):
# 	return 1 / 4 * x

# def opt1(x):
# 	return 1 / 2 * x

# def wfp(x):
# 	return x

# def mc(x):
# 	return 3 / 2 * x

# def local(x):
# 	return 2 * x

# x = list(range(0, 100))

# opt2_ = list(map(opt2, x))
# opt1_ = list(map(opt1, x))
# wfp_ = list(map(wfp, x))
# mc_ = list(map(mc, x))
# local_ = list(map(local, x))

# plt.plot(x, opt2_, 'r', label='opt2')
# plt.plot(x, opt1_, 'g', label='opt1')
# plt.plot(x, wfp_, 'b', label='wfp')
# plt.plot(x, mc_, 'm', label='mc')
# plt.plot(x, local_, 'y', label='local')

# plt.title('Energy Efficiency per Offloading Decision Policy')
# plt.xlabel('Number of application executions')
# plt.ylabel('Energy consumption')
# plt.legend()
# plt.show()

# plt.plot(x, opt2_, 'r', label='opt2')
# plt.plot(x, opt1_, 'g', label='opt1')
# plt.plot(x, wfp_, 'b', label='wfp')
# plt.plot(x, mc_, 'm', label='mc')
# plt.plot(x, local_, 'y', label='local')

# plt.title('Time completion per Offloading Decision Policy')
# plt.xlabel('Number of application executions')
# plt.ylabel('Time completion')
# plt.legend()
# plt.show()

# plt.plot(x, opt2_, 'r', label='opt2')
# plt.plot(x, opt1_, 'g', label='opt1')
# plt.plot(x, wfp_, 'b', label='wfp')
# plt.plot(x, mc_, 'm', label='mc')
# plt.plot(x, local_, 'y', label='local')

# plt.title('Rewards per Offloading Decision Policy')
# plt.xlabel('Number of application executions')
# plt.ylabel('Rewards')
# plt.legend()
# plt.show()

# N, bins, patches = plt.hist(['E1', 'E2', 'E3', 'MD', 'MD', 'E1', 'E1', 'E3', 'MD', 'E1', 'E1', 'E2', 'E3', 'MD', 'CD', 'E1', 'E2', 'E1', 'MD', 'MD', 'E1', 'E2', 'E2', 'MD', 'CD'], bins = 5)

# cmap = plt.get_cmap('jet')
# E1_c = cmap(0.25)
# E2_c =cmap(0.1)
# E3_c = cmap(0.5)
# CD_c = cmap(0.75)
# MD_c = cmap(1)
# c_map = [E1_c, E2_c, E3_c, CD_c, MD_c]

# for i in range(len(c_map)):
#     patches[i].set_facecolor(c_map[i])

# handles = [Rectangle((0,0), 1, 1, color=c, ec="k") for c in c_map]
# labels = ["Edge Server A","Edge Server B", "Edge Server C", "Cloud Data Center", "Mobile Device"]

# plt.title("Number of executed tasks per offloading site")
# plt.xlabel("Offloading sites")
# plt.ylabel("Number of executed tasks")
# plt.legend(handles, labels)
# plt.show()

# N, bins, patches = plt.hist(['Opt1', 'Opt2', 'OptWf', 'MC', 'OptWf', 'OptWf', 'OptWf', 'MC', 'MC', 'Opt2', 'OptWf', 'MC', 'MC', 'OptWf', 'MC', 'MC'], bins = 4)

# cmap = plt.get_cmap('jet')
# opt1_c = cmap(0.25)
# opt2_c =cmap(0.1)
# wfp_c = cmap(0.5)
# mc_c = cmap(0.75)
# c_map = [opt1_c, opt2_c, wfp_c, mc_c]

# for i in range(len(c_map)):
#     patches[i].set_facecolor(c_map[i])

# handles = [Rectangle((0,0), 1, 1, color=c, ec="k") for c in c_map]
# labels = ["Optimal MDP model 1", "Optimal MDP model 2", "Optimal MDP w/o failures", "Mobile Cloud"]

# plt.title("Number of offloading failures per offloading decision policy")
# plt.xlabel("Offloading policies")
# plt.ylabel("Number of offloading failures")
# plt.legend(handles, labels)
# plt.show()

# opt_ee = list(map(opt2, x))
# opt_ct = list(map(opt1, x))
# opt_mdp = list(map(wfp, x))

# plt.plot(x, opt_ee, 'r', label='opt_ee')
# plt.plot(x, opt_ct, 'g', label='opt_ct')
# plt.plot(x, opt_mdp, 'b', label='opt_mdp')

# plt.title('Rewards by MDP Optimal Policies with different weight factors')
# plt.xlabel('Number of application executions')
# plt.ylabel('Rewards')
# plt.legend()
# plt.show()

# N, bins, patches = plt.hist(['Opt1', 'Opt2', 'OptWf', 'MC', 'OptWf', 'OptWf', 'OptWf', 'MC', 'MC', 'Opt2', 'OptWf', 'MC', 'MC', 'OptWf', 'MC', 'MC'], bins = 4)

# cmap = plt.get_cmap('jet')
# opt1_c = cmap(0.25)
# opt2_c =cmap(0.1)
# wfp_c = cmap(0.5)
# mc_c = cmap(0.75)
# c_map = [opt1_c, opt2_c, wfp_c, mc_c]

# for i in range(len(c_map)):
#     patches[i].set_facecolor(c_map[i])

# handles = [Rectangle((0,0), 1, 1, color=c, ec="k") for c in c_map]
# labels = ["Optimal MDP model 1", "Optimal MDP model 2", "Optimal MDP w/o failures", "Mobile Cloud"]

# plt.title("Number of offloading failures per offloading decision policy")
# plt.xlabel("Offloading policies")
# plt.ylabel("Number of offloading failures")
# plt.legend(handles, labels)
# plt.show()

# length_of_flowers = np.random.randn(100, 3)
# Lbins = [0.1 , 0.34, 0.58, 0.82, 1.06, 1.3 , 1.54, 1.78, 2.02, 2.26, 2.5 ]
# # Lbins could also simply the number of wanted bins

# colors = ['red','yellow', 'blue']
# labels = ['red flowers', 'yellow flowers', 'blue flowers']
# plt.hist(length_of_flowers, Lbins,
#          histtype='bar',
#          stacked=False,  
#          fill=True,
#          label=labels,
#          alpha=0.8, # opacity of the bars
#          color=colors,
#          edgecolor = "k")

# # plt.xticks(Lbins) # to set the ticks according to the bins
# plt.xlabel('flower length'); plt.ylabel('count');
# plt.legend();
# plt.show()

# N, bins, patches = plt.hist(([[0, 23, 45, 90], [12, 45, 456, 567]]), bins = 5)

labels = ['Local', 'Mobile Cloud', 'Energy Efficient', 'EFOP']
plt.hist(([['MOBILE_DEVICE', 'EDGE_DATABASE', 'EDGE_COMPUTATIONAL', 'CLOUD'], ['MOBILE_DEVICE', 'MOBILE_DEVICE', 'EDGE_SERVER', 'CLOUD'], ['MOBILE_DEVICE', 'MOBILE_DEVICE', 'EDGE_SERVER', 'CLOUD'], ['MOBILE_DEVICE', 'MOBILE_DEVICE', 'EDGE_SERVER', 'CLOUD']]), 5,
         histtype='bar',
         stacked=False,  
         fill=True,
         label=labels,
         alpha=0.8, # opacity of the bars
         edgecolor = "k")

# plt.xticks(Lbins) # to set the ticks according to the bins
plt.xlabel('Offloading sites'); 
plt.ylabel('Frequency');
plt.legend();
plt.show()