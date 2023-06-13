#!/usr/bin/env python3

from Fluid import Fluid
import simulate_helpers as sim



#CONSTANTS that don't really need user specified input

#Thermal expansion coef. (scaled by 100)
ALPH = .37

#gravitational acceleration
G = 10


#USER will have option to customize these in program
#These are the default values



#used to scale movement
MAX_SPEED = 5

#timestep magnitude
DT = .1

#Ambient temperature- effects buoyancy
AMB_TEMP= 300


#bool stores whether or not there is a fire
isFire = True

#Flame temperature
FLAME_TEMP = 1900


#ambient temperature
#get input from user



def getPosInt( askString  ):

    num = 0
    haveInt = False
    
    while not haveInt:
        try:
            print("\n")
            num = int(input( askString ) )
            
            if num <=0 :
                      
             raise ValueError("Dimensions must be greater than 0")
            
            haveInt = True
            
        except ValueError:
            print("Please enter a valid number > 0.")

    return num


def getPosFloat( askString ):
    
    num = 0
    haveNum = False
    
    while not haveNum:
        try:
            print("\n")
            num = float(input( askString ) )
            
            if num <=0 :
                      
             raise ValueError("Value must be 0")
            
            haveNum = True
            
        except ValueError:
            print("Please enter a valid float> 0.")

    return num

def getAnyFloat( askString ):
    
    num = 0
    haveNum = False
    
    while not haveNum:
        try:
            print("\n")
            num = float(input( askString ) )
            
            haveNum = True
            
        except ValueError:
            print("Please enter a valid float> 0.")

    return num

    
def getAnswer( question ):
    
    needAns = True

    
    usrAns= False
    

    response = ''

    #get an answer
    while needAns:
        
        print("\n")
        print(question)
        
        try:
            
            response =  input("Enter y/n: ") 
            print(response)
            
            if (response == 'y') or (response == 'Y'):
                usrAns = True
                needAns = False
            elif (response == 'n') or (response == 'N'):
                usrAns = False
                needAns = False
            else:
                raise TypeError("Invalid input from user. Need, 'y' or 'n'")
            
        except TypeError:
            print("Answer must be a 'y' or an 'n'.")

    return usrAns



def getFlameShape( needHelp, shape ):
    
    if needHelp:
        
        print("\nThe flame will be a triangle of high temp centered on the bottom of the grid.")
        print("You will now be prompted to enter it's dimensions.")
        input("\nPress <enter> to continue>")

    #Get valid input for shape of fire

    #width
    needInput = True

    while needInput:
        
        width = getPosInt("Enter desired width of Flame: ")
        
        if  width < shape[1]:
            needInput = False
        else:
            print("Flame width must be less than size of Axis 0")

    #height
    needInput = True
    
    while needInput:
        
        height = getPosInt("Enter desired height of Flame: ")
        
        if height < shape[0]:
            needInput = False
        else:
            print("Flame height must be less than size of Axis 1.") 
            
    return [ width, height]


def getRegion( Xmax, Ymax ):

    #get position from user

    point = [0,0]
    
    #x point
    needInput=True

    while needInput:
        
        point[0] = getPosInt("Enter an x-coordinate: ")


        if point[0] < Xmax:
            
            needInput = False
        else:
            print("X coordinate must be within viewable domain ( x < %d ) " % Xmax)


    #y point
    needInput=True

    while needInput:
        
        point[1]  = getPosInt("Enter an y-coordinate: ")

        if point[1]  < Ymax:
            
            needInput = False
            
        else:
            print("Y coordinate must be within viewable domain ( y < %d ) " % Ymax)        


    
    #get input for shape of region

    rShape = [0,0]

    #width
    rShape[0] = getPosInt("Enter a width: ")


    #height
    rShape[1]  = getPosInt("Enter height: ")



    return [point, rShape] 


