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
        self.granuality = 100

        self.linecount = 0
        self.beziercount = 0

        #Controla se houve movimento para iniciar tracking do desenho
        self.moved =  False

        #self.cont = 0    #variavel usada para contar quantas vezes paintGL foi executado (usada para resolver um bug que deixava varias linhas desenhadas ao redimensionar a janela)

        #vamos rastrear o mouse independente de haver clique (press event)
        self.setMouseTracking(True)
    
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
        
        #Para gerar previsualização da Linha, checamos se o primeiro ponto foi coletado, caso sim, atualizamos conforme movimento do mouse para desenhar
        if(self.linecount == 1):
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
        #se o tipo de linha for bezier vamos mostrar com linhas retas a ligação entre os pontos de controle
        #Checamos se há primeiro ponto coletado, se sim, desenhar linhas entre pontos de controle
        if(self.mode == 1):
            #caso estejamos coletando o pt1, desenhar entre pt0 e pt1
            if(self.beziercount == 1):
                glCallList(self.list)
                glDeleteLists(self.list, 1)
                self.list = glGenLists(1)
                glNewList(self.list, GL_COMPILE)
                pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
                pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
                glColor3f(1.0, 0.0, 0.0)
                glLineStipple(1, 0xAAAA)
                glEnable(GL_LINE_STIPPLE)
                glBegin(GL_LINE_STRIP)
                glVertex2f(pt0_U.x(), pt0_U.y())
                glVertex2f(pt1_U.x(), pt1_U.y())
                glEnd()
                glEndList()
            #caso estejamos coletando o pt2, desenhar entre pt0, pt1 e pt2
            if(self.beziercount == 2):
                glCallList(self.list)
                glDeleteLists(self.list, 1)
                self.list = glGenLists(1)
                glNewList(self.list, GL_COMPILE)
                pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
                pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
                pt2_U = self.convertPtCoordsToUniverse(self.m_pt2)
                glColor3f(1.0, 0.0, 0.0)
                glLineStipple(1, 0xAAAA)
                glEnable(GL_LINE_STIPPLE)
                glBegin(GL_LINE_STRIP)
                glVertex2f(pt0_U.x(), pt0_U.y())
                glVertex2f(pt1_U.x(), pt1_U.y())
                glVertex2f(pt2_U.x(), pt2_U.y())
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

    #a forma de coleta da linha foi alterado para coletagem on release, assim, apenas setamos como true que o botão foi pressionado
    def mousePressEvent(self, event):
        self.m_buttonPressed = True

    #na inicialização definimos para sempre rastrear o mouse, assim, conseguimos definir os pontos para linha guia interativamente
    def mouseMoveEvent(self, event):
        #coletando retas se mode == 0
        if(self.mode == 0):
            if(self.linecount == 1):
                self.m_pt1 = event.pos()
                self.update()
        #coletando retas se mode ==1
        if(self.mode == 1):
            #se o contador da bezier está em 1 o primeiro ponto foi coletado
            #atualizar posição do ponto 2 pra previa
            if(self.beziercount == 1):
                self.m_pt1 = event.pos()
                self.update()
            if(self.beziercount == 2):
                self.m_pt2 = event.pos()
                self.update()

    #toda a coleta se dará no evento (mouserelease)
    def mouseReleaseEvent(self, event):
        
        #coletando retas (modo 0)
        if(self.mode == 0):
            #checamos se algum ponto foi coletado, se não coletamos o primeiro ponto e atualizamos o atributo
            if(self.linecount == 0):
                self.m_pt0 = event.pos()
                self.m_pt1 = event.pos() #definimos o ponto 1 provisoriamente como o mesmo para tracking dinamico da linha guia, evita aparecerem linhas com pontos antigos
                self.linecount+=1
                self.update()
                self.repaint()
            #se o primeiro ponto foi coletado, coletamos o segundo ponto e adicionamos o segmento ao model
            elif(self.linecount == 1):
                self.m_pt1 = event.pos()
                pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
                pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
                p0 = Point(pt0_U.x(), pt0_U.y())
                p1 = Point(pt1_U.x(), pt1_U.y())
                segment = Polyline([p0,p1])
                self.m_controller.addSegment(segment, 0.01)
                self.update()
                self.repaint()
                self.linecount=0 #resetando contagem de pontos para proxima linha
            #botão foi solto (release)
            self.m_buttonPressed = False 

        #coletando as curvas bezier quadráticas (modo 1)    
        if(self.mode == 1):
            #checamos se algum ponto foi coletado, se não coletamos o primeiro ponto e atualizamos o atributo
            if(self.beziercount == 0):
                self.m_pt0 = event.pos()
                self.m_pt1 = event.pos() #definindo ponto para linhas guias interativas
                self.beziercount+=1
                self.update()
                self.repaint()
            #Se um ponto foi coletado, vamos coletar o segundo ponto e atualizar o atributo
            elif(self.beziercount == 1):
                self.m_pt1 = event.pos()
                self.m_pt2 = event.pos() #definindo ponto para linhas guias interativas
                self.beziercount+=1
                self.update()
                self.repaint()
            #se o segundo ponto foi coletado, vamos coletar o terceiro e ultimo ponto, adicionar segmento no model e resetar o atributo beziercount
            elif(self.beziercount == 2):
                self.m_pt2 = event.pos()
                #fim da coleta, adicionar curvas
                self.beziercount = 0 #resetando atributo
                #convertendo pontos
                pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
                pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
                pt2_U = self.convertPtCoordsToUniverse(self.m_pt2)
                #criando o segmento
                segment = Polyline()
                #adicionando primeiro ponto do segmento
                segment.addPoint(pt0_U.x(), pt0_U.y())
                #loop para encontrar as coordenadas x e y usando a formula para calculos de bezier quadratica com paretro t
                #B(t) = (1-t)²P0 + 2t(1-t)P1 + t²P2
                #a variável self.granuality controla a granularidade do loop
                for t in range(0, self.granuality):
                    t = t/self.granuality
                    x = (1-t)**2*pt0_U.x() + 2*t*(1-t)*pt1_U.x() + t**2*pt2_U.x()
                    y = (1-t)**2*pt0_U.y() + 2*t*(1-t)*pt1_U.y() + t**2*pt2_U.y()
                    #para cada novo ponto calculado, adicionar ao segmento
                    segment.addPoint(x,y)
                #após o fim do calculo dos pontos inserimos o segmento na lista
                self.m_controller.addSegment(segment, 0.01)
                self.update()
                self.repaint()
            #botão foi solto (release)
            self.m_buttonPressed = False
    
    #função que limpa o canvas removendo todos os segmentos da tela
    def resetCanvas(self):
        self.m_hmodel.clearAll()
        self.update()
        self.repaint()
                
            
        