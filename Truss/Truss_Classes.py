#region imports
import math
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from GraphicsView_App import RigidLink, RigidPivotPoint
#endregion

#region class definitions
class Position():
    """
    I made this position for holding a position in 3D space (i.e., a point).  I've given it some ability to do
    vector arithmetic and vector algebra (i.e., a dot product).  I could have used a numpy array, but I wanted
    to create my own.  This class uses operator overloading as explained in the class.
    """
    def __init__(self, pos=None, x=None, y=None, z=None):
        """
        x, y, and z have the expected meanings
        :param pos: a tuple (x,y,z)
        :param x: float
        :param y: float
        :param z: float
        """
        #set default values
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        #unpack position from a tuple if given
        if pos is not None:
            self.x, self.y, self.z = pos
        #override the x,y,z defaults if they are given as arguments
        self.x=x if x is not None else self.x
        self.y=y if y is not None else self.y
        self.z=z if z is not None else self.z

    #region operator overloads $NEW$ 4/7/21
    def __eq__(self, other):
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        if self.z != other.z:
            return False
        return True

    def __add__(self, other):
        return Position((self.x+other.x, self.y+other.y,self.z+other.z))

    def __iadd__(self, other):
        if other in (float, int):
            self.x += other
            self.y += other
            self.z += other
            return self
        if type(other) == Position:
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self

    def __sub__(self, other):
        return Position((self.x-other.x, self.y-other.y,self.z-other.z))

    def __isub__(self, other):
        if other in (float, int):
            self.x -= other
            self.y -= other
            self.z -= other
            return self
        if type(other) == Position:
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            return self

    def __mul__(self, other):
        if type(other) in (float, int):
            return Position((self.x*other, self.y*other, self.z*other))
        if type(other) is Position:
            return Position((self.x*other.x, self.y*other.y, self.z*other.z))

    def __rmul__(self,other):
        return self*other

    def __imul__(self, other):
        if type(other) in (float, int):
            self.x *= other
            self.y *= other
            self.z *= other
            return self

    def __truediv__(self, other):
        if type(other) in (float, int):
            return Position((self.x/other, self.y/other, self.z/other))

    def __idiv__(self, other):
        if type(other) in (float,int):
            self.x/=other
            self.y/=other
            self.z/=other
            return self
    #endregion

    def set(self,strXYZ=None, tupXYZ=None):
        #set position by string or tuple
        if strXYZ is not None:
            cells=strXYZ.replace('(','').replace(')','').strip().split(',')
            x, y, z = float(cells[0]), float(cells[1]), float(cells[2])
            self.x=float(x)
            self.y=float(y)
            self.z=float(z)
        elif tupXYZ is not None:
            x, y, z = tupXYZ
            self.x=float(x)
            self.y=float(y)
            self.z=float(z)

    def getTup(self): #return (x,y,z) as a tuple
        return (self.x, self.y, self.z)

    def getStr(self, nPlaces=3):
        return '{}, {}, {}'.format(round(self.x, nPlaces), round(self.y,nPlaces), round(self.z, nPlaces))

    def mag(self):  # normal way to calculate magnitude of a vector
        return (self.x**2+self.y**2+self.z**2)**0.5

    def normalize(self):  # typical way to normalize to a unit vector
        l=self.mag()
        if l<=0.0:
            return
        self.__idiv__(l)

    def getAngleRad(self):
        """
        Gets angle of position relative to an origin (0,0) in the x-y plane
        :return: angle in x-y plane in radians
        """
        l=self.mag()
        if l<=0.0:
            return 0
        if self.y>=0.0:
            return math.acos(self.x/l)
        return 2.0*math.pi-math.acos(self.x/l)

    def getAngleDeg(self):
        """
        Gets angle of position relative to an origin (0,0) in the x-y plane
        :return: angle in x-y plane in degrees
        """
        return 180.0/math.pi*self.getAngleRad()

class Rectangle():
    def __init__(self, top=None, left=None, bottom=None, right=None):
        self.top=0 if top is None else top
        self.left = 0 if left is None else left
        self.bottom=0 if bottom is None else bottom
        self.right=0 if right is None else right

    def height(self):
        return self.top-self.bottom

    def width(self):
        return self.right-self.left

    def centerY(self):
        return self.bottom+self.height()/2.0

    def centerX(self):
        return self.left+self.width()/2.0