def getWind( aFluid ):

    
    reg = getRegion( aFluid.Nj, aFluid.Ni )

    vel = getAnyFloat("Enter the desired wind speed:")

    direction = -1

    print("Now, specify the direction")
    while direction != 0 and direction != 1 :

        try :
            print("For x-ward wind enter < 0 > ")
            print("For y-ward wind enter < 1 > ")

            direction = int( input("\nEnter < 0 >  or  < 1 > : ") )
                          
        except ValueError:
            print("Please enter an integer, 0 or 1.")
            
    #add the wind
    regionArr = aFluid.selectRegion( reg[0], reg[1] )
    print(regionArr)
    aFluid.makeWind( regionArr, vel, direction)



def getDye( aFluid ):

    reg = getRegion( aFluid.Nj, aFluid.Ni )

    #get concentration

    conc = 0
    needNum = True

    while needNum:
    
        conc = getPosFloat("Enter a concentration between 0 & 1: ")
        
        if conc  <= 1:
            needNum = False
            
    #add the dye
    regionArr = aFluid.selectRegion( reg[0], reg[1] )

    aFluid.addDye( regionArr, conc )


print("\n\nWelcome to the megafluid simulator!")


#get user selection of mode
print("\nThere are 3 available modes: ")
print("Default gets you straight to the program")
print("Custom allows you to specify your own simulation parameters")

userIn = -1
while userIn != 0 and userIn != 1 :

    try :
        print("\nTo run the default program, enter 0.")
        print("To run the custom program, enter 1.")

        userIn = int( input("\nEnter < 0 >  or  < 1 > : ") )
                      
    except ValueError:
        print("Please enter an integer, 0 or 1.")

#set mode
mode = ''

if userIn == 0:
    mode = 'default'

elif userIn == 1:
    mode = 'custom'


needHelp = not getAnswer("Would you like to disable help messages?")

if needHelp:            
    print("\nYou will now be prompted to enter dimensions for your simulation")
    print("Please note that high resolution simulations can take some time.")
    print("Simulations on scale of 10x10 to 200x200 resolve in seconds to minutes")
    print("500x500 and greater can take tens of minutes.")
    print("(100x100) is a good place to start")
          
    input("\nPress <enter> to continue")


#important user input parameters in all caps
SHAPE = [0, 0]

#get proper input for both dimensions from user
for i in range(2):
    
    SHAPE[1-i] = getPosInt("\nEnter size of axis %i: " % (i) )


#Cartesian storage of shape for readability
Ymax = SHAPE[0]
Xmax = SHAPE[1]

#DEFAULT FLAMESIZE: depends on user input:
#FLAME SHAPE ( height and width )default values
FLAME_W = SHAPE[0] // 2

FLAME_H = SHAPE[1] // 2


#CUSTomization of parameters begins
if mode == 'custom' :
    #Get input for speed          
    if needHelp:           
        print("\nYou will now be prompted to enter a max speed, used for scaling velocities in simulation.")
        print("Reccomended values are 1-50 for simulations on scales 10x10 and 100x100")
        input("\nPress <enter> to continue")



    haveSpeed = False

    while not haveSpeed:
        try:
            
            MAX_SPEED = float( input("\nEnter speed: " ) )

            haveSpeed = True              
        except ValueError:

            print("Please enter a valid float.")



    #Get input for timestep
    if needHelp:           
        print("\nYou will now be prompted to enter a timestep, used for numerical approximations.")
        print("Reccomended value is .1 . Time of simulation increases exponentially w this input.")
        input("\nPress <enter> to continue")

    DT = getPosFloat("Enter timestep: " )
        



    #Does the user want a flame?

    if Xmax > 1 and Ymax > 1:
        
        isFire = getAnswer("Would you like a flame in your simulation?")
    else:
        isFire = False
        
    if isFire:

        fshape = [0, 0]
        
        fShape = getFlameShape( needHelp, SHAPE)

        FLAME_W = fShape[0]
        Flame_H = fshape[1] 
            
        print("\nDefault flame temperature is 1900K")
        
        needTemp = getAnswer("Would you like to enter a custom flame temp?")
                  
        if needTemp:

            
            haveTemp = False
            while not haveTemp:

                FLAME_TEMP = getPosFloat("Enter flame temp > 1500: ")
                if FLAME_TEMP >= 1500:
                    haveTemp = True
                else:
                    print("flame temp must be greater than 1500")
        
                
        else:
            FLAME_TEMP = 1900




#Simulation time
ourFluid = Fluid( SHAPE, DT, )

#initialize velocities
ourFluid.setSpeeds( MAX_SPEED )

#if in default mode, ask if user wants flame:

if mode == 'default':
    
    if Xmax > 1 and Ymax > 1:
        
        isFire = getAnswer("Would you like a flame in your simulation?")
    else:
        isFire = False


    if isFire:

        fshape = [ 0, 0 ]
        fShape = getFlameShape( needHelp, SHAPE)

        FLAME_W = fShape[0]
        Flame_H = fshape[1]
       
            
#if theres a flame, add it
if isFire:
    ourFluid.addFlame( FLAME_W, FLAME_H, FLAME_TEMP )

#allow the user to add to simulation.


print("\nThe basics of your simulation are all set!")

print("Now, please specify if you would like to add wind, dye, or temp to your fluid")

#keep simulating until user wants to stop
kpSim = True
while kpSim:
    
    if Xmax > 1 and Ymax > 1:
        needWind = getAnswer("Would you like to add any wind to your fluid? (say yes!)")
    else:
        needWind = False


    if needHelp and needWind:
        print("\nWind can be added to rectangular regions in the simulation")
        print("You will now be prompted to specify the center point of one such region")
        print("You then will specify the width of the region, the magnitude of the")
        print("wind's velocity, and it's direction.")
        print("You may input as many regions as you desire.")

        input( "\nPress <enter> to continue")
        
    while needWind:

        getWind( ourFluid )
        
        #ask if user wants more wind
        needWind = getAnswer("Wind added! Would you like to add any more?")



    if Xmax > 1 and Ymax > 1:
        needDye = getAnswer("Would you like to add any dye to your fluid? (say yes!)")
    else:
        needDye = False

    if needHelp and needDye:
        print("\Dye can be added the same as wind,")
        print("in rectangles specified by location and shape, and density")

        input( "\nPress <enter> to continue")

    while needDye:

        getDye( ourFluid )
        
        #ask if user wants more wind
        needDye = getAnswer("Dye added! Would you like to add any more?")


    #Once the user has finished there, we can simulate the fluid!!
    if needHelp:
        print("You will now be asked to specify a time for your simulation")
        print("Increasing the time of simulation can drastically increase the time")
        print("required to reneder the sim. I would reccomend beginning with only 5 to 10 seconds")
        print("you can always come back and simulate for longer!")
        
        input( "\nPress <enter> to continue")

    simTime = getPosFloat("Please enter a time length: ")

    if needHelp:
        print("\nWe will now render your simulation")
        print("A GIF file of your simulation will be saved with the title myFluidSim.gif")

        input( "\nPress <enter> to continue")
        
    userSim = sim.genSimulation( ourFluid, simTime )

    if needHelp:
        print("\nYour Simulation has been successfully rendered and saved!")
        print("You will now be asked to input a multiplier for time")
        print("When your sim is displayed it will be at this rate.")
        print("it may be a large or tiny number- slow, or fast speed")
        print("Enjoy!")

        input( "\nPress <enter> to continue")

    kpWatch = True

    while kpWatch:

        #get time mult 
        timeMult = getPosFloat("Please enter a watch speed: ")


        #get quantity to view
        userIn = -1

        while userIn != 0 and userIn != 1 :

            try :
                print("To see temperature map enter < 0 > ")
                print("To see dye density enter < 1 > ")

                userIn = int( input("\nEnter < 0 >  or  < 1 > : ") )
                              
            except ValueError:
                print("Please enter an integer, 0 or 1.")
                
            if userIn == 0:
                viewQuant = 'temp'

            elif userIn == 1:
                viewQuant = 'dens'


        sim.drawSim( userSim, timeMult, viewQuant )

        kpWatch = getAnswer("Would you like to watch it again w a different time or colors?")

    kpSim = getAnswer("Would you like to add more dye and wind to your simulation?")


print("\nThank you for participating. Have a great day!")
