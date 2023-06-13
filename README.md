# fluid-simulator
A numerical fluid simulator that I programmed a couple years ago

##06/02/23## Brandon Statner

This is a project I worked on for my computational physics course at UCSB 2 years ago in the summer of 2021 under professor Everett Lipman. I had initially intended to make a program that could simulate a flame flickering in the air. The first step of that problem was to simulate air, which meant simulating a fluid. This task ended up proving much more difficult than expected and required many hours of study and coding. I achieved a reasonable fluid simulation, but did not have time in the short (5wk) summer course to figure out how to accurately model a flame given the added levels of complexity for that problem. That being said, I feel my program is quite an accomplishment. The program- executable through fluid_sim.py - allows the user to specify size of the simulation, and add dye, wind , and temperature to the "substance". Interesting results are attainable with the right input, and included in sample_images are some snapshots and gifs of my own experiments. I hope you enjoy looking at it, using it, and playing with the program.

Below is my then-written introduction to the problem and the abstracted functionality of the code. A list of all files in this folder are indexed at the bottom of this document

##Introduction to program##

Program simulates a fluid in 2D and visualizes the movement. 
Provides user interactivity for modeling their own fluid.


Using the Eulerian Scheme, a fluid can be represented by a vector-field (U)
that represent the velocity of the fluid at the point of the
relevant vector. The evolution of these vectors is governed by the Navier-Stokes
equations. The equations are basically just Newton's law for fluids:


The first equation

Conservation of Mass: Moving fluid must be coming from somewhere. For an
incompressible fluid, this means:

div( U ) = 0


The second equation is basically just a statement of Newton's 2nd law in vector-calc form.
There are 4 relevant forces:

Advection: The particle-like tendency of the vector field to be carried along by itself

Pressure: The gradient of the pressure field exerts a force on the fluid.
it is the effect of this force that forces U to be divergence free.

Viscosity: The resistance of the fluid to changing its shape. The numerical techniques we
will be using to discretize the fluid will introduce an artificial viscous effect, so this
force will be ignored- it's not really super important to looking "fluid-like" anyways

Outside Forces: Simply gravity, and an approximate buoyant force based off of temperature


I will briefly discuss how I will approach numerically solving these equations. I will be
following the procedures detailed here (https://www.cs.ubc.ca/~rbridson/fluidsimulation/fluids_notes.pdf).
This paper explains and derives all relevant equations and methods, so if you're interested in a full
understanding, I would recommend going there. This method of solving the Navier-Stokes numerically
was first described by Jos Stam in his paper "Stable Fluids" (https://d2f99xq7vri1nk.cloudfront.net/legacy_app_files/pdf/ns.pdf)
It is only a couple of pages long, so if you are interested there is that too.


We basically fill up a grid with "particles" that aren't actually particles, but eulerian style vectors representing the state of the fluid, then we numerically approximate their behavior under the forces described above.

The numerical method is basically just splitting the Navier-Stokes equation up into those parts that I detailed above, and then approximating their effect for a small time-step DT. 

For advection, we model it by tracing the velocities of the particles back to a different point on the field and mapping that positions current speed and other quantities(dye, temp) to the current position in the next frame.

Then we apply outside forces, to all fluid particles. For my program this is just gravity. I tried to incorporate a boussinesq approximation to make the temperature of particles in my system significant, but it didn't really work all that well.

Then the divergence of the field is calculated, and used in a poisson equation to calculate the pressure field for the fluid at that frame
laplacian( pressure ) = div( U )

Which is a linear equation of sparse matrices which is then solved numerically using numpy and used to approximate the effect of pressure on the system

U' = U - grad ( pressure ) * dt

Once that was all working smoothly, I put quantities of "dye" and "temperature" into the fluid which get advected along with the fluid itself and then plug those into a color map to get a visualization of the movement.

Once that was working I wrote a simple User interactive program that allows the user to specify the details of the simulation- dump "dye" into the water (they can only draw with rectangles perpendicular to the axes), and swirl it up by adding "wind" into the system.

Besides some of the linear algebra, the code is all quite simple. I did not have time to perfect the documentation, but its not too bad.

I should also note that some basic code/methods were informed by the below sources; particularly with regards to the solving of the poisson equation and boundary conditions with numpy.

https://github.com/GregTJ/stable-fluids
http://www.philipzucker.com/annihilating-my-friend-will-with-a-python-fluid-simulation-like-the-cur-he-is/

Again, I hope you can have some fun with it.

Thanks for everything, and have a fantastic summer!


Files:

Python Scripts 

Fluid.py - Fluid object represents model of the fluid-vector system and contains functions for its evolution.

simulate_helpers.py - some functions that assist in the running of the program

fluid_sim.py - The python script that should be executed to get an interactive, visualizable simulation. Gets input from user and visualizes simulation and allows user to save the result as a gif and watch it multiple times at different speeds



Sample Images:
