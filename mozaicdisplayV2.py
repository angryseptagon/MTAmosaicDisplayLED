import cadquery as cq
import numpy as np

gridHeight = 30
#standard thickness of walls
wallThickness = 2

unitSize = 24.8
Height = 12*unitSize
Width = 8*unitSize
ledHoleDia = 5

#used to make sure there is enough clearance to push in LEDs in lofts
ledHeight = 7

# this variable is only used to make the simplified version. make this the same as led Height to ensure there is enough clearance if you push them through
baseThickness = 7

#make part without lofts, they are broken
simplifiedPart = True

def straightWall(i):
    x1 = i[0]
    y1 = i[1]
    x2 = i[2]
    y2 = i[3]
    distance = np.linalg.norm([x2-x1,y2-y1])*unitSize
    angle = np.degrees(np.arctan2(y2-y1,x2-x1))
    out = (cq.Workplane("XY")
           .rect(distance,wallThickness,centered=(False,True))
           .extrude(gridHeight).rotate((0,0,0),(0,0,1),angle)
           .translate([x1*unitSize,y1*unitSize,0])
           )
    return out

def curvedWall(i):
    x = i[0]*unitSize
    y = i[1]*unitSize
    deg = i[2]
    radius = i[3]*unitSize
    out = (cq.Workplane("XY")
            .lineTo(radius+wallThickness/2,0)
            .radiusArc((0,radius+wallThickness/2),-radius-wallThickness/2)
            .lineTo(0,radius-wallThickness/2)
            .radiusArc((radius-wallThickness/2,0),radius-wallThickness/2)
            .close()
            .extrude(gridHeight)
            .rotate((0,0,0),(0,0,1),deg)
            .translate([x,y,0])
            )
    return out

# curveWallTest = curvedWall([1,1,45])

listoflines = [#make outside walls
        [-4,-6,-4,6],
        [-4,-6,4,-6],
        [4,6,4,-6],
        [4,6,-4,6],
        
        #middle vertical walls
        [1,6,1,-6],
        [2,6,2,-6],
        [-1,6,-1,-6],
        [-2,6,-2,-6],
        #middle vertical wall not all the way through
        [3,6,3,-2],
        
        #middle horizontal walls
        [4,4,-4,4],
        [4,2,-4,2],
        [4,-4,-4,-4],
        #horizontal segments 2 unit length
        [4,3,2,3],
        [-4,3,-2,3],
        [4,-3,2,-3],
        [-4,-3,-2,-3],
        #horizontal segments 6 units length
        [4,-2,-2,-2],
        [4,0,-2,0],
        [-4,-1,2,-1],
        #horizontal segment 4 unitlength
        [-2,1,2,1],
        
        #slantedwalls left
        [-4,2,0,-6],
        [-4,6,2,-6],
        [-2,6,4,-6],
        #straightwalls right
        [4,2,0,-6],
        [4,6,-2,-6],
        [2,6,-4,-6],
        [-4,-2,0,6]]

listOfCurvePts = [
    #make curvedwalls
    #4 corners
    [2,4,0,2],
    [-2,4,90,2],
    [-2,-4,180,2],
    [2,-4,270,2],
    #middlecurves
    [-2,-1,90,2],
    [-2,1,180,2],
    [2,-1,0,2],
    [2,1,270,2],
    #curve for "1" character
    [-3,6,270,2]
    ]

walls = cq.Workplane("XY")
for j in listoflines:
    walls = walls.union(straightWall(j))

for j in listOfCurvePts:
    walls = walls.union(curvedWall(j))

islands = cq.Workplane("XY").rect(Width,Height).extrude(baseThickness).cut(walls)
islandList = islands.val().Solids()

if(simplifiedPart):
    #number labels take a long time to render
    # numberLabels = cq.Workplane("XY")
    # numberText = 0
    
    massCenters=[]
    for i in islandList:
        inVector=cq.Shape.centerOfMass(i).projectToPlane(cq.Plane((0,0,baseThickness)))
        # numberLabels = numberLabels.union(cq.Workplane("XY").text(str(numberText),8,1,cut=False).translate(inVector))
        # numberText = numberText+1
        massCenters.append(inVector)
    
    #islands = islands.pushPoints(massCenters).hole(ledHole) #making the holes here may make it easier to 3d print but it cuts off the holes
    
    result = walls.union(islands).pushPoints(massCenters).hole(ledHoleDia)
    # add rounded edges
    result = result.pushPoints([(0,0,0)]).rect(Width,Height,forConstruction=True).vertices().circle(wallThickness/2).extrude(gridHeight)
    show_object(result)


if(simplifiedPart==False):
    lofts = cq.Workplane("XY")
    for i in islandList:
        lofts = lofts.union(
            cq.Workplane(i).translate([0,0,gridHeight])
            .faces("<Z").wires().toPending()
            .workplane(centerOption="CenterOfMass",offset=gridHeight).circle(ledHoleDia/2)
            .loft()
            .faces("<Z")
            .circle(ledHoleDia/2)
            .extrude(-ledHeight)
            )
    result = cq.Workplane("XY").rect(Width+wallThickness,Height+wallThickness).extrude(gridHeight).cut(lofts)
    show_object(result)

