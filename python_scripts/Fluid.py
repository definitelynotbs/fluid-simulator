#!/usr/bin/env python3


#
#Program simulates a fluid in 2D and visualizes the movement
#
#Brandon Statner


import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import map_coordinates
from scipy import sparse
from scipy.sparse.linalg import cg
from simulate_helpers import *

SIZE_X = 100
SIZE_Y = 100

#Ideal speed/time step seems to be when vectors move < 1 grid per timestep
MAX_SPEED = 5
DT = .1


#ambient_Temperature (Kelvin
AMB_TEMP = 300

#MAX_TEMP = 1000
FLAME_TEMP = 1900
#Thermal expansion coef
ALPH = 100 * .0037

FLAM_W = SIZE_X//5
FLAM_H = SIZE_Y//2

#Gravitational acceleration
G = 10



        

class Fluid( ):


    #Below Functions get discritized representation of necessary mathematical operators
    #1st and 2nd gradients in both dim and Laplacian
   
    #discrete gradient operator constructed using a forward finite difference method
    def getGrad( self, dim ):

        #elements in diagonol of operator
        diag = -np.ones( dim )
        
        #elements in upper off diagonol
        upprDiag = np.ones( dim )

        #construct the matrix operator for a N x 1 vector
        return sparse.diags([ diag, upprDiag ], [ 0, 1 ]  )



    #Discrete 2nd derivative operator
    def get2ndGrad( self, dim ):

        #elements in diagonol 
        diag = 2*np.ones(dim)

        #elements in off-diagonols
        offDiag = -np.ones( dim - 1)

        #Matrix rep for operation on N x 1 vector
        return sparse.diags([ offDiag, diag, offDiag ], [-1, 0, 1] )



    #discrete 2D laplacian operator
    #it is the kronecker sum of 2 1D laplacian's( 2nd derivatives )
    def getLaplacian( self ):
        
        return sparse.kronsum( self.get2ndGrad( self.Nj ), self.get2ndGrad( self.Ni ) )



    def __init__( self, shape, timeStep, ambTemp=300 ):


        #fields represent width and height of sim domain, respectively
        self.Ni = shape[0]
        self.Nj = shape[1]


        #array representation of gridspace 
        self.indices = np.indices( shape )
        self.indices[0] = self.indices[0]
        self.indices[1] = self.indices[1]

        
        #fields store size of timestep and mass density
        self.dt = timeStep

        #self.roh = ROH
        

        #field will store the velocity of all points in 2-D
        self.velocities = np.zeros( (2, self.Ni, self.Nj) )

        
        #field will store temperature values-
        self.temp = np.random.rand( self.Ni, self.Nj ) * 2*ambTemp


        #region that will be "on fire"
        self.flame = np.zeros( (self.Ni, self.Nj) )
        self.smoke = np.zeros( (self.Ni, self.Nj) )
        
        #field will store density of dye/smoke in fluid.
        self.dens = np.random.rand( self.Ni, self.Nj )/4

    

        #define gradient operator matrices:

         
        #To get the general gradient matrix for an NiN dimensional tensor, we will need
        #to use a kronecker product with the identity and Ni1 dimensional operator

        self.xGrad = sparse.kron( self.getGrad( self.Ni ), sparse.identity( self.Nj ) )
        self.yGrad = sparse.kron( sparse.identity( self.Ni ), self.getGrad( self.Nj ) )


        #2h/w = m
    #m*Yh + b = h
    #b = h - mYh = h - 2h/w* Yh = h - h/w*Y
    # y = 2h/wx + h - h/w*y = h/w( 2x + w - y)
    def getFlame( self, width, height ):

        flame = np.zeros( (self.Ni, self.Nj) )

                                                            
        for y in range( self.Nj//2 - width//2, self.Nj//2 + 1  ):

            line_pt =  height//width * ( 2*y + width  - self.Nj)

            if line_pt >= 1:
                      
                flame[self.Ni - line_pt:self.Ni, y] = ( 1 - (self.Nj//2 - y) / (width//2)  )**2
                flame[self.Ni - line_pt:self.Ni, self.Nj - y ] = (  1 - ( self.Nj//2 - y ) / (width//2)  )**2

                
        #iterate through lowering temp based on vertical distance
        for x in range( 0, self.Ni ):

            flame[x] *= ( 1 - ( self.Ni - x ) / height)**2
            
        return( flame )


    def addFlame( self, width, height, flamTemp=1900 ):
        
        #define region that is "on fire"
        fire_grid = self.getFlame( width, height )

        #light it up
        self.flame = fire_grid * flamTemp


        #smoke forms around the edges
        #convert firegrid to ones, then subtract it from the ones to get 1 - fire
        #this way, cells outside of fire region are unaffected.
        self.smoke = np.array( self.flame, dtype='bool' ) * np.ones( (self.Ni, self.Nj) ) - fire_grid


        #add the heat and smoke to sim
        self.temp += self.flame

        
        self.dens += self.smoke




        
    def setSpeeds( self, max_speed ):


        speeds = np.random.rand( 2, self.Ni, self.Nj )

        #avg speed will be max/2
        self.velocities = (speeds - .5 ) * MAX_SPEED


    #function will approximate a step in advection
    def advect( self ):


        #find initial location of advected "particles" for each gridpoint
        
        adv_points = self.indices - self.velocities*self.dt

        
        #Advect quantities using linear interpolation while respecting bounds
        #perfect function takes care of every thing already :`)
        #TODO: Optimize order and mode
        
        #advect x velocity
        self.velocities[0] = map_coordinates( self.velocities[0], adv_points, order=5, mode="wrap" )

        #advect y velocity
        self.velocities[1] = map_coordinates( self.velocities[1], adv_points, order=5, mode="wrap" )
        
        #advect temperature
        self.temp = map_coordinates( self.temp, adv_points, order=2, mode="nearest" )

        #advect density of colloid
        self.dens = map_coordinates( self.dens, adv_points, order=2, mode="wrap" )



    
    def applyPressure( self ):
        
        #-dt/roh * laplac(p)= - div( u )
        #pressure field must first be determined.
        #pressure field is the vector field that makes our fluid divergence free


        #Determining field is equivalent to solving
        #(dt/roh)* Lp = div( u )
        #u' = u - dt*p

        #We can solve it using the conjugate gradient method


        #calculate div( u )
        divrg = (self.xGrad.dot( self.velocities[0].flatten( ) )  +
                 self.yGrad.dot( self.velocities[1].flatten( ) )  )

        #solve equation
        pField = sparse.linalg.cg( ( self.getLaplacian() ), divrg )[0]

        
        #Apply pressure to V-field
        #
        self.velocities[0] -= self.xGrad.T.dot( pField ).reshape( (self.Ni, self.Nj) )
        self.velocities[1] -= self.yGrad.T.dot( pField ).reshape( (self.Ni, self.Nj) )



            
    
    
    def applyForce( self ):


        #Using Boussinesq Appr.
        #roh = roh_0 - aplh*roh_0( T - T0 )
        #Effect of gravity then is
        #F = -g*(roh_0 - aplh*roh_0( T - T0 )

        self.velocities[0] += G * (1 - ALPH( self.temp - np.average(self.temp) ) ) * self.dt 


          

    #function fixes boundary conditions
    def fixBounds( self ):


        #V's should "bounce off of walls"
        
        #bottom wall
        self.velocities[1][:, 0] = 0#abs( self.velocities[0][:, 0] )

            
        #top wall
        self.velocities[1][:, self.Nj-1] = 0#-abs( self.velocities[0][:, self.Nj-1] )

        
        #left wall
        self.velocities[0][0, :] = 0#abs( self.velocities[1][0, :] )


        #right wall
        self.velocities[0][self.Ni-1, : ] = 0#-abs( self.velocities[1][self.Ni-1, : ] )

        #Create illusion of continued burning
        self.temp += self.flame/10 * self.dt
        self.dens += self.smoke/10 * self.dt
        
    def timeStep( self ):


            self.applyForce
            self.fixBounds( )
            self.advect( )
            self.applyPressure( )


    #take a cartesian position and shape
    #select a region in the field
    def selectRegion( self, position, shape ):

        #ij indexing is backwards
        i = (self.Ni - 1) - position[1]
        j =  position[0]

        Di = shape[1]//2
        Dj = shape[0]//2

        #represent points
        region = np.zeros( (self.Ni, self.Nj) )


        #make sure Region is within the bounds
        if i - Di < 0:
            Di = i
            
        if i + Di  > self.Ni :
            Di = self.Ni - i

        if j - Dj < 0:
            Dj = j
            
        if j + Dj  > self.Nj:
            Dj = self.Nj - j


        #select region
        region[ i - Di: i + Di, j - Dj : j + Dj ] = 1

        return region

    def makeWind( self, region, speed, direction ):

        #direciton will be 1 indicating -i direction (y)
        #or 0 indicating j direction

        wind = region * speed

        #axes are flipped
        if direction == 0:
            self.velocities[1] += wind

        #y axis is reversed
        if direction == 1:
            self.velocities[0] -= wind

    def addDye( self, region, concentration ):

        self.dens +=  region * concentration
        

    def addTemp( self, region, degrees ):


        self.temp += region * degrees

        

