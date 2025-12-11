from yade import pack, plot, qt

##### SETUP #####
plot.plots = {'t':('velocityw1', 'surfacevelocityw1', 'surfacevelocityabovethreshw1', 'maximumsurfacevelocityw1', 'kineticSum')}

## MATERIALS ##
O.trackEnergy = True
# provide a friction material and set Young's Modulus, Poisson's ratio, density, a label to identify the material, and friction angle, which is used to calculate the friction coefficient
cloth = O.materials.append(FrictMatCDM(alpha = radians(10), sigmaMax = 9e8, young = 4e9, poisson = 0.2, density = 2000, frictionAngle = radians(17), label = 'cloth'))
# define sand material second since spherePack takes the last defined material
O.materials.append(FrictMatCDM(alpha = radians(5),sigmaMax = 1.9e9, young = 7.2e10, poisson = 0.17, density = 2650, frictionAngle = radians(20), label = 'sand'))

## NUMBER DEFINITIONS ##
# scaling factor for relevant parts of the simulation
scalingFactor = 40
numParticles = 10000

# relevant parts of the simulation
width = 5e-2 * cbrt(scalingFactor)
widthUnit = width/10
length = 1.82e-1 * scalingFactor 
lengthUnit = length/10
height = -1.05e-1 * scalingFactor 
one = 1e-1 * scalingFactor

# define grains
r = 1.5e-4 * scalingFactor # iter is directly related to r
h = one * 0.6


## CREATING OBJECTS IN YADE ##
# only edit if you know what you're doing!

# define door
door = [
    facet([[width,0,one - 2*one],[width,width,one - 2*one],[width,0,one]], material='cloth'),
    facet([[width,width,one - 2*one],[width,width,one],[width,0,one]], material='cloth')
]

# add door
O.bodies.append(door)
# add ramp with walls to simulation
O.bodies.append(
    [
        # add floor on the plane 3x + 5.196z  =  0
        facet([[0,0,0],[length,width,height],[0,width,0]]),
        facet([[0,0,0],[length,width,height],[length,0,height]]),
        # add walls
        facet([[0,0,0],[0,0,one],[length,0,height]]),
        facet([[0,width,0],[0,width,one],[length,width,height]]),
        facet([[0,0,0],[0,0,one],[0,width,0]]),
        facet([[0,0,one],[0,width,0],[0,width,one]]),
        facet([[0,0,one],[length,0,height],[length,0,height+one]]),
        facet([[0,width,one],[length,width,height],[length,width,height+one]]),
        # add landing area
        facet([[length - one,0 - one,height],[length - one,width + one,height],[length + 2*one, width + one, height]], material='cloth'),
        facet([[length + 2*one, width + one, height],[length + 2*one, 0 - one, height],[length - one, 0 - one, height]], material='cloth')
    ]
)

sp = pack.SpherePack()
sp.makeCloud((0,0,0),(width,width,h),rMean=r,porosity=0.9,num=numParticles)
# add grains to simulation
sp.toSimulation()

# run for 5 virtual seconds
simLength = int(1/PWaveTimeStep() * 10)

# create and set the simulation view
v = qt.View()
v.lookAt, v.viewDir, v.eyePosition, v.upVector = (Vector3(0.03992180520697213852,0.9400607547759574079,-0.2158212119544579144),Vector3(0.02955093752978604424,0.9746965006718428803,-0.2215704711128608784),Vector3(0.01037086767718609602,-0.03463574589588552105,0.005749259158402977854),Vector3(-0.05212551937053259976,0.2228683612338996367,0.9734539659332990258))
# calculate the physics! reset all current forces -> set sphere bounding boxes to collide with each other, handle sphere-sphere collisions, frictmat-frictmat interactions,
# and model collisions using the Hertz-Mindlin contact model, finally, apply newtonian gravity and damping
O.engines = [
    ForceResetter(),
    InsertionSortCollider([Bo1_Sphere_Aabb(),Bo1_Facet_Aabb()]),
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom(),Ig2_Facet_Sphere_ScGeom()],
        [Ip2_FrictMatCDM_FrictMatCDM_MindlinPhysCDM()],
        [Law2_ScGeom_MindlinPhysCDM_HertzMindlinCDM()]
    ),
    NewtonIntegrator(gravity = (0,0,-9.81*scalingFactor), damping = 0.04),
    PyRunner(command = "addPlotData()",iterPeriod = 1),
    PyRunner(command = "savePlot()",iterPeriod = simLength-1),
    PyRunner(command = "openDoor()",iterPeriod = int(simLength*0.03)),
    SnapshotEngine(iterPeriod = int(simLength/300),fileBase = '/home/mikeoat/scripts/python/sand/yade/img/periodicSand-',label = 'snapshooter'),
    VTKRecorder(iterPeriod = 1000, fileName='vtk/dune-', recorders=['spheres','facets'])
]

# for the definitions of the grains in this simulation, 1/sampleRate happens to be less than
# PWaveTimeStep(), which is ideal
O.dt = PWaveTimeStep()

##### RUN SIMULATION #####

O.run(simLength)
print("simulation completed successfully")
 
##### FUNCTION DEFINITIONS #####

# create class that returns references based on window parameters
class GrainList:
    def __init__(self, xmin, xmax, ymin, ymax):
        # measurement bounding box parameters
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    # get IDs of bodies in window
    def getBodiesInWindow(self):
        idsOfBodiesInWindow = []
        for i in O.bodies:
            # check if particle is in bounding box and if it belongs to the material 'sand'
            if i.state.pos[0] >= self.xmin and i.state.pos[0] <= self.xmax and i.mat.label == 'sand':
                if i.state.pos[1] >= self.ymin and i.state.pos[1] <= self.ymax:
                    idsOfBodiesInWindow.append(i.id)
        return idsOfBodiesInWindow

    def getAverageDistance(self):
        # use particles in defined bounding box
        bodyIDs = self.getBodiesInWindow()
        bodyDistances = []
        for i in bodyIDs:
            # get normal distance vectors along the plane 3x + 5.196z = 0
            bodyDistances.append(abs(3*O.bodies[i].state.pos[0] + 5.196*O.bodies[i].state.pos[2])/sqrt(3**2 + 5.196**2))
        # divide by zero safety
        if len(bodyDistances) == 0:
            return 0
        # calculate and return average of all values
        return sum(bodyDistances)/len(bodyDistances)

    def getAverageNormalVelocity(self):
        # use particles in defined bounding box
        bodyIDs = self.getBodiesInWindow()
        bodyVelocities = []
        for i in bodyIDs:
            # get velocity components only along the normal of 3x + 5.196z = 0
            bodyVelocities.append(abs(3*O.bodies[i].state.vel[0] + 5.196*O.bodies[i].state.vel[2])/sqrt(3**2 + 5.196**2))
        # divide by zero safety
        if len(bodyVelocities) == 0:
            return 0
        # calculate and return average of all values
        return sum(bodyVelocities)/len(bodyVelocities)

    def getAverageNormalSurfaceVelocity(self, threshold):
        # use particles in defined bounding box
        bodyIDs = self.getBodiesInWindow()
        bodyVelocities = []
        for i in bodyIDs:
            # only append to bodyVelocities if the normal distance vector along 3x + 5.196z = 0's magnitude is higher than the user-provided threshold
            if abs(3*O.bodies[i].state.pos[0] + 5.196*O.bodies[i].state.pos[2])/sqrt(3**2 + 5.196**2) > threshold:
                bodyVelocities.append(abs(3*O.bodies[i].state.vel[0] + 5.196*O.bodies[i].state.vel[2])/sqrt(3**2 + 5.196**2))
        # divide by zero safety
        if len(bodyVelocities) == 0:
            return 0
        # calculate and return average of all values
        return sum(bodyVelocities)/len(bodyVelocities)

    def getHighestNormalVelocity(self):
        # use particles in defined bounding box
        bodyIDs = self.getBodiesInWindow()
        bodyVelocities = []
        for i in bodyIDs:
            # get velocity components only along the normal of 3x + 5.196z = 0
            bodyVelocities.append(abs(3*O.bodies[i].state.vel[0] + 5.196*O.bodies[i].state.vel[2])/sqrt(3**2 + 5.196**2))
        # empty array safety
        if len(bodyVelocities) == 0:
            return 0
        # return only the greatest body velocity
        return max(bodyVelocities)

### DATA COLLECTION ###
# add relevant data to the plot, to be made into a text file
def addPlotData():
    window1 = GrainList(5*lengthUnit,6*lengthUnit,0,width)
    window2 = GrainList(5*lengthUnit,5.1*lengthUnit,3*widthUnit,4*widthUnit)
    window3 = GrainList(one,one + (0.1 * one),0.1 * one,0.2 * one)
    plot.addData(
        t = O.iter,
        # plot average distance for each window
        distancew1 = window1.getAverageDistance(),
        distancew2 = window2.getAverageDistance(),
        distancew3 = window3.getAverageDistance(),
        # plot average velocity for each window
        velocityw1 = window1.getAverageNormalVelocity(),
        velocityw2 = window2.getAverageNormalVelocity(),
        velocityw3 = window3.getAverageNormalVelocity(),
        # plot average of velocities higher than overall average velocity for each window
        surfacevelocityw1 = window1.getAverageNormalSurfaceVelocity(window1.getAverageDistance()),
        surfacevelocityw2 = window2.getAverageNormalSurfaceVelocity(window2.getAverageDistance()),
        surfacevelocityw3 = window3.getAverageNormalSurfaceVelocity(window3.getAverageDistance()),
        # plot average of velocities higher than overall average velocity * 1.5 (0.75 of the overall domain) for each window
        surfacevelocityabovethreshw1 = window1.getAverageNormalSurfaceVelocity(window1.getAverageDistance() * 1.5),
        surfacevelocityabovethreshw2 = window2.getAverageNormalSurfaceVelocity(window2.getAverageDistance() * 1.5),
        surfacevelocityabovethreshw3 = window3.getAverageNormalSurfaceVelocity(window3.getAverageDistance() * 1.5),
        # plot the highest velocity for each window
        maximumsurfacevelocityw1 = window1.getHighestNormalVelocity(),
        maximumsurfacevelocityw2 = window2.getHighestNormalVelocity(),
        maximumsurfacevelocityw3 = window3.getHighestNormalVelocity(),
        # plot the overall kinetic energy of the system
        kineticSum = O.energy.items()[1][1]
    )

# output all plotted variables to data.txt
def savePlot():
    plot.saveDataTxt('./data.txt')
    print("done!")

# move facets defined in door:[] underneath the ramp
def openDoor():
    print('door opened!')
    for i in range(2):
        O.bodies[i].state.pos = Vector3(5.196,0 + 0.5*widthUnit,-30*one)
