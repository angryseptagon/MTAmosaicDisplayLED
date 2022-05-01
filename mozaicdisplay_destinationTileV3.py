import cadquery as cq
import numpy as np

gridHeight = 30
#standard thickness of walls
wallThickness = 2

unitSize = 25.4
Height = 16*unitSize
Width = 8*unitSize
ledHoleDia = 5

#used to make sure there is enough clearance to push in LEDs in lofts
ledHeight = 7

# this variable is only used to make the simplified version. make this the same as led Height to ensure there is enough clearance if you push them through
baseThickness = 7

#make part without lofts, they are broken
simplifiedPart = False

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
               #make outside walls
               [-4,-8,-4,8],
               [-4,-8,4,-8],
               [4,8,4,-8],
               [4,8,-4,8],
               
               #make vertical walls
               [1,8,1,-8],
               [-1,8,-1,-8],
               [2,8,2,-8],
               [-2,8,-2,-8],
               
               #make horizontal walls
               [3,0,-3,0],
               [4,2,-4,2],
               [4,-2,-4,-2],
               [4,4,-4,4],
               [4,-4,-4,-4],
               [4,6,-4,6],
               [4,-6,-4,-6],
               
               #make left slanted walls
               [-1,-8,-4,-2],
               [-1,-4,-3,0],
               [2,-6,-4,6],
               [4,-6,-2,6],
               
               #make right slanted walls ordered right to left
               [1,-8,4,-2],
               [1,-4,3,0],
               [-2,-6,4,6],
               [-4,-6,2,6],
               [-3,0,0,6],
               ]

listOfCurvePts = [
    #make curved walls ordered bottom to top
    [-2,-6,180,2],
    [1,-6,180,2],
    [2,-6,270,2],
    [3,-1,0,1],
    [-3,-1,90,1],
    [-3,1,180,1],
    [3,1,270,1],
    [3,1,0,1],
    [3,3,0,1],
    [-3,3,90,1],
    [2,6,0,2],
    [1,6,90,2],
    [-2,6,90,2]
    ]

walls = cq.Workplane("XY")
for j in listoflines:
    walls = walls.union(straightWall(j))

for j in listOfCurvePts:
    walls = walls.union(curvedWall(j))

islands = cq.Workplane("XY").rect(Width,Height).extrude(gridHeight).cut(walls)
islandList = islands.val().Solids()

if(simplifiedPart):
    #number labels take a long time to render
    # numberLabels = cq.Workplane("XY")
    # numberText = 0
    
    massCenters=[]
    for i in islandList:
        inVector=cq.Shape.centerOfMass(i).projectToPlane(cq.Plane((0,0,baseThickness)))
        # numberLabels = numberLabels.union(cq.Workplane("XY").text(str(numberText),8,1,cut=False).translate(inVector),glue=true)
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
            , glue = True
            )
    result = cq.Workplane("XY").rect(Width+wallThickness,Height+wallThickness).extrude(gridHeight).cut(lofts)
    show_object(result)