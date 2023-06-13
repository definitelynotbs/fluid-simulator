#!/usr/bin/env python3

#
#File contains some functions necessary for the running of a simulation
#

#import Fluid

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import time
from PIL import Image


#Generate an array of snapshots of state of system
#will be used for smoother than real-time simulation of higher order problems
def genSimulation( aflud, sim_time ):


    nFrames =  int(sim_time//aflud.dt)

    
    #stores array of matrices[ Vx, Vy, Dens, Temp ] for times t 
    simulation = [ np.empty( (nFrames, 4, aflud.Ni, aflud.Nj), dtype='float' ), aflud.dt ] 

    print(simulation[1])

    #time loops to approximate waittime
    t0 = time.perf_counter( )
    avgTime = 0

    
    for t in range( 0, nFrames ):

        simulation[0][t, 0] = aflud.velocities[0]

        simulation[0][t, 1] = aflud.velocities[1]

        simulation[0][t, 2] = aflud.dens

        simulation[0][t, 3] = aflud.temp

        aflud.timeStep()

        

        #use first 10 iterations to calc avg time taken
        if ( t < 10 ):
            
            avgTime += (time.perf_counter( ) - t0)/10
            t0 = time.perf_counter()

            if t == 0:
                print("Simulation begun. Calculating time remaining...")

            else:
                print(".")
                
        #display remaining time
        else:
            if t%15 == 0:
                print("Approximately %d minutes and %d seconds remainng"
                      % (  ( (nFrames - t) * avgTime ) //60,
                           ( (nFrames - t) * avgTime ) %60  ), end='' )
            print(".")
            
                
    return simulation


def getGif( sim, timeMult, quantName='temp' ):


    dtaShape = sim[0][0, 0].shape
    
    colMap=''
    
    if quantName == 'dens':
        
        n = 2
        colMap='YlGnBu'

        #factor necessary to scale to cmap
        dataScale = 1
        
    elif quantName == 'temp' :
        
        n = 3
        colMap = 'jet'
        print('edfondofnso')
        #factor necessary to scale to cmap
        dataScale = 2500

        
    #else, if invalid input
    else:

        raise ValueError("Input field is invalid. Must be: 'temp' or 'dens'")
    

    frames = []
    
    for data in sim[0]:

        #get relevant data
        im = data[n]

        #choose colormap
        cm = plt.get_cmap( colMap )

        #map image to color
        im = cm( im/dataScale )

        #convert to RGB
        im = np.uint8( im * 255 )

        #convert to an image
        im = Image.fromarray(im)

        #resize the image
        #im = im.resize( (dim[0], dim[1]), resample=None )
        
        #add it to the Gif
        frames.append( im )

    
    frames[0].save('myFluidSim.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=sim[1]*1000/timeMult,
                    loop=0)
    

    return frames


#function displays animated simulation using plt.Animator obj
def drawSim( sim, timeMult, quantName='temp' ):

    f1, ax1 = plt.subplots()

    plt.axis('off')
    plt.grid(b=None)

    theGif = getGif( sim, timeMult, quantName )
    
    
    #use animator object to animate simulation
    im = plt.imshow(  theGif[0] , interpolation='none'  )


    def init( ):
        
        im.set_data( theGif[0] )
        return [im]


    def updateImg(i):

        im.set_array( theGif[i] ) #/ dataScale ) 
        
        return[im]


    animator = ani.FuncAnimation( f1, updateImg, init_func=init,
                                  frames=len( theGif ), interval=sim[1]*1000/timeMult, blit=False)
    
    plt.show( )



#function shows a single frame of an array
def showFrame( arr ):

    f1, ax1 = plt.subplots( )
    
    plt.axis('off')
    plt.grid(b=None)
    
    ax1.imshow( arr, cmap='jet', interpolation='none' )

    
    f1.show()

