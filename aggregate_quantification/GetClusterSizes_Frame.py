import vtk
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np
import os
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist,squareform
import pylab as pl
def GetClusterSizes_Frame(folder,frame_id,plot_counter,interaction_radius, threshold, print_fig = False, dt = 0.00001, L = 360, R = 3):
    
    reader = vtk.vtkXMLUnstructuredGridReader()

    file = "results_"+str(int(plot_counter*(frame_id)))+".vtu"
    full_path2file = folder+"results_from_time_0/"+file
    if os.path.isfile(full_path2file):
        reader.SetFileName(full_path2file)
        reader.Update()
        output = dsa.WrapDataObject(reader.GetOutput())
        positions = output.Points
        fbs_id = output.PointData.keys().index("fbs")
        col, row = (2,len(positions))
        X = [[ 0 for x in range(col)] for y in range (row)]

        for i in range(len(positions)):
            X[i][0] = R*positions[i][0]
            X[i][1] = R*positions[i][1]
        X = np.array(X)
        # finding clusters, with periodic boundary
        for d in range(0,X.shape[1]):
            # find all 1-d distances
            pd=pdist(X[:,d].reshape(X.shape[0],1))
            # apply boundary conditions
            pd[pd>L*0.5]-=L
     
            try:
                # sum
                total+=pd**2
            except Exception:
                # or define the sum if not previously defined
                total=pd**2
        # transform the condensed distance matrix...
        total=pl.sqrt(total)
        # ...into a square distance matrix
        square=squareform(total)
        db=DBSCAN(eps=threshold, min_samples = 1, metric='precomputed').fit(square)
        print('frame # '+str(frame_id)+' number of clusters: '+str(max(db.labels_)+1))

        if print_fig:
            from mycolorpy import colorlist as mcp
            import matplotlib.pyplot as plt
            colours=mcp.gen_color(cmap="gist_rainbow",n=max(db.labels_)+1)
            # x, y coordinates of cell positions
            x = []
            y = []
            for i in range(len(positions)):
                x.append(R*positions[i][0])
                y.append(R*positions[i][1])
            figure, axes = plt.subplots(dpi=200)
            axes.set_aspect( 1 )
            for i in range(len(positions)):
                cell = plt.Circle((x[i],y[i]),interaction_radius,color=str(colours[db.labels_[i]])) #color=(0.3, 0.3, 0.3))
                axes.add_artist(cell)
            plt.xlim([0, L])
            plt.ylim([0, L])
            plt.xlabel('$\mu m$') 
            plt.ylabel('$\mu m$') 
            plt.title('time = '+str(np.round(plot_counter*(frame_id)*dt,2))+' h')
            plt.rc('axes', labelsize=15)  
            plt.rc('xtick', labelsize=12)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=12)  
            plt.rc('axes', titlesize=18)   
            plt.tight_layout()
            plt.show() 
            #figure.savefig("Frame_"+str(frame_id)+".png", bbox_inches="tight")
        
        # now we count their sizes
        clusters_array = np.full((1000,1000),-1)
        pixel_size = L/clusters_array.shape[0]
        cell_width_in_pixels = np.ceil(interaction_radius*2/pixel_size)
        pixel_area = pixel_size**2

        for cell in range(len(positions)):
            idmin_x = int(np.floor((X[cell][0] - interaction_radius)/pixel_size))
            if(idmin_x<0):
                idmin_x += clusters_array.shape[0]
            idmax_x = int(idmin_x + cell_width_in_pixels)
            if(idmax_x>clusters_array.shape[0]-1):
                idmax_x -=clusters_array.shape[0]
            idmin_y = int(np.floor((X[cell][1] - interaction_radius)/pixel_size))
            if(idmin_y<0):
                idmin_y += clusters_array.shape[1]
            idmax_y = int(idmin_y + cell_width_in_pixels)
            if(idmax_y>clusters_array.shape[1]-1):
                idmax_y -=clusters_array.shape[1]

            if(idmin_x<idmax_x):
                indexes_x = np.arange(idmin_x,idmax_x+1,1)
            else:
                indexes_x = np.concatenate([np.arange(idmin_x,clusters_array.shape[0],1),np.arange(0,idmax_x+1,1)])
    
            if(idmin_y<idmax_y):
                indexes_y = np.arange(idmin_y,idmax_y+1,1)
            else:
                indexes_y = np.concatenate([np.arange(idmin_y,clusters_array.shape[1],1),np.arange(0,idmax_y+1,1)])
    
            for i in indexes_x:
                for j in indexes_y:
                    x = (i+0.5)*pixel_size  #defines the middle of the pixel
                    y = (j+0.5)*pixel_size
                    if( (min(abs(x - X[cell][0]),abs(x - L - X[cell][0]),abs(x + L - X[cell][0])))**2 + (min(abs(y - X[cell][1]),abs(y - L - X[cell][1]),abs(y + L - X[cell][1])))**2 <= interaction_radius**2):
                        clusters_array[i,j] = db.labels_[cell]

        vals, counts = np.unique(clusters_array, return_counts=True)
        labels, aggregates_cell_number = np.unique(db.labels_, return_counts=True)
        aggrerate_areas = np.zeros(max(db.labels_)+1)
        for l in range(max(db.labels_)+1):  # l = 0 is the -1 value from the initialization
            aggrerate_areas[l] = counts[l+1]*pixel_area
        return aggregates_cell_number, aggrerate_areas
    else:
        print("no such file")
        return [], []