class Material():
    def __init__(self, uts=None, ys=None, modulus=None, staticFactor=None):
        self.uts = uts
        self.ys = ys
        self.E=modulus
        self.staticFactor=staticFactor

class Node():
    def __init__(self, name=None, position=None, is_roller=False):
        self.name = name
        self.position = position if position is not None else Position()
        self.is_roller = is_roller  # Flag to indicate if the node is a roller joint
        self.graphic = RigidPivotPoint(position.x, position.y, 10, 30, is_roller=self.is_roller)

    def __eq__(self, other):
        """
        This overloads the == operator such that I can compare two nodes to see if they are the same node.
        """
        if self.name != other.name:
            return False
        if self.position != other.position:
            return False
        return True

class Link():
    def __init__(self, name="", node1="1", node2="2", width=0.1, thickness=0.05, material="steel", length=None, angleRad=None):
        """
        Enhanced definition of a link with additional attributes for width, thickness, and material.
        """
        self.name = name
        self.node1_Name = node1
        self.node2_Name = node2
        self.width = width  # Width of the link in meters
        self.thickness = thickness  # Thickness of the link in meters
        self.material = material.lower()  # Material: "steel" or "aluminum"
        self.length = length
        self.angleRad = angleRad
        self.weight = None  # Will be calculated in calcLinkVals
        self.graphic = RigidLink(0, 0, 1, 1)
        self.graphic.name = name

    def calculate_weight(self, node1, node2):
        """
        Calculate the weight of the link based on its dimensions and material.
        Density of steel: 7850 kg/m^3, aluminum: 2700 kg/m^3.
        Weight = volume * density, where volume = width * thickness * length.
        Convert length from feet to meters (1 ft = 0.3048 m).
        """
        if self.length is None:
            r = node2.position - node1.position
            self.length = r.mag()
        length_meters = self.length * 0.3048  # Convert feet to meters
        density = 7850 if self.material == "steel" else 2700
        volume = self.width * self.thickness * length_meters  # in m^3
        self.weight = volume * density  # in kg
        return self.weight

    def __eq__(self, other):
        """
        This overloads the == operator for comparing equivalence of two links.
        """
        if self.node1_Name != other.node1_Name: return False
        if self.node2_Name != other.node2_Name: return False
        if self.length != other.length: return False
        if self.angleRad != other.angleRad: return False
        return True

    def set(self, node1=None, node2=None, width=None, thickness=None, material=None, length=None, angleRad=None):
        self.node1_Name = node1
        self.node2_Name = node2
        self.width = width if width is not None else self.width
        self.thickness = thickness if thickness is not None else self.thickness
        self.material = material.lower() if material is not None else self.material
        self.length = length
        self.angleRad = angleRad

class TrussModel():
    def __init__(self):
        self.title = None
        self.links = []
        self.nodes = []
        self.material = Material()
        self.rct = Rectangle()

    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n

    def getCenterPt(self):
        """
        Sets the rectangle that encloses the truss nodes.
        """
        rct = Rectangle()
        rct.left = self.nodes[0].position.x
        rct.right = self.nodes[0].position.x
        rct.top = self.nodes[0].position.y
        rct.bottom = self.nodes[0].position.y
        for n in self.nodes:
            if rct.left > n.position.x:
                rct.left = n.position.x
            if rct.right < n.position.x:
                rct.right = n.position.x
            if rct.top < n.position.y:
                rct.top = n.position.y
            if rct.bottom > n.position.y:
                rct.bottom = n.position.y
        self.rct = rct

    def calculate_node_load(self, node):
        """
        Calculate the vertical load at a support node due to the truss weight.
        Assume the total weight is split evenly between the 'left' and 'right' nodes.
        """
        total_weight = sum(link.weight for link in self.links if link.weight is not None)
        support_nodes = [n for n in self.nodes if n.name.lower() in {'left', 'right'}]
        if node in support_nodes and len(support_nodes) > 0:
            return total_weight / len(support_nodes)  # Split evenly
        return 0

class TrussView():
    def __init__(self):
        # Setup widgets for display
        self.scene = qtw.QGraphicsScene()
        self.le_LongLinkName = qtw.QLineEdit()
        self.le_LongLinkNode1 = qtw.QLineEdit()
        self.le_LongLinkNode2 = qtw.QLineEdit()
        self.le_LongLinkLength = qtw.QLineEdit()
        self.te_Report = qtw.QTextEdit()
        self.gv = qtw.QGraphicsView()

        # region setup pens and brushes and scene
        # Make the pens first
        self.penLink = qtg.QPen(qtg.QColor("orange"))
        self.penLink.setWidth(1)
        self.penNode = qtg.QPen(qtc.Qt.darkBlue)
        self.penNode.setStyle(qtc.Qt.SolidLine)
        self.penNode.setWidth(1)
        self.penLabel = qtg.QPen(qtc.Qt.darkMagenta)
        self.penLabel.setStyle(qtc.Qt.SolidLine)
        self.penLabel.setWidth(1)
        self.penGridLines = qtg.QPen()
        self.penGridLines.setWidth(1)
        self.penGridLines.setColor(qtg.QColor.fromHsv(197, 144, 228, alpha=50))
        # Now make some brushes
        self.brushLink = qtg.QBrush(qtg.QColor.fromHsv(35, 255, 255, 64))
        self.brushPivot = qtg.QBrush(qtg.QColor.fromRgb(215, 215, 215, alpha=128))
        self.brushFill = qtg.QBrush(qtc.Qt.darkRed)
        self.brushNode = qtg.QBrush(qtg.QColor.fromCmyk(0, 0, 255, 0, alpha=100))
        self.brushGrid = qtg.QBrush(qtg.QColor.fromHsv(87, 98, 245, alpha=128))
        # Brush for roller joint
        self.brushRoller = qtg.QBrush(qtg.QColor("red"))
        # endregion

    def setDisplayWidgets(self, args):
        self.te_Report = args[0]
        self.le_LongLinkName = args[1]
        self.le_LongLinkNode1 = args[2]
        self.le_LongLinkNode2 = args[3]
        self.le_LongLinkLength = args[4]
        self.gv = args[5]
        self.gv.setScene(self.scene)

    def displayReport(self, truss=None):
        st = '\tTruss Design Report\n'
        st += 'Title:  {}\n'.format(truss.title)
        st += 'Static Factor of Safety:  {:0.2f}\n'.format(truss.material.staticFactor)
        st += 'Ultimate Strength:  {:0.2f}\n'.format(truss.material.uts)
        st += 'Yield Strength:  {:0.2f}\n'.format(truss.material.ys)
        st += 'Modulus of Elasticity:  {:0.2f}\n'.format(truss.material.E)
        st += '_____________Link Summary________________\n'
        st += 'Link\t(1)\t(2)\tLength\tAngle\tWeight (kg)\n'
        longest = None
        for l in truss.links:
            if longest is None or l.length > longest.length:
                longest = l
            st += '{}\t{}\t{}\t{:0.2f}\t{:0.2f}\t{:0.2f}\n'.format(
                l.name, l.node1_Name, l.node2_Name, l.length, l.angleRad, l.weight if l.weight is not None else 0)
        self.te_Report.setText(st)
        self.le_LongLinkName.setText(longest.name)
        self.le_LongLinkLength.setText("{:0.2f}".format(longest.length))
        self.le_LongLinkNode1.setText(longest.node1_Name)
        self.le_LongLinkNode2.setText(longest.node2_Name)

    def buildScene(self, truss=None):
        """
        Build the scene by centering a grid and drawing the truss links and nodes.
        """
        truss.getCenterPt()
        rct = truss.rct
        rct.left -= 50
        rct.right += 50
        rct.top += 50
        rct.bottom -= 50

        self.scene.clear()
        self.drawAGrid(DeltaX=10, DeltaY=10, Height=abs(rct.height()), Width=abs(rct.width()), CenterX=0, CenterY=0)
        self.drawLinks(truss=truss)
        self.drawNodes(truss=truss)

    def drawAGrid(self, DeltaX=10, DeltaY=10, Height=320, Width=180, CenterX=120, CenterY=60):
        """
        Draw a reference grid.
        """
        Pen = self.penGridLines
        Brush = self.brushGrid
        height = self.scene.sceneRect().height() if Height is None else Height
        width = self.scene.sceneRect().width() if Width is None else Width
        left = self.scene.sceneRect().left() if CenterX is None else (CenterX - width / 2.0)
        right = self.scene.sceneRect().right() if CenterX is None else (CenterX + width / 2.0)
        top = -1.0 * self.scene.sceneRect().top() if CenterY is None else (CenterY - height / 2.0)
        bottom = -1.0 * self.scene.sceneRect().bottom() if CenterY is None else (CenterY + height / 2.0)
        Dx = DeltaX
        Dy = DeltaY
        pen = qtg.QPen() if Pen is None else Pen

        if Brush is not None:
            rect = qtw.QGraphicsRectItem(left, top, width, height)
            rect.setBrush(Brush)
            rect.setPen(pen)
            self.scene.addItem(rect)
        x = left
        while x <= right:
            lVert = qtw.QGraphicsLineItem(x, top, x, bottom)
            lVert.setPen(pen)
            self.scene.addItem(lVert)
            x += Dx
        y = bottom
        while y >= top:
            lHor = qtw.QGraphicsLineItem(left, y, right, y)
            lHor.setPen(pen)
            self.scene.addItem(lHor)
            y -= Dy

    def drawLinks(self, truss=None):
        """
        Draw the truss links with updated tooltips.
        """
        scene = self.scene
        truss.getCenterPt()
        rct = truss.rct
        offset = Position(x=rct.centerX(), y=rct.centerY())

        penLink = self.penLink
        for l in truss.links:
            n1 = truss.getNode(l.node1_Name)
            n2 = truss.getNode(l.node2_Name)
            l.graphic = RigidLink(n1.position.x - offset.x, -(n1.position.y - offset.y),
                                 n2.position.x - offset.x, -(n2.position.y - offset.y),
                                 radius=3, pen=self.penLink, brush=self.brushLink, name="link name = "+l.name)
            # Build a detailed tooltip string
            st = f'Link: {l.name}\n'
            st += f'Nodes: {l.node1_Name}-{l.node2_Name}\n'
            st += f'Length: {l.length:.2f} m\n'
            st += f'Width: {l.width:.2f} m\n'
            st += f'Thickness: {l.thickness:.2f} m\n'
            st += f'Material: {l.material}\n'
            st += f'Weight: {l.weight:.2f} kg' if l.weight is not None else 'Weight: N/A'
            l.graphic.setToolTip(st)
            scene.addItem(l.graphic)

    def drawNodes(self, truss=None):
        """
        Draw the truss nodes, distinguishing between pin and roller joints.
        """
        truss.getCenterPt()
        rct = truss.rct
        offset = Position(x=rct.centerX(), y=rct.centerY())
        for n in truss.nodes:
            x = n.position.x - offset.x
            y = (n.position.y - offset.y)
            # Build tooltip with load information for support nodes
            joint_type = "Roller" if n.is_roller else "Pin"
            toolTip = f"Node: {n.name}\nJoint: {joint_type}"
            if n.name.lower() in {'left', 'right'}:
                load = truss.calculate_node_load(n)
                toolTip += f"\nVertical Load: {load:.2f} kg"
            if n.name.lower() in {'left', 'right'}:
                # Draw roller for 'right' node, pin for 'left'
                brush = self.brushRoller if n.is_roller else self.brushPivot
                n.graphic = RigidPivotPoint(x, -y, 10, 18, brush=brush, name=n.name, is_roller=n.is_roller)
                n.graphic.setToolTip(toolTip)
                self.scene.addItem(n.graphic)
            self.drawALabel(x=x - 5, y=y + 15, str=n.name, pen=self.penLabel)

    def drawALabel(self, x, y, str='', pen=None, brush=None, tip=None):
        scene = self.scene
        lbl = qtw.QGraphicsTextItem(str)
        w = lbl.boundingRect().width()
        h = lbl.boundingRect().height()
        lbl.setX(x - w / 2.0)
        lbl.setY(-y - h / 2.0)
        if tip is not None:
            lbl.setToolTip(tip)
        if pen is not None:
            lbl.setDefaultTextColor(pen.color())
        if brush is not None:
            bkg = qtw.QGraphicsRectItem(lbl.x(), lbl.y(), w, h)
            bkg.setBrush(brush)
            outlinePen = qtg.QPen(brush.color())
            bkg.setPen(outlinePen)
            scene.addItem(bkg)
        scene.addItem(lbl)

    def drawACircle(self, centerX, centerY, Radius, angle=0, brush=None, pen=None, name=None, tooltip=None):
        scene = self.scene
        ellipse = qtw.QGraphicsEllipseItem(centerX - Radius, -1.0 * (centerY + Radius), 2 * Radius, 2 * Radius)
        if pen is not None:
            ellipse.setPen(pen)
        if brush is not None:
            ellipse.setBrush(brush)
        if name is not None:
            ellipse.setData(0, name)
        if tooltip is not None:
            ellipse.setToolTip(tooltip)
        scene.addItem(ellipse)

class TrussController():
    def __init__(self):
        self.truss = TrussModel()
        self.view = TrussView()

    def ImportFromFile(self, data):
        """
        Parse the input file to build the truss, including new link attributes.
        """
        self.truss = TrussModel()
        for L in data:
            L = L.strip()
            if L.find('#') == 0:
                pass  # Comment
            else:
                Cells = L.split(',')
                if len(Cells) <= 1:
                    pass  # No data
                elif Cells[0].lower().find('material') >= 0:
                    sut = float(Cells[1].strip())
                    sy = float(Cells[2].strip())
                    E = float(Cells[3].strip())
                    self.truss.material = Material(uts=sut, ys=sy, modulus=E)
                elif Cells[0].lower().find('static') >= 0:
                    sf = float(Cells[1].strip())
                    self.truss.material.staticFactor = sf
                elif Cells[0].lower().find('node') >= 0:
                    name = Cells[1].strip()
                    x = float(Cells[2].strip())
                    y = float(Cells[3].strip())
                    # Set 'right' node as roller
                    is_roller = (name.lower() == 'right')
                    self.truss.nodes.append(Node(name=name, position=Position(x=x, y=y), is_roller=is_roller))
                elif Cells[0].lower().find('link') >= 0:
                    name = Cells[1].strip()
                    n1 = Cells[2].strip()
                    n2 = Cells[3].strip()
                    # Read new attributes: width, thickness, material
                    width = float(Cells[4].strip()) if len(Cells) > 4 else 0.1
                    thickness = float(Cells[5].strip()) if len(Cells) > 5 else 0.05
                    material = Cells[6].strip().lower() if len(Cells) > 6 else "steel"
                    self.truss.links.append(Link(name=name, node1=n1, node2=n2, width=width, thickness=thickness, material=material))
        self.calcLinkVals()
        self.displayReport()
        self.drawTruss()

    def hasNode(self, name):
        for n in self.truss.nodes:
            if n.name == name:
                return True
        return False

    def addNode(self, node):
        self.truss.nodes.append(node)

    def getNode(self, name):
        for n in self.truss.nodes:
            if n.name == name:
                return n

    def addLink(self, link):
        self.truss.links.append(link)

    def calcLinkVals(self):
        for l in self.truss.links:
            n1 = None
            n2 = None
            if self.hasNode(l.node1_Name):
                n1 = self.getNode(l.node1_Name)
            if self.hasNode(l.node2_Name):
                n2 = self.getNode(l.node2_Name)
            if n1 is not None and n2 is not None:
                r = n2.position - n1.position
                l.length = r.mag()
                l.angleRad = r.getAngleRad()
                l.calculate_weight(n1, n2)  # Calculate weight

    def setDisplayWidgets(self, args):
        self.view.setDisplayWidgets(args)

    def displayReport(self):
        self.view.displayReport(truss=self.truss)

    def drawTruss(self):
        self.view.buildScene(truss=self.truss)

    # Methods to fix MVC violations
    def install_event_filter(self, widget):
        """
        Install an event filter on the view's scene.
        """
        self.view.scene.installEventFilter(widget)

    def get_scene(self):
        """
        Return the view's scene for event filtering.
        """
        return self.view.scene

    def handle_mouse_move(self, scenePos, transform):
        """
        Handle mouse move events to update the mouse position label.
        """
        strScene = f"Mouse Position: x = {round(scenePos.x(), 2)}, y = {round(-scenePos.y(), 2)}"
        s = self.view.scene.itemAt(scenePos, transform)  # Get item under the mouse
        if s is not None and s.data(0) is not None:
            strScene += f' ({s.data(0)})'
        items = self.view.scene.items(scenePos)
        item_names = [item.name if hasattr(item, 'name') else None for item in items]
        for i in item_names:
            strScene += ', ' + (i if i is not None else 'none')
        return strScene

#endregion