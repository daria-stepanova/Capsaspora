import numpy as np
import sys
import dill
import matplotlib.pyplot as plt #yes for fig plots
import GetClusterSizes_Frame as gcs

print ('argument list', sys.argv)
# The first argument must specify the absolute path to the directory contaning simulation data
sim_folder = sys.argv[1]
# Second argument defines the last frame of the simulation (typically 1050)
last_frame = int(sys.argv[2])
print ('Analysing simulation results from folder: '+sim_folder)

folder_local_tmp = sim_folder.split("/")[-1:]
folder_local = folder_local_tmp[0]

folder = sim_folder+'/'

sim_end_time = 70.0
# sim_dt = 0.00001 for all simulations except
# initial FBS=10% and cell adhesion response 0 and 1 (Hill and steep linear), where sim_dt = 0.000004
sim_dt = 0.00001
tot_frame_num = 1050
plot_counter = np.ceil(sim_end_time/sim_dt/tot_frame_num)
R = 3 # cell radius
interaction_radius = R
threshold = interaction_radius*2.1
print_fig = False
L = 360     

agg_cell_number = []
agg_sizes = []
for i in range(last_frame):
    agg_cell_number_i, agg_sizes_i = gcs.GetClusterSizes_Frame(folder,i,plot_counter,interaction_radius,threshold,print_fig,sim_dt,L,R)
    agg_cell_number.append(agg_cell_number_i)
    agg_sizes.append(agg_sizes_i)


filename = 'globalsave_'+folder_local+'.pkl'
dill.dump_session(filename)

if len(agg_sizes)<tot_frame_num:
      for i in range(len(agg_sizes),tot_frame_num):
            agg_sizes.append([-2])
            agg_cell_number.append([-2])

filename = 'AggreatesDistribution_'+folder_local+'.txt'
f = open(filename,'w')
for t in range(tot_frame_num):
	f.write(str(t+1)+'\t')
	for i in range(len(agg_cell_number[t])):
		f.write(str(i+1)+'\t'+str(agg_cell_number[t][i])+'\t'+str(agg_sizes[t][i])+'\t')
	f.write(str(-1.0)+'\n')
f.close()

agg_area_mean = np.zeros(len(agg_sizes))
agg_area_std  = np.zeros(len(agg_sizes))
for i in range(len(agg_sizes)):
    agg_area_mean[i] = np.mean(agg_sizes[i])
    agg_area_std[i] = np.std(agg_sizes[i])

time_vec = np.linspace(0,sim_end_time,tot_frame_num)
plt.clf()
figure, axes = plt.subplots(dpi=200)
plt.fill_between(time_vec, agg_area_mean - agg_area_std, agg_area_mean + agg_area_std,  color = "#543686", alpha = 0.4)
plt.plot(time_vec,agg_area_mean,color = "#543686",linewidth = 2)
plt.ylim([0, np.round(max(agg_area_mean + agg_area_std),-2)])
#axes.errorbar(time_vec,agg_area_mean,yerr = agg_area_std,fmt='-o',color = "#543686")
plt.xlabel('time, h') 
plt.ylabel('area, $\mu m^2$') 
plt.title('Mean aggregate area') 
plt.rc('axes', labelsize=15)  
plt.rc('xtick', labelsize=12)    # fontsize of the tick labels
plt.rc('ytick', labelsize=12)  
plt.rc('axes', titlesize=18)   
plt.tight_layout()
#plt.show() 
figure.savefig("AggregateArea_"+folder_local+".png", bbox_inches="tight")
plt.close('all')

