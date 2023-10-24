from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import *
from OpenGL.GL import *
from PyQt5 import QtCore

from he.hecontroller import HeController
from he.hemodel import HeModel
from geometry.segments.line import Line
from geometry.segments.polyline import Polyline
from geometry.point import Point
from compgeom.tesselation import Tesselation

class MyCanvas(QtOpenGL.QGLWidget):

    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_hmodel = HeModel()
        self.m_controller = HeController(self.m_hmodel)
        self.m_w = 0 #width: GL canvas horizontal size
        self.m_h = 0 #height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPointF(0.0,0.0)
        self.m_pt1 = QtCore.QPointF(0.0,0.0)
        self.m_pt2 = QtCore.QPointF(0.0,0.0)

        self.mode = 0    #0 para linha, 1 para bezier
        self.beziercount = 0
        self.granuality = 50

        self.insersegment = False
        #self.cont = 0    #variavel usada para contar quantas vezes paintGL foi executado (usada para resolver um bug que deixava varias linhas desenhadas ao redimensionar a janela)
    
    def initializeGL(self):
        #glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)
    
    def resizeGL(self, _width, _height):
        #store GL canvas sizes in object properties
        self.m_w = _width
        self.m_h = _height
        
        if(self.m_hmodel == None) or (self.m_hmodel.isEmpty()): self.scaleWorldWindow(1.0)
        else:
            self.m_L, self.m_R, self.m_B, self.m_T = self.m_hmodel.getBoundBox()
            self.scaleWorldWindow(1.1)

        #setup the viewport to canvas dimensions
        glViewport(0, 0, self.m_w, self.m_h)
        #reset the cordinate system
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #Establish the clipping colume by setting up an orthographic projection
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        #setup display in model cordinates
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def paintGL(self):
        
        #limpando buffer para evitar bug de linhas antigas no redimensionamento
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #se o botão do mouse estiver pressionado, mostrar linha da curva na tela
        if(self.m_buttonPressed == True):
            glCallList(self.list)
            glDeleteLists(self.list, 1)
            self.list = glGenLists(1)
            glNewList(self.list, GL_COMPILE)
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt1_U.y())
            glEnd()
            glEndList()
        if not(self.m_hmodel.isEmpty()):
            #print("teste", self.cont)      #imprimindo teste
            #self.cont = self.cont + 1      #atualizando valor de contagem
            patches = self.m_hmodel.getPatches()
            for pat in patches:
                pts = pat.getPoints()
                triangs = Tesselation.tessellate(pts)
                for j in range(0, len(triangs)):
                    glColor3f(1.0, 0.0, 1.0)
                    glBegin(GL_TRIANGLES)
                    glVertex2d(pts[triangs[j][0]].getX(), pts[triangs[j][0]].getY())
                    glVertex2d(pts[triangs[j][1]].getX(), pts[triangs[j][1]].getY())
                    glVertex2d(pts[triangs[j][2]].getX(), pts[triangs[j][2]].getY())
                    glEnd()
            segments = self.m_hmodel.getSegments()
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glColor3f(0.0,1.0,1.0)
                glBegin(GL_LINE_STRIP)
                for point in ptc:
                    glVertex2f(point.getX(), point.getY())
                glEnd()
            '''
            for curv in segments:
                ptsnumber = curv.getNumberOfPoints()
                print('curv', i, ":", ptsnumber, sep=' ')
                i+=1
                ptc = curv.getPointsToDraw()
                glColor3f(0.0,1.0,1.0)

                if(ptsnumber>2):
                    glBegin(GL_LINE_STRIP)
                    for point in ptc:
                        glVertex2f(point.getX(), point.getY())
                    glEnd()
                else:
                    glBegin(GL_LINES)
                    for point in ptc:
                        glVertex2f(point.getX(), point.getY())
                    glEnd()
            '''
    
    def setModel(self, _model):
        self.m_model = _model
    
    def fitWorldToViewport(self):
        #print("fitWorldToViewport")
        if self.m_hmodel == None:
            return
        self.m_L, self.m_R, self.m_B, self.m_T = self.m_hmodel.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()
        self.repaint()
    
    def scaleWorldWindow(self, _scaleFac):
        #compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w
        #get current window center
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        #set new window sizes based on scaling factor
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac
        #Adjust window to keep the same aspect ratio of the viewport
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr
        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        #Establish the clipping volume by setting up an
        #orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
    
    def panWorldWindow(self, _panFacX, _panFacY):
        #compute pan distances in horizontal and vertical directions
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        #shift current window
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        #Establish the clipping volume by setting up an
        #orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
    
    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x,y)

    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        if(self.mode == 0):
            self.m_pt0 = event.pos()

    def mouseMoveEvent(self, event):
        #coletando retas se mode == 0
        if(self.mode == 0):
            if self.m_buttonPressed:
                self.m_pt1 = event.pos()
                self.update()

    def mouseReleaseEvent(self, event):
        if(self.mode == 0):
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
            p0 = Point(pt0_U.x(), pt0_U.y())
            p1 = Point(pt1_U.x(), pt1_U.y())
            segment = Line(p0,p1)
            self.m_controller.insertSegment(segment, 0.01)
            self.update()
            self.repaint()
            self.m_buttonPressed = False
        if(self.mode == 1):
            if(self.beziercount == 0):
                self.m_pt0 = event.pos()
                print('pos 0 coletada')
                self.beziercount+=1
                self.m_buttonPressed = False
            elif(self.beziercount == 1):
                self.m_pt1 = event.pos()
                print('pos 1 coletada')
                self.beziercount+=1
                self.m_buttonPressed = False
            elif(self.beziercount == 2):
                self.m_pt2 = event.pos()
                print('pos 2 coletada')
                #fim da coleta, adicionar curvas
                self.beziercount = 0

                pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
                pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
                pt2_U = self.convertPtCoordsToUniverse(self.m_pt2)

                p0 = Point(pt0_U.x(), pt0_U.y())
                '''
                segmento = Polyline()
                segmento.addPoint(pt0_U.x(),pt0_U.y())
                segmento.addPoint(pt1_U.x(),pt1_U.y())
                segmento.addPoint(pt2_U.x(),pt2_U.y())
                print(segmento.getNumberOfPoints())
                #inserimos segmento na lista
                self.m_controller.insertSegment(segmento, 0.01)
                '''
                for t in range(0, self.granuality):
                    t = t/self.granuality
                    x = pt1_U.x() + (1 - t)**2 * (pt0_U.x()-pt1_U.x()) + t**2 * (pt2_U.x() - pt1_U.x())
                    y = pt1_U.y() + (1 - t)**2 * (pt0_U.y()-pt1_U.y()) + t**2 * (pt2_U.y() - pt1_U.y())
                    #definimos segundo ponto do segmento
                    p1 = Point(x, y)
                    print('Imprimindo pontos', pt0_U.x(), pt0_U.y(), x, y)
                    #agora temos 2 pontos, criamos a linha
                    segment = Line(p0,p1)
                    #inserimos segmento na lista
                    self.m_controller.insertSegment(segment, 0.01)
                    #atualizar p0 para proximo loop
                    p0 = Point(x, y)
                ''''''
                self.update()
                self.repaint()
                self.m_buttonPressed = False
                
            
        