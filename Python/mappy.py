import eventBasedAnimation

import math
import random
import string
import copy
import os

from Tkinter import *
import tkMessageBox
import tkSimpleDialog
import tkFileDialog

import json

import webcolors

version = '1.0'


def rgbString(red, green, blue): # from the class notes
    return "#%02x%02x%02x" % (red, green, blue)


def darkenRGB((r, g, b), factor):
    '''Darkens a given RGB color value by a factor between 0 and 1'''
    maxColor = 255
    r *= 1-factor
    g *= 1-factor
    b *= 1-factor
    r, g, b = int(round(r)), int(round(g)), int(round(b))
    return (r, g, b)

def lightenRGB((r, g, b), factor):
    '''Lightens a given RGB color value by a factor between 0 and 1'''
    maxColor = 255
    # lighten by inverting, darkening, and inverting again
    r, g, b = 255 - r, 255 - g, 255 - b
    r, g, b = darkenRGB((r, g, b), factor)
    r, g, b = 255 - r, 255 - g, 255 - b
    r, g, b = int(round(r)), int(round(g)), int(round(b))
    return (r, g, b)

def isDark((r, g, b)):
    '''Returns 1 is a color is dark, and 0 if it is light'''
    maxColor = 255
    avg = 1.0*(r+g+b)/3
    return True if avg <= maxColor/2 else False

def choose(title, message, options): # taken from class notes, with edits
    msg = message + "\n" + "Choose one:"
    for i in xrange(len(options)):
        msg += "\n" + str(i+1) + ": " + options[i]
    response = tkSimpleDialog.askinteger(title, msg)
    # clicked cancel
    if response == None:
        return
    # checks to see if they input a number in the right range
    if response - 1 in xrange(len(options)):
        response = response - 1
        return options[response]
    else:
        tkMessageBox.showwarning("Error!", "Please enter a valid choice")
        return
    
def textSize(canvas, text, font): # taken from the class notes!
    temp = canvas.create_text(0, 0, text=text, anchor=NW, font=font)
    (x0, y0, x1, y1) = canvas.bbox(temp)
    canvas.delete(temp)
    return (x1-x0, y1-y0)

class Node(object):
    def __init__(self, x, y, m, name, color="white", textColor="black"):
        self.x = x
        self.y = y
        self.m = m
        self.name = name
        self.color = color
        self.textColor = textColor
        self.darkenFactor = 0.2
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        

    def __repr__(self):
        return "Node %s at (%f, %f) with size %d" % \
                (self.name, self.x, self.y, self.m)

    def __eq__(self, other):
        return type(other) == Node and self.name == other.name

    def inNode(self, x, y, sizeScaleFactor):
        dx = self.x - x
        dy = self.y - y
        return (dx**2 + dy**2) ** 0.5 < math.sqrt(self.m) * sizeScaleFactor

    def doPhysics(self): # code from Adriel Luo & co's Graff program
        aLimit = 5
        self.ax = max(min(self.ax, aLimit), -aLimit)
        self.ay = max(min(self.ay, aLimit), -aLimit)

        self.vx += self.ax
        self.vy += self.ay
        self.vx *= 0.7
        self.vy *= 0.7

        self.x += self.vx
        self.y += self.vy

    # adjustment factors to account for controls/options boxes
    def draw(self, canvas, sizeScaleFactor, xAdjust, yAdjust):
        r = self.m**0.5 * sizeScaleFactor
        x, y = self.x + xAdjust, self.y + yAdjust
        # if the color is in hex form, keep it
        # otherwise, convert from name to hex
        color = self.color if self.color[0] == '#' else \
                webcolors.name_to_hex(self.color)
        colorIsDark = isDark(webcolors.hex_to_rgb(color)) 
        if colorIsDark:
            active=webcolors.rgb_to_hex(lightenRGB(webcolors.hex_to_rgb(color),
                                              self.darkenFactor))
        else:
            active=webcolors.rgb_to_hex(darkenRGB(webcolors.hex_to_rgb(color),
                                              self.darkenFactor))
        canvas.create_oval(x-r, y-r, x+r, y+r, 
                           fill=self.color, activefill=active)
        canvas.create_text(x, y, text=self.name, font='Arial 13 bold', 
                           fill=self.textColor, state=DISABLED)




class Edge(object):
    def __init__(self, frm, to, width=1):
        self.frm = frm
        self.to = to
        self.width = width

    def __repr__(self):
        return "Edge from %s to %s, width %d" % \
                (repr(self.frm), repr(self.to), self.width)

    def addWidth(self):
        self.width += 1 

    def draw(self, canvas, xAdjust, yAdjust):
        frmx, frmy = self.frm.x + xAdjust, self.frm.y + yAdjust
        tox, toy = self.to.x + xAdjust, self.to.y + yAdjust
        canvas.create_line(frmx, frmy, tox, toy, 
                           fill="black", width=math.sqrt(self.width))


class Button(object):
    def __init__(self, x0, y0, width, height, name):
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.name = name
        self.fill = "light gray"
        self.activefill = "white"

    def __repr__(self):
        return "Button %s at (%d, %d) of dim %d x %d" % \
                (self.name, self.x0, self.y0, self.width, self.height)

    def inButton(self, x, y):
        inX = x >= self.x0 and x <= self.x0+self.width
        inY = y >= self.y0 and y <= self.y0+self.height
        return inX and inY

    def draw(self, canvas):
        canvas.create_rectangle(self.x0, self.y0, self.x0+self.width, 
                                self.y0+self.height, fill=self.fill, 
                                activefill=self.activefill)
        canvas.create_text(self.x0+self.width/2, self.y0+self.height/2, 
                           anchor=CENTER, text=self.name, state=DISABLED)

class CircleButton(object):
    def __init__(self, x0, y0, r, name):
        self.x0 = x0
        self.y0 = y0
        self.r = r
        self.name = name
        self.fill = "orange red"
        self.activefill = "tomato"

    def __repr__(self):
        return "Circular Button %s at (%d, %d) with radius %d" % \
                (self.name, self.x0, self.y0, self.r)

    def inButton(self, x, y):
        dx = x - self.x0
        dy = y - self.y0
        return math.sqrt(dx**2 + dy**2) <= self.r

    def draw(self, canvas):
        canvas.create_oval(self.x0-self.r, self.y0-self.r, self.x0+self.r, 
                           self.y0+self.r, fill=self.fill, 
                           activefill=self.activefill)
        canvas.create_text(self.x0, self.y0, text=self.name, state=DISABLED, 
                           font='Arial 10 bold')


class Mappy(eventBasedAnimation.Animation):
    
    def setConstants(self):
        self.repulsionConstant = 1000000.0
        self.nodeRepulsionConstant = 200000.0
        self.hookesLawK = 0.025
        self.nodeRepulsionScaleFactor = 100
        self.HookesLawScaleFactor = 100
        self.findSizeScaleFactor()

    # initialize all the buttons
    def createButtons(self):
        margin, buttonHeight, buttonWidth, buttonR = 10, 25, 150, 28

        shakeItUpButton = Button(self.width-margin*2-buttonWidth,
                                 self.height - margin*2 - buttonHeight, 
                                 buttonWidth, buttonHeight, "Shake It Up!")
        addNodeButton = Button(margin, self.height - margin*4 - buttonHeight*4, 
                               buttonWidth, buttonHeight, "Add Node")
        addEdgeByNameButton = Button(margin,self.height-margin*3-buttonHeight*3,
                                buttonWidth, buttonHeight, "Add Edge By Name")
        editEdgeButton = Button(margin, self.height - margin*2 - buttonHeight*2,
                                buttonWidth, buttonHeight, "Edit Edge") 
        deleteEdgeButton = Button(margin, self.height - margin - buttonHeight,
                                  buttonWidth, buttonHeight, "Delete Edge")
        exportDataButton = Button(margin, self.controlsHeight-margin*3,
                            buttonWidth,buttonHeight, "Export Data to file...")
        importDataButton = Button(margin*2 + buttonWidth, self.controlsHeight-\
                margin*3,buttonWidth,buttonHeight,"Import Data from file...")
        clearDataButton = Button(margin*3 + buttonWidth*2, self.controlsHeight-\
                            margin*3, buttonWidth, buttonHeight, "Clear Data")

        aboutButton = CircleButton(self.width-margin*5,margin*5,buttonR,"about")
        helpButton = CircleButton(self.width-margin*12,margin*5,buttonR,"help")
        settingsButton = CircleButton(self.width - margin*19, margin*5, 
                                      buttonR, "settings")


        return [shakeItUpButton, addNodeButton, addEdgeByNameButton, 
                editEdgeButton, deleteEdgeButton, exportDataButton, 
                clearDataButton,importDataButton, helpButton, settingsButton, 
                aboutButton]

    def getHelpAndAboutText(self):
        helpTextFile = "helpText.txt"
        with open(helpTextFile, "rt") as infile:
            self.helpText = infile.read()
        aboutTextFile = "aboutText.txt"
        with open(aboutTextFile, "rt") as infile:
            self.aboutText = infile.read()

    def onInit(self):
        # set the dimensions of each section of the UI
        self.graphWidth, self.graphHeight = 1000, 700
        self.controlsWidth, self.controlsHeight = 1200, 100
        self.dataBoxWidth, self.dataBoxHeight = 200, 700
        self.contextWidth, self.contextHeight = 150, 20

        self.bgColor = "white"

        self.windowTitle = "Mappy"

        self.getHelpAndAboutText()
        self.nodes, self.edges = [], []
        self.buttons = self.createButtons()
        self.setConstants()
        self.pauseAnimation = False
        self.selected = None
        self.contextMenuItems = []
        self.contextMenuLocation = (0,0)
        self.contextNode = None
        self.addingEdge = False
        self.addingEdgeNode = None

        self.data = []

        # demo objects
        '''self.nodes.append(Node(50,50, 10, 'hithere'))
        self.nodes.append(Node(200,200, 20, '2'))
        self.nodes.append(Node(400,400, 30, '3'))
        self.nodes.append(Node(400,200, 100, '#acfupward'))
        self.edges.append(Edge(self.nodes[0], self.nodes[1]))
        self.edges.append(Edge(self.nodes[0], self.nodes[3]))'''


    # Takes a node and returns a list of tuples of all nodes it is 
    # linked to and the edge linking them
    def getLinkedNodes(self, node): 
        linked = [ ]
        for edge in self.edges:
            if edge.frm == node:
                linked.append((edge.to, edge))
            elif edge.to == node:
                linked.append((edge.frm, edge))
        return linked

    def getAreaCovered(self):
        totalArea = 0
        for node in self.nodes:
            totalArea += math.pi * (node.m**0.5)**2
        return totalArea

    # finds scaling factor so that the nodes cover 1% of the screen
    def findSizeScaleFactor(self):
        ratio = 1.0 * self.getAreaCovered() / (self.graphWidth*self.graphHeight)
        size = 0.01
        self.sizeScaleFactor = (size / ratio) ** 0.5 if ratio != 0 else 1

    def getTotalSize(self):
        totalSize = 0
        for node in self.nodes:
            totalSize += node.m
        return totalSize

    # finds a scaling factor for wall repulsions as total size increases
    def findRepulsionScaleFactor(self):
        totalSize = self.getTotalSize()
        self.repulsionScaleFactor = 1.0*totalSize / 100


    def processPhysics(self):
        """Calculates the forces acting on each node.

        The code for processPhysics and its helper functions is based heavily 
        off the process physics code for Graff by Adriel Luo, Diao Zheng, and 
        Lee Yang Bryan, with adjustments made to allow for variable node size 
        and edge thickness.
        """

        # calculates the effects of repulsion from the walls
        def wallRepulsions(self, node):
            node.ax += (node.x/abs(node.x)*(self.repulsionConstant/(node.x)**2 \
                      + (node.x - self.graphWidth)/abs(node.x-self.graphWidth) \
                      * self.repulsionConstant/(node.x - self.graphWidth)**2)) \
                      * self.repulsionScaleFactor
            
            node.ay += (node.y/abs(node.y)*(self.repulsionConstant/(node.y)**2 \
                      + (node.y-self.graphHeight)/abs(node.y-self.graphHeight) \
                      * self.repulsionConstant/(node.y - self.graphHeight)**2))\
                      * self.repulsionScaleFactor


        # calculates the effects of repulsion from other nodes
        def otherNodeRepulsions(self, node, i):
            otherNodes = self.nodes[:i] + self.nodes[i+1:]
            for otherNode in otherNodes:

                dx = node.x - otherNode.x
                dy = node.y - otherNode.y
                magnitude = ((dx)**2 + (dy)**2) / \
                        (1.0*node.m*otherNode.m/self.nodeRepulsionScaleFactor)
                theta = math.atan2(dy,dx)

                if magnitude == 0:
                    magnitude = random.uniform(0,10)
                    theta = random.uniform(0,10)
                node.ax +=self.nodeRepulsionConstant/(magnitude)*math.cos(theta)
                node.ay +=self.nodeRepulsionConstant/(magnitude)*math.sin(theta)


        # calculates the effects of tensions from links on the node
        def edgeTensions(self, node):
            linkedNodes = self.getLinkedNodes(node)
            for (linkedNode, edge) in linkedNodes:
                dx = node.x - linkedNode.x
                dy = node.y - linkedNode.y
                magnitude = ((dx)**2 + (dy)**2) ** 0.5 \
                           * (1.0*node.m*linkedNode.m*math.sqrt(edge.width)\
                           / self.HookesLawScaleFactor)
                theta = math.atan2(dy, dx)
                node.ax -= self.hookesLawK * (magnitude) * math.cos(theta)
                node.ay -= self.hookesLawK * (magnitude) * math.sin(theta)
                linkedNode.ax += self.hookesLawK * (magnitude) * math.cos(theta)
                linkedNode.ay += self.hookesLawK * (magnitude) * math.sin(theta)


        for i in xrange(len(self.nodes)):
            node = self.nodes[i]

            # Set electron's ax and ay
            # Wall's repulsions
            wallRepulsions(self, node)

            # Other nodes' repulsions
            otherNodeRepulsions(self, node, i)

            # Take into account edge tensions
            edgeTensions(self, node)

        for node in self.nodes:
            node.doPhysics()

    def onStep(self):
        # remove any edges if they're not actually connected to anything
        for edge in self.edges:
            if edge.frm not in self.nodes or edge.to not in self.nodes:
                self.deleteEdge(edge)

        self.findSizeScaleFactor()
        self.findRepulsionScaleFactor()
        #self.nodeRepulsionScaleFactor = 
        #self.HookesLawScaleFactor = 


        # Reset all accelerations
        for node in self.nodes:
            node.ax = 0
            node.ay = 0        

        # Process physics if we're not dragging any nodes
        if self.selected == None:
            self.processPhysics()

    # obtains a color from user input
    def getColor(self, item):
        encodeMethod = choose(item + " color","Choose an encoding method",
                              ['name', 'RGB', 'hex'])
        if encodeMethod == 'RGB':
            r = tkSimpleDialog.askinteger("Red", 
                                        "Input a red value from 0 to 255")
            g = tkSimpleDialog.askinteger("Green",
                                        "Input a green value from 0 to 255")
            b = tkSimpleDialog.askinteger("Blue",
                                        "Input a blue value from 0 to 255")
            if r>255 or r<0 or g>255 or g<0 or b>255 or b<0:
                tkMessageBox.showwarning("Error!", 
                                         "Please enter a valid color!")
                return
            return rgbString(r, g, b)
        else:
            color = tkSimpleDialog.askstring("Color", "Input your color")
            return color


    # returns the node with the matching name, or None if it doesn't exist            
    def findNode(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    # gets a user-inputted pair of nodes
    def findTwoNodesFromUser(self):
        frmString = tkSimpleDialog.askstring("Node 1",
                                    "Please enter the name of the first node")
        if frmString == None: # they pressed cancel
            return        
        frm = self.findNode(frmString)
        if frm == None:
            tkMessageBox.showwarning("Error!","There's no node with that name!")
            return

        toString = tkSimpleDialog.askstring("Node 2", 
                                    "Please enter the name of the second node")
        if frmString == None: # they pressed cancel
            return        
        elif frmString == toString:
            tkMessageBox.showwarning("Error!", 
                                     "Please enter two distinct names!")
        to = self.findNode(toString)
        if to == None:
            tkMessageBox.showwarning("Error!","There's no node with that name!")
            return

        return (frm, to)


    def addNodeButtonPressed(self):
        name = tkSimpleDialog.askstring("Add node","Please enter the node name")
        size = tkSimpleDialog.askinteger("Add node","Please enter the node size")
        #color = self.getColor("Node")
        #textColor = self.getColor("Text")
        if name == '' or name == None or size == None: return
        #self.addNode(size, name, color, textColor)
        self.addNode(size, name)

    def addNode(self, m, name, color="white", textColor="black"):
        if self.findNode(name) != None:
            tkMessageBox.showwarning("Error!", 
                                     "There's already a node with that name!")
            return
        x = self.graphWidth/2 + self.dataBoxWidth
        y = self.graphHeight/2 + self.controlsHeight
        self.nodes.append(Node(x, y, m, name, color, textColor))

    def deleteNode(self, node):
        confirm = tkMessageBox.askyesno("Confirm", 
                                "Are you sure you want to delete this node?")
        if confirm:
            self.nodes.pop(self.nodes.index(node))

    def editNodeName(self, node):
        name = tkSimpleDialog.askstring("Name", "Please enter a new name")
        if name == '' or name == None:
            return
        node.name = name

    def editNodeSize(self, node):
        size = tkSimpleDialog.askinteger("Size", "Please enter a new size")
        if size > 0:
            node.m = size
        else:
            tkMessageBox.showwarning("Error", 
                                     "Please enter a positive integer!")

    def editNodeColor(self, node):
        color = self.getColor("Node")
        if color != None: node.color = color

    def editNodeTextColor(self, node):
        color = self.getColor("Text")
        if color != None: node.textColor = color


    def editNode(self, node):
        options = ["Name", "Size", "Color", "Text Color"]
        title = "Choose One"
        msg = "Which attribute would you like to edit?"
        item = choose(title, msg, options)
        if item == "Name":
            self.editNodeName(node)
        elif item == "Size":
            self.editNodeSize(node)
        elif item == "Color":
            self.editNodeColor(node)
        elif item == "Text Color":
            self.editNodeTextColor(node)
        else:
            return

    def addEdgeByNameButtonPressed(self):
        findNodes = self.findTwoNodesFromUser()
        if findNodes == None:
            return
        else:
            frm, to = findNodes[0], findNodes[1]
            self.addEdge(frm, to)

    def addEdgeToNodeByName(self, node):
        response = tkSimpleDialog.askstring("Add Edge", 
                        "Please enter the node you would like to connect to")
        if response == None: # pressed cancel
            return
        other = self.findNode(response)
        if other != None:
            if self.findEdge(node, other):
                tkMessageBox.showwarning("Error!", 
                                "There already is an edge between those nodes!")
                return
            else:
                self.addEdge(node, other)
        else:
            tkMessageBox.showwarning("Error!", "Please enter a valid node!")
        return

    def addEdgeToNode(self, node):
        self.addingEdge = True
        self.addingEdgeNode = node


    def addEdge(self, frm, to):
        for edge in self.edges:
            if (edge.frm == frm and edge.to == to) or \
               (edge.to == frm and edge.frm == to):
                tkMessageBox.showwarning("Error!",
                    "There's already an edge connecting those!")
                return
        self.edges.append(Edge(frm, to))

    def findEdge(self, frm, to):
        for edge in self.edges:
            if ((edge.frm == frm and edge.to == to) or 
                (edge.frm == to and edge.to == frm)):
                return edge
        return None

    def editEdgeButtonPressed(self):
        findNodes = self.findTwoNodesFromUser()
        if findNodes == None:
            return
        else:
            frm, to = findNodes[0], findNodes[1]
        edge = self.findEdge(frm, to)
        if edge == None:
            tkMessageBox.showwarning("Error!", 
                                     "There isn't an edge between those nodes!")
            return
        newWidth = tkSimpleDialog.askinteger("New Width", 
                                        "Please enter the desired edge width") 
        if newWidth == None:
            return
        elif newWidth > 0:
            edge.width = newWidth
        else:
            tkMessageBox.showwarning("Error!", 
                             "Please enter a positive integer for the width")

    def deleteEdge(self, edge):
        self.edges.pop(self.edges.index(edge)) # deletes the edge


    def deleteEdgeButtonPressed(self):
        findNodes = self.findTwoNodesFromUser()
        if findNodes == None:
            return
        else:
            frm, to = findNodes[0], findNodes[1]
        edge = self.findEdge(frm, to)
        if edge == None:
            tkMessageBox.showwarning("Error!", 
                                     "There isn't an edge between those nodes!")
            return
        else:
            self.deleteEdge(edge)

    def deleteEdgeFromNode(self, node):
        response = tkSimpleDialog.askstring("Delete Edge", 
                    "Which node would you like to delete the connection to?")
        if response == None: # pressed cancel
            return
        other = self.findNode(response)
        if other != None:
            edge = self.findEdge(node, other)
            if edge != None:
                self.deleteEdge(edge)
            else:
                tkMessageBox.showwarning("Error!", 
                                        "There isn't an edge between those two")
        else:
            tkMessageBox.showwarning("Error!", "Please enter a valid node")
        return

    def clearData(self):
        confirm = tkMessageBox.askyesno("Confirm", 
            "Are you sure you wish to reset all data?\nIt is recommended that \
you save your data first.")
        if confirm:
            self.nodes = []
            self.edge = []

    def showHelp(self):
        
        tkMessageBox.showinfo("Help", self.helpText)

    def showAbout(self):
        tkMessageBox.showinfo("About", self.aboutText)

    def showSettings(self):
        title = "Settings"
        msg = "Please choose a setting to adjust"
        options = ["Background Color", "Node Color", "Node Text Color"]
        setting = choose(title, msg, options)
        if setting == "Background Color":
            newColor = self.getColor("Background")
            self.bgColor = newColor
        elif setting == "Node Color":
            newColor = self.getColor("Node")
            for node in self.nodes:
                node.color = newColor
        elif setting == "Node Text Color":
            newColor = self.getColor("Text")
            for node in self.nodes:
                node.textColor = newColor

    # returns the index of the item clicked, or False if we clicked outside
    def clickedInContextMenu(self, x, y):
        if x >= self.contextMenuCoords[0] and \
           x <= self.contextMenuCoords[0]+self.contextWidth and \
           y >= self.contextMenuCoords[1]:
            for i in xrange(len(self.contextMenuItems)):
                if y >= self.contextMenuCoords[1] + (i)*self.contextHeight and \
                   y <= self.contextMenuCoords[1] + (i+1)*self.contextHeight:
                    return i
        return False

    def contextMenuAction(self, action, node):
        if action == "Delete Node":
            self.deleteNode(node)
        if action == "Edit Node":
            self.editNode(node)
        if action == "Add Edge By Name":
            self.addEdgeToNodeByName(node)
        if action == "Add Edge":
            self.addEdgeToNode(node)
        if action == "Delete Edge":
            self.deleteEdgeFromNode(node)


    # sets random accelerations to shake up the graph
    # code from Graff program by Adriel Luo & co.
    def shakeItUp(self):
        for node in self.nodes:
            # Give random vx and vy to electron
            minV, maxV = -50, 50
            node.vx = random.uniform(minV, maxV)
            node.vy = random.uniform(minV, maxV)

    def onMouse(self, event):
        self.pauseAnimation = True
        x, y = event.x, event.y

        # if a context menu is open and an item is selected
        if len(self.contextMenuItems) != 0: 
            # if we clicked a context menu item
            item = self.clickedInContextMenu(x, y)
            if item != False or type(item) == int:
                self.contextMenuAction(self.contextMenuItems[item], 
                                       self.contextNode)
            self.contextMenuItems = []
            self.contextNode = None
            return

        if self.addingEdge == True:
            for node in reversed(self.nodes): # reversed to search back to front
                if node.inNode(x - self.dataBoxWidth, y - self.controlsHeight, 
                            self.sizeScaleFactor) and node!=self.addingEdgeNode:
                    self.addEdge(node, self.addingEdgeNode)
            self.addingEdge = False
            self.addingEdgeNode = None
            return

        # if we clicked on a node, select it
        for node in reversed(self.nodes): # reversed to search back to front
            if node.inNode(x - self.dataBoxWidth, y - self.controlsHeight, 
                           self.sizeScaleFactor):
                self.selected = node
                return
        # if a button is pressed
        for button in self.buttons:
            if button.inButton(x,y):
                self.clickButton(button.name)
                return

    # does the appropriate action when a button is clicked
    def clickButton(self, button):
        if button == "Shake It Up!":
            self.shakeItUp()
        elif button == "Add Node":
            self.addNodeButtonPressed()
        elif button == "Add Edge By Name":
            self.addEdgeByNameButtonPressed()
        elif button == "Edit Edge":
            self.editEdgeButtonPressed()
        elif button == "Delete Edge":
            self.deleteEdgeButtonPressed()
        elif button == "Export Data to file...":
            self.exportData()
        elif button == "Import Data from file...":
            self.importData()
        elif button == "Clear Data":
            self.clearData()
        elif button == "about":
            self.showAbout()
        elif button == "help":
            self.showHelp()
        elif button == "settings":
            self.showSettings()

    # returns the corresponding node if click is in  node list, False otherwise
    def inNodesList(self, x, y):
        margin = 10
        textHeight = 25
        for i in xrange(len(self.nodes)):
            x1 = 0
            x2 = self.dataBoxWidth
            y1 = self.controlsHeight + margin*2 + textHeight*(i+1)
            y2 = y1 + textHeight
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                return self.nodes[i]
        return False

    def onMouseMove(self, event):
        self.mouseX = event.x
        self.mouseY = event.y

    def onMouseDrag(self, event):
        # drag the node around if one is selected
        if type(self.selected) == Node:
            x, y = event.x - self.dataBoxWidth, event.y - self.controlsHeight
            self.selected.x, self.selected.y = x, y

    def onMouseRelease(self, event):
        self.pauseAnimation = False
        self.selected = None

    def onRightMouse(self, event):
        x, y = event.x, event.y
        self.contextMenuItems = []
        self.contextNode = None
        # creates the context menu if we clicked on a node
        for node in reversed(self.nodes): # detect from the top down
            if node.inNode(x - self.dataBoxWidth, y - self.controlsHeight, 
                           self.sizeScaleFactor):
                self.contextNode = node
                self.contextMenuCoords = x, y
                self.contextMenuItems += ["Delete Node", "Edit Node", 
                                          "Add Edge By Name", "Add Edge",
                                          "Delete Edge"]
                return
        nodeListItem = self.inNodesList(x, y)
        if nodeListItem != False:
            self.contextNode = nodeListItem
            self.contextMenuCoords = x, y
            self.contextMenuItems += ["Delete Node", "Edit Node", 
                                      "Add Edge", "Delete Edge"]


    def onKey(self, event):
        if event.keysym == 's': self.shakeItUp()
        if event.keysym == 'e': self.exportData()
        if event.keysym == 'i': self.importData()


    def saveData(self):
        '''Saves the current data in a form that is encodeable by JSON.

        Node data is saved as a list of nodes, with each node stored as the
        node's dictionary.
        Edge data is saved as a list of edges, with each edge stored as the name
        of the the "from" and "to" nodes as well as the edge width. 
        '''
        nodeData = [copy.deepcopy(node.__dict__) for node in self.nodes]
        edgeData = [copy.deepcopy(edge.__dict__) for edge in self.edges]
        # replaces the reference to the "to" and "from" nodes with the names
        for edge in edgeData:
            edge['to'] = edge['to'].name
            edge['frm'] = edge['frm'].name
        self.data = [nodeData, edgeData]

    def exportData(self):
        self.saveData()
        filename = tkFileDialog.asksaveasfilename()
        if filename == None or filename == '':
            return
        with open(filename, 'w') as outfile:
            json.dump(self.data, outfile)

    def unpackData(self):
        '''Rebuilds the node and edge lists from a given data set.'''
        nodeData = self.data[0]
        edgeData = self.data[1]
        self.nodes = []
        for node in nodeData:
            x = node['x']
            y = node['y']
            m = node['m']
            name = node['name']
            color = node['color']
            self.nodes.append(Node(x, y, m, name, color))
        self.edges = []
        for edge in edgeData:
            frm = self.findNode(edge['frm'])
            to = self.findNode(edge['to'])
            width = edge['width']
            self.edges.append(Edge(frm, to, width))


    def importData(self):
        filename = tkFileDialog.askopenfilename()
        if filename == None or filename == '':
            return
        # loads the data from the given file
        with open(filename, 'r') as infile:
            data = infile.read()
            try:
                self.data = json.loads(data)
            except:
                tkMessageBox.showwarning("Error!", "That is not a valid file!")
                return
        self.unpackData()



    def drawNodesAndEdges(self, canvas):
        for edge in self.edges:
            edge.draw(canvas, self.dataBoxWidth, self.controlsHeight)
        if self.addingEdge == True:
            canvas.create_line(self.addingEdgeNode.x + self.dataBoxWidth, self.addingEdgeNode.y + self.controlsHeight, self.mouseX, self.mouseY)
        for node in self.nodes:
            node.draw(canvas, self.sizeScaleFactor, self.dataBoxWidth, 
                      self.controlsHeight)

    def drawNodesList(self, canvas):
        margin = 10
        textHeight = 25
        textOffset = 4
        canvas.create_rectangle(0, self.controlsHeight, self.dataBoxWidth, 
                                self.controlsHeight+margin*2+textHeight, 
                                fill="gray")
        canvas.create_text(margin*2, self.controlsHeight+margin, anchor=NW, 
                           text="Current Nodes:",font="Arial 14 bold underline")
        for i in xrange(len(self.nodes)):
            y = self.controlsHeight + margin*3 + textHeight*(i+1)
            node = self.nodes[i]
            canvas.create_rectangle(margin, y, self.dataBoxWidth-margin, y+textHeight, 
                                    fill="light gray", activefill="white")
            canvas.create_text(margin*2, y+textOffset, anchor=NW, text=node.name, 
                                    font="Arial 13 bold", state=DISABLED)
        

    def drawButtons(self, canvas):
        for button in self.buttons:
            button.draw(canvas)

    def drawContextMenu(self, canvas, coords):
        fill = "seashell2"
        activefill = "blue"
        font = "Arial 12 bold"
        for i in xrange(len(self.contextMenuItems)):
            text = self.contextMenuItems[i]
            canvas.create_rectangle(coords[0], coords[1]+i*self.contextHeight, 
                coords[0]+self.contextWidth, coords[1]+(i+1)*self.contextHeight,
                fill=fill, activefill=activefill)
            canvas.create_text(coords[0], coords[1]+i*self.contextHeight, 
                               text=text, anchor=NW, font=font, state=DISABLED)

    def drawTitle(self, canvas):
        text = "Mappy Version %s" % version
        font = "Arial 20 bold"
        margin = 10
        boxWidth, boxHeight = textSize(canvas, text, font)
        x1, x2 = self.width/2 - boxWidth/2, self.width/2 + boxWidth/2
        canvas.create_rectangle(x1-margin, 0, x2+margin, margin*2+boxHeight,
                                fill="black")
        canvas.create_text(self.width/2, margin, text=text, anchor=N, 
                           font="Arial 20 bold", fill="white")

    def onDraw(self, canvas):
        # blue background for controls area
        canvas.create_rectangle(0, 0, self.controlsWidth, self.controlsHeight,
                                fill="blue")

        # royal blue background for data area
        canvas.create_rectangle(0, self.controlsHeight, self.dataBoxWidth, 
                                self.controlsHeight + self.dataBoxHeight, 
                                fill="royal blue")

        # background for graph area
        canvas.create_rectangle(self.dataBoxWidth, self.controlsHeight, 
                                self.dataBoxWidth + self.graphWidth, 
                                self.controlsHeight + self.graphHeight, 
                                fill=self.bgColor)
        self.drawTitle(canvas)
        self.drawNodesAndEdges(canvas)
        self.drawNodesList(canvas)
        self.drawButtons(canvas)
        if len(self.contextMenuItems) != 0:
            self.drawContextMenu(canvas, self.contextMenuCoords)

Mappy(width=1200, height=800, timerDelay=64).run()