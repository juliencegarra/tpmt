#-*- coding: utf-8 -*-
#!/usr/bin/env python

# TimePressureMazeTask (TPMT)
# (c) Julien Cegarra


import pygame
import os
import copy
import math
import time
import math
import sys
import string
from PySide import QtCore, QtGui
import codecs, unicodedata
import random

# Definitions of the scenarios
# The key is used in the 'participant' window
scenarios = {}
scenarios['a']={'T':'estimation','PT':1, 'dial':0}
scenarios['b']={'T':'estimation','PT':0, 'dial':0}
scenarios['c']={'T':'estimation','PT':1, 'dial':1}
scenarios['d']={'T':'estimation','PT':0, 'dial':1}

scenarios['e']={'T':'production','PT':1, 'dial':0}
scenarios['f']={'T':'production','PT':0, 'dial':0}
scenarios['g']={'T':'production','PT':1, 'dial':1}
scenarios['h']={'T':'production','PT':0, 'dial':1}

scenarios['i']={'T':'prospective','PT':1, 'dial':0}
scenarios['j']={'T':'prospective','PT':0, 'dial':0}
scenarios['k']={'T':'prospective','PT':1, 'dial':1}
scenarios['l']={'T':'prospective','PT':0, 'dial':1}


class partie():
    def __init__(self, fichier_level, scenario, id_sujet):

        pygame.init()
        pygame.display.set_caption("")

        self.case_width = 24
        self.case_height = 24

        self.font_a = pygame.font.Font("res/porkys.ttf", 190)
        self.font_b = pygame.font.Font("res/porkys.ttf", 34)
        self.font_c = pygame.font.SysFont("Arial", 22)

        self.screen = pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()


        self.scenario = scenario

        self.fichier_level = fichier_level

        self.task_type = scenarios[scenario]['T']
        self.pressure_type = scenarios[scenario]['PT']
        self.info_type = scenarios[scenario]['dial']
        self.fail_type = 0
        self.id_sujet = id_sujet


        if "short" in fichier_level.lower():
            self.delay_before_exit = 30.0
            self.type_duree = "short"
        elif "medium" in fichier_level.lower():
            self.delay_before_exit = 60.0
            self.type_duree = "medium"
        elif "long" in fichier_level.lower():
            self.delay_before_exit = 90.0
            self.type_duree = "long"
        if "training" in fichier_level.lower():
            self.delay_before_exit = 15.0
            self.type_duree ="training"

        if ("fail" in fichier_level.lower()):
            self.fail_type = 1

        if self.task_type=="production" or self.task_type=="prospective":
            tmp = str(round(self.delay_before_exit, 0)).replace(".0", "")
            if tmp == "60":
                tmp = "1 minute"
            elif tmp=="90":
                tmp = "1 minute 30"
            else:
                tmp += " seconds"
            self.infobox("You have to press the space key after "+tmp)




        #default colors
        self.edgeLightColor=(255, 206, 255, 255)
        self.fillColor=(132, 0, 132, 255)
        self.edgeShadowColor=(255, 0, 255, 255)
        self.pelletColor=(128, 0, 128, 255)


        self.oldEdgeLightColor = self.edgeLightColor
        self.oldEdgeShadowColor = self.edgeShadowColor
        self.oldFillColor = self.fillColor

        self.loadfruits()
        self.loadanimations()
        self.newlevel()




    def newlevel(self):
        self.listresults=[]
        self.results_to_save=[]

        self.loadlevel()
        self.loadimages()


        self.findshortedpathByFloodFill()
        self.initializeghost()
        self.drawbackground()
        self.startGame()

    def initializeghost(self):
        self.ghost_x = self.start_x
        self.ghost_y = self.start_y
        self.ghost_visible = False

    def loadimages(self):
        listimages  = []
        self.tile_table = {}

        for i in self.tablelevel:
            if i not in listimages and i!=' ' and i!='#':
                listimages.append(i)
                self.tile_table[i] = pygame.image.load("res/tiles/wall-"+i+".gif").convert()

                for y in range(0, 16, 1):
                    for x in range(0, 16, 1):
                        if self.tile_table[i].get_at( (x, y) ) == (255, 206, 255, 255):
                            # wall edge
                            self.tile_table[i].set_at( (x, y), self.edgeLightColor )

                        elif self.tile_table[i].get_at( (x, y) ) == (132, 0, 132, 255):
                            # wall fill
                            self.tile_table[i].set_at( (x, y), self.fillColor )

                        elif self.tile_table[i].get_at( (x, y) ) == (255, 0, 255, 255):
                            # shadow color
                            self.tile_table[i].set_at( (x, y), self.edgeShadowColor )

                        elif self.tile_table[i].get_at( (x, y) ) == (128, 0, 128, 255):
                            # pellet color
                            self.tile_table[i].set_at( (x, y), self.pelletColor )

    def loadfruits(self):
        self.fruits={}
        for i in range(0, 5, 1):
            self.fruits[i] = pygame.image.load(os.path.join("res","sprite","fruit " + str(i) + ".gif")).convert()

    def loadanimations(self):
        self.animFrame=0
        self.anim_pacmanL = {}
        self.anim_pacmanR = {}
        self.anim_pacmanU = {}
        self.anim_pacmanD = {}
        self.anim_pacmanS = {}
        self.anim_pacmanCurrent = {}

        PACMAN_WIDTH=20
        PACMAN_HEIGHT=20
        for i in range(1, 9, 1):
            self.anim_pacmanL[i] = pygame.image.load(os.path.join("res","sprite","pacman-l " + str(i) + ".gif")).convert()
            self.anim_pacmanL[i] = pygame.transform.smoothscale(self.anim_pacmanL[i], (PACMAN_WIDTH,PACMAN_HEIGHT))
            self.anim_pacmanR[i] = pygame.image.load(os.path.join("res","sprite","pacman-r " + str(i) + ".gif")).convert()
            self.anim_pacmanR[i] = pygame.transform.smoothscale(self.anim_pacmanR[i], (PACMAN_WIDTH,PACMAN_HEIGHT))
            self.anim_pacmanU[i] = pygame.image.load(os.path.join("res","sprite","pacman-u " + str(i) + ".gif")).convert()
            self.anim_pacmanU[i] = pygame.transform.smoothscale(self.anim_pacmanU[i], (PACMAN_WIDTH,PACMAN_HEIGHT))
            self.anim_pacmanD[i] = pygame.image.load(os.path.join("res","sprite","pacman-d " + str(i) + ".gif")).convert()
            self.anim_pacmanD[i] = pygame.transform.smoothscale(self.anim_pacmanD[i], (PACMAN_WIDTH,PACMAN_HEIGHT))
            self.anim_pacmanS[i] = pygame.image.load(os.path.join("res","sprite","pacman.gif")).convert()
            self.anim_pacmanS[i] = pygame.transform.smoothscale(self.anim_pacmanS[i], (PACMAN_WIDTH,PACMAN_HEIGHT))

        ghostcolor={}
        ghostcolor[0] = (255, 0, 0, 255)
        ghostcolor[1] = (255, 128, 255, 255)
        ghostcolor[2] = (128, 255, 255, 255)
        ghostcolor[3] = (255, 128, 0, 255)
        ghostid = 0

        self.animghost = {}
        self.animFrameGhost=1
        for i in range(1, 7, 1):
            self.animghost[i] = pygame.image.load(os.path.join("res","sprite","ghost " + str(i) + ".gif")).convert()
            self.animghost[i] = pygame.transform.smoothscale(self.animghost[i], (PACMAN_WIDTH,PACMAN_HEIGHT))



    def loadlevel(self):
        self.linelen=0
        self.cursor_x=-1
        self.cursor_y=-1
        self.fin_x=-1
        self.fin_y=-1
        currentline = 0
        self.velX=0
        self.velY=0
        self.fruit_x=-1
        self.fruit_y=-1


        level = self.fichier_level

        self.tablelevel = []
        self.levelfog = {}
        fp = open("res/"+level, 'r')
        for currentline, j in enumerate(fp):
            ligne = j.strip('\r').strip('\n')

            if "\t" in ligne:
                print "There is a problem with the level named: "+level+". There is a tabulation in the line: "+str(currentline)+". Please fix it to check your level alignment."

            if len(ligne.replace(' ',''))>0:

                if currentline==0:
                    self.linelen=len(ligne)
                    if " " in ligne and ligne.index(" ")>0:
                        self.cursor_x=ligne.index(" ")
                        self.cursor_y=0
                        self.velX=0
                        self.velY=1
                else:
                    if len(ligne)!=self.linelen:
                        print "There is a problemwithin the level named:  "+level+". The line : "+str(currentline)+" is not "+str(self.linelen)+" characters long."
                        #print ligne


                if self.cursor_x==-1:
                    #from left to right
                    if ligne[0]==' ':
                        self.cursor_x=0
                        self.cursor_y=currentline

                for currentcolumn, l in enumerate(ligne):
                    if len(ligne.replace(' ',''))>0:
                        self.tablelevel.append(l)
                        if self.cursor_y==0 and " " in ligne:
                            self.fin_x=ligne.index(" ")
                            self.fin_y=currentline

                if self.fin_y==-1:
                    if ligne[self.linelen-1]==' ':
                        self.fin_x=self.linelen-1
                        self.fin_y=currentline
                        self.velX=1
                        self.velY=0
        fp.close()




        if self.cursor_x==-1 or self.cursor_y==-1:
            print "bug : no start point!"
            sys.exit()
        elif self.fin_x==-1 or self.fin_y==-1:
            print "bug : no exit!"
            sys.exit()


        self.start_x=self.cursor_x
        self.start_y=self.cursor_y


        self.nblines = currentline+1




        #Establish corners
        for y in range(0, self.nblines):
            for x in range(0, self.linelen):
                tile = self.tablelevel[x+y*self.linelen]
                if tile != ' ':
                    if x>0 and self.tablelevel[(x-1)+y*self.linelen]!=' ':
                        if x<=self.linelen and y+1<self.nblines and self.tablelevel[(x+1)+y*self.linelen]!=' ':
                            if y>0 and self.tablelevel[(x)+(y-1)*self.linelen]!=' ':
                                if y+1<self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    if x!=self.linelen-1:
                                        self.tablelevel[x+y*self.linelen]="x"
                                    else:
                                        self.tablelevel[x+y*self.linelen]="t-right"

                                else:
                                    self.tablelevel[x+y*self.linelen]="t-bottom"
                            else:
                                if y+1<self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    if x!=self.linelen-1:
                                        self.tablelevel[x+y*self.linelen]="t-top"
                                    else:
                                        self.tablelevel[x+y*self.linelen]="corner-ur"
                                else:
                                    self.tablelevel[x+y*self.linelen]="straight-horiz"


                        else:
                            if y>0 and self.tablelevel[(x)+(y-1)*self.linelen]!=' ':
                                 if y+1<self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    self.tablelevel[x+y*self.linelen]="t-right"
                                 else:
                                    if y==self.nblines-1:
                                        if x!=self.linelen-1:
                                            self.tablelevel[x+y*self.linelen]="t-bottom"
                                        else:
                                            self.tablelevel[x+y*self.linelen]="corner-lr"

                                    else:
                                        self.tablelevel[x+y*self.linelen]="corner-lr"
                            else:
                                 if y+1<self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    self.tablelevel[x+y*self.linelen]="corner-ur"
                                 else:
                                    if self.tablelevel[(x-1)+y*self.linelen]!=' ' and self.tablelevel[(x+1)+y*self.linelen]!=' ':
                                        self.tablelevel[x+y*self.linelen]="straight-horiz"
                                    else:
                                        self.tablelevel[x+y*self.linelen]="end-r"
                    else:
                        if x<self.linelen and self.tablelevel[(x+1)+y*self.linelen]!=' ':
                            if y>0 and self.tablelevel[(x)+(y-1)*self.linelen]!=' ':
                                if y+1<self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    if x!=self.linelen-1:
                                        self.tablelevel[x+y*self.linelen]="t-left"
                                    else:
                                        self.tablelevel[x+y*self.linelen]="straight-vert"

                                else:
                                    self.tablelevel[x+y*self.linelen]="corner-ll"
                            else:
                                if y+1<=self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    self.tablelevel[x+y*self.linelen]="corner-ul"
                                else:
                                    self.tablelevel[x+y*self.linelen]="end-l"


                        else:
                            if y>0 and self.tablelevel[(x)+(y-1)*self.linelen]!=' ':
                                 if y+1<=self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    self.tablelevel[x+y*self.linelen]="straight-vert"
                                 else:
                                    self.tablelevel[x+y*self.linelen]="end-b"
                            else:
                                 if y+1<=self.nblines and self.tablelevel[(x)+(y+1)*self.linelen]!=' ':
                                    self.tablelevel[x+y*self.linelen]="end-t"
                                 else:
                                    self.tablelevel[x+y*self.linelen]="end-l"


        self.fogUpdate(self.cursor_x, self.cursor_y, 1)
        self.fogUpdate(self.fin_x,self.fin_y, 1)

        self.last_good_position= 0




    def findshortedpathByFloodFill(self):
	 # Flood fill. An A* star algorithm is not really required for maze this size.

        self.floodcalc = copy.deepcopy(self.tablelevel)
        for i, j in enumerate(self.floodcalc):
            if j!=' ':
                self.floodcalc[i]='#'

        self.distancesortie=-1

        listfloodnexttmp=[]
        listfloodnext=[]
        listfloodnext.append(self.fin_x+(self.fin_y)*self.linelen) #exit

        self.floodcalc[self.fin_x+(self.fin_y)*self.linelen]=0

        while len(listfloodnext)>0:
            listfloodnexttmp=copy.deepcopy(listfloodnext)
            listfloodnext=[]

            for i in listfloodnexttmp:
                val = self.floodcalc[i]
                if i>1 and self.floodcalc[i-1]==' ':
                    listfloodnext.append(i-1)
                    self.floodcalc[i-1]=val+1
                if i<(self.nblines-1)*self.linelen and self.floodcalc[i+1]==' ':
                    listfloodnext.append(i+1)
                    self.floodcalc[i+1]=val+1
                if i>self.linelen and self.floodcalc[i-self.linelen]==' ':
                    listfloodnext.append(i-self.linelen)
                    self.floodcalc[i-self.linelen]=val+1
                if i<(self.nblines-1)*self.linelen and self.floodcalc[i+self.linelen]==' ':
                    listfloodnext.append(i+self.linelen)
                    self.floodcalc[i+self.linelen]=val+1


        if self.floodcalc[self.start_x+(self.start_y*self.linelen)]==' ':
            print "THE MAZE EXIT WAS NOT FOUND IN THIS LEVEL! ABORTING."
            sys.exit(1)
            return
        else:
            self.distancesortie=self.floodcalc[self.start_x+(self.start_y)*self.linelen]





	# Retrace path
        position = self.start_x+(self.start_y)*self.linelen
        val = self.floodcalc[position]
        self.shortestpath = []

        while val>0:
            self.shortestpath.append(position)
            val-=1

            if self.floodcalc[position-1]==val:
                position = position-1

            elif i<(self.nblines-1)*self.linelen and self.floodcalc[position+1]==val:
                position = position+1
                #print
            elif i>self.linelen and self.floodcalc[position-self.linelen]==val:
                position = position-self.linelen
            elif i<(self.nblines-1)*self.linelen and self.floodcalc[position+self.linelen]==val:
                position = position+self.linelen
            else:
                print "Shortest path not found!" + str(val)
                break





    def drawplayer(self):
        if (self.velX != 0 or self.velY != 0) and self.gamemode==4:
            # only move mouth when the player is moving
            self.animFrame += 1

            if self.animFrame == 9:
                # wrap to beginning
                self.animFrame = 1


        if self.animFrame == 0:
            self.animFrame = 1

        if self.velX > 0:
            self.anim_pacmanCurrent = self.anim_pacmanR
        elif self.velX < 0:
            self.anim_pacmanCurrent = self.anim_pacmanL
        elif self.velY > 0:
            self.anim_pacmanCurrent = self.anim_pacmanD
        elif self.velY < 0:
            self.anim_pacmanCurrent = self.anim_pacmanU
        else:
            self.animFrame = 1 #static
            self.anim_pacmanCurrent = self.anim_pacmanS

        self.background.blit (self.anim_pacmanCurrent[ self.animFrame ], (self.cursor_x*self.case_width+4, self.cursor_y*self.case_height+4))

    def drawghost(self):
        if self.ghost_visible==True:
            self.animFrameGhost+=1
            if self.animFrameGhost>6:
                self.animFrameGhost=1
            elif self.animFrameGhost==0:
                self.animFrameGhost=1
            self.background.blit (self.animghost[ self.animFrameGhost ], ((self.ghost_x)*self.case_width+4, self.ghost_y*self.case_height+4))


    def drawbackground(self):
        self.background = pygame.Surface((self.linelen*self.case_width,self.nblines*self.case_height))
        self.background.fill((0, 0, 0))

        fog_actif=True

        for y in range(0, self.nblines):
            for x in range(0, self.linelen):
                tile = self.tablelevel[x+y*self.linelen]
                if tile!=' ' and tile!='#':
                    if self.levelfog.has_key(str(x)+"-"+str(y)) and fog_actif==True:
                        self.tile_table[tile].set_alpha(self.levelfog[str(x)+"-"+str(y)])
                        self.background.blit(self.tile_table[tile], (x*self.case_width, y*self.case_height))
                    elif fog_actif==False:
                        self.background.blit(self.tile_table[tile], (x*self.case_width, y*self.case_height))

                if tile=="#":
                    print "BUG IN THE LEVEL! SHOULD NOT OCCUR"

        #There is a fruit on path
        if self.fruit_x!=-1 and self.fruit_y!=-1:
            if self.levelfog.has_key(str(self.fruit_x)+"-"+str(self.fruit_y)) and fog_actif==True:
                self.fruits[ 4 ].set_alpha(self.levelfog[str(self.fruit_x)+"-"+str(self.fruit_y)])
                self.background.blit (self.fruits[ 4 ], ((self.fruit_x)*self.case_width+4, self.fruit_y*self.case_height+4))
            elif fog_actif==False:
                self.background.blit (self.fruits[ 4 ], ((self.fruit_x)*self.case_width+4, self.fruit_y*self.case_height+4))


        #There is a fruit at the exit
        self.background.blit (self.fruits[ 2 ], ((self.fin_x)*self.case_width+4, self.fin_y*self.case_height+4))



    def fogUpdate_radius(self, x, y, radius, typefog):
        route=[x, y]

        if typefog==1:
            if radius==0:
                fog = 255
            elif radius==1:
                fog = 120
            elif radius==2:
                fog = 60
            elif radius==3:
                fog = 20

            if self.levelfog.has_key(str(x)+"-"+str(y)):
                if self.levelfog[str(x)+"-"+str(y)]>fog:
                    return


            self.levelfog[str(x)+"-"+str(y)]=fog
        else:
            if self.levelfog.has_key(str(x)+"-"+str(y)):
                fog = self.levelfog[str(x)+"-"+str(y)]
                fog-=40
                if fog<0:
                    fog=0

            self.levelfog[str(x)+"-"+str(y)]=fog




    def fogUpdate(self, x, y, typefog):
        radius_max = 3
        for radius in range(0, radius_max):
            coingauche_x = x
            if x-radius>0:
                coingauche_x = x-1-radius

            coindroite_x = x
            if x+radius<self.linelen:
                coindroite_x = x+1+radius

            cointbas_y = y
            if y-radius>0:
                cointbas_y = y-1-radius

            coinhaut_y = y
            if y+radius<self.nblines:
                coinhaut_y = y+1+radius


            for tmpx in range(coingauche_x, coindroite_x+1):
                self.fogUpdate_radius(tmpx, cointbas_y, radius, typefog)
                self.fogUpdate_radius(tmpx, coinhaut_y, radius, typefog)
            for tmpy in range(cointbas_y, coinhaut_y+1):
                self.fogUpdate_radius(coingauche_x, tmpy, radius, typefog)
                self.fogUpdate_radius(coindroite_x, tmpy, radius, typefog)





    def ghostMovement(self):
        pos_fantome = self.floodcalc[(self.ghost_x)+self.ghost_y*self.linelen]
        pos_participant = self.floodcalc[(self.cursor_x)+self.cursor_y*self.linelen]

        distance = pos_fantome-pos_participant

        stringtosave = ""

        if self.ghost_visible==False and pos_fantome>pos_participant+10:
            self.ghost_visible=True
            self.ghost_pos_list=0
            delai=sum(self.participant_time)/len(self.participant_time)
            self.next_movement_time = time.time()+delai
            return

        if self.ghost_visible==False or time.time()<self.next_movement_time:
            return

        delai=sum(self.participant_time)/len(self.participant_time)

        #Speed calibration
        if self.fail_type == 1:
            delai = delai-delai/2


        elif self.fail_type == 0:
            if self.pressure_type == 1:
                #Time pressure is enabled

                if distance<5:
                    delai = delai*3

                elif distance>15:
                    delai = delai/2

                else:
                    delai = delai

            else:
                #Without pressure...
                delai = delai*2 # 2 time the average time


        self.next_movement_time = time.time()+delai


        self.ghost_pos_list+=1
        self.ghost_x, self.ghost_y = self.cheminparticipant[self.ghost_pos_list]

        self.fogUpdate(self.ghost_x, self.ghost_y, 0)


        stringtosave = ";"+str(time.time()-self.start_game)+";GHOST_ACTION"+";-1;"+str(self.ghost_x)+";"+str(self.ghost_y)+";"+str(self.floodcalc[(self.ghost_x)+self.ghost_y*self.linelen])+";"+str(len(self.cheminparticipant))+";"+str(self.ghost_pos_list)

        if self.ghost_x == self.cursor_x and self.ghost_y == self.cursor_y and self.ghost_visible==True:
            stringtosave+="The ghost eat the player"
            self.modeTimer = 0
            self.gamemode=7
            self.tempsfinal = time.time()-self.start_game

        elif self.floodcalc[(self.ghost_x)+self.ghost_y*self.linelen]==0:
            stringtosave+="The ghost is at the exit"
            self.modeTimer = 0
            self.gamemode=7
            self.tempsfinal = time.time()-self.start_game

        if stringtosave!="":
            self.results_to_save.append(stringtosave)



    def playerMovement(self, velX, velY):
        self.velX = velX
        self.velY=velY
        self.cursor_x+=velX
        self.cursor_y+=velY
        self.nbappuistouches+=1

        self.fogUpdate(self.cursor_x, self.cursor_y, 1)

        #path followed by the participant
        self.cheminparticipant.append([self.cursor_x, self.cursor_y])
        self.distanceparticipantfantome.append(len(self.cheminparticipant)-self.ghost_pos_list)

        temps_de_mouvement = time.time()-self.derniere_action
        self.participant_time.append(temps_de_mouvement)

        self.derniere_action=time.time()

        tmpk="BAD PATH"
        for i in [i for i,x in enumerate(self.shortestpath) if x == self.cursor_x+(self.cursor_y)*self.linelen]:
            self.last_good_position = i
            tmpk="GOOD PATH"


        stringtosave = ";"+str(time.time()-self.start_game)+";PARTICIPANT_ACTION"+";"+str(temps_de_mouvement)+";"+str(self.cursor_x)+";"+str(self.cursor_y)+str(self.floodcalc[(self.cursor_x)+self.cursor_y*self.linelen])+";"+str(len(self.cheminparticipant)-self.ghost_pos_list)+";"+tmpk+";"



        if self.cursor_x==self.fin_x and self.cursor_y==self.fin_y and self.gamemode!=7:
            stringtosave+="EXIT;END;"
            self.modeTimer = 0
            self.gamemode=7
            self.tempsfinal = time.time()-self.start_game

        elif self.cursor_x==self.fruit_x and self.cursor_y==self.fruit_y and self.gamemode!=7:
            stringtosave+= "EXIT;FRUIT;"+str(time.time()-self.start_game)+" seconds"
            self.modeTimer = 0
            self.gamemode=7
            self.tempsfinal = time.time()-self.start_game

        self.results_to_save.append(stringtosave)





    def displayExitEstimationMode(self):
        if self.delay_before_exit>0 and self.fruit_x==-1:


            if len(self.participant_time)==0:
                return

            if (time.time()-self.start_game)+(sum(self.participant_time)/len(self.participant_time))*3>=self.delay_before_exit:
                    tmpk = self.last_good_position+3
                    if tmpk>len(self.shortestpath)-1:
                        tmpk=len(self.shortestpath)-1
                    case_fruit = self.shortestpath[tmpk]

                    self.fruit_y=int(case_fruit/self.linelen)
                    self.fruit_x=case_fruit-(self.fruit_y*self.linelen)

                    stringtosave = ";"+str(time.time()-self.start_game)+";FRUIT_GEN"+";-1;"+str(self.fruit_x)+";"+str(self.fruit_y)+str(self.floodcalc[(self.fruit_x)+self.fruit_y*self.linelen])+";"
                    self.results_to_save.append(stringtosave)






    def startGame(self):
        self.gamemode=1

        self.dialprospective = 0.0
        self.message = 0.0

        decompte = 0

        self.appuitemps = 0.0

        self.ghost_pos_list=0
        done = False

        self.modeTimer=0
        self.nbappuistouches = 0
        self.distanceparticipantfantome=[]

        while done==False:
            self.clock.tick (60)
            #pygame.display.set_caption("FPS: %.2f" % (self.clock.get_fps())) # display FPS
            self.drawbackground()
            self.drawplayer()
            self.drawghost()
            self.screen.blit(pygame.transform.smoothscale(self.background,self.screen.get_size()), (0,0))

            if self.dialprospective!=0.0:
                if (time.time()-self.start_game)>(self.dialprospective+1.0):
                    self.dialprospective=0.0
                    stringtosave = ";"+str(time.time()-self.start_game)+";HIDE_DIAL_PROSPECTIVE"+";-1;;;"
                    self.results_to_save.append(stringtosave)
                else:
                    self.label = self.font_b.render(str(self.dialprospective).replace(".0",""), 4, (255, 255, 255))
                    self.screen.blit(self.label, ( (self.screen.get_size()[0]-self.label.get_size()[0])/2,2) )

            if self.message!=0.0:
                if (time.time()-self.start_game)>(self.message+1.0):
                    self.message=0.0
                    stringtosave = ";"+str(time.time()-self.start_game)+";HIDE_MESSAGE"+";-1;;;"
                    self.results_to_save.append(stringtosave)
                else:
                    self.label = self.font_b.render("Spacekey press!", 4, (255, 255, 255))
                    self.screen.blit(self.label, ( (self.screen.get_size()[0]-self.label.get_size()[0])/2,2) )


            if self.gamemode==1:
                if decompte!=0:
                    string = str(decompte)
                else:
                    string = "GO !"
                self.label = self.font_a.render(string, 1, (255, 255, 255))
                self.screen.blit(self.label, ((self.screen.get_size()[0]-self.label.get_size()[0])/2,(self.screen.get_size()[1]-self.label.get_size()[1])/2) )
                self.modeTimer +=1
                if self.modeTimer == 100:
                    decompte-=1
                    self.modeTimer=0
                if decompte==-1:
                    self.gamemode=4
                    self.derniere_action = time.time()
                    self.start_game = time.time()


                    #GAME STARTED!
                    self.participant_time=[]
                    self.cheminparticipant=[]
                    self.cheminparticipant.append([self.cursor_x, self.cursor_y])

                for event in pygame.event.get():
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        done=True
                    elif pygame.key.get_pressed()[pygame.K_F12]:
                        sys.exit(1)
                        done=True




            pygame.display.update()

            pygame.key.set_repeat()

            if self.gamemode == 7: #Level end / Flash
                    self.modeTimer +=1
                    whiteSet = [10, 30, 50, 70]
                    normalSet = [20, 40, 60, 80]


                    if self.modeTimer in whiteSet:
            		# member of white set
                        self.edgeLightColor = (255, 255, 254,255)
                        self.edgeShadowColor = (255, 255, 254,255)
                        self.fillColor = (0, 0, 0,255)
                        self.loadimages()
                        self.drawbackground()

                    elif self.modeTimer in normalSet:
                        # member of normal set
                        self.edgeLightColor = self.oldEdgeLightColor
                        self.edgeShadowColor = self.oldEdgeShadowColor
                        self.fillColor = self.oldFillColor
                        self.loadimages()
                        self.drawbackground()

                    elif self.modeTimer == 150:
                        self.screen.fill((0, 0, 0))
                        pygame.display.update()
                        self.gamemode=8



            if self.gamemode==8:

                partie1 = str(self.id_sujet)+";"+self.scenario+";"+self.fichier_level+";"+str(self.task_type)+";"+str(self.pressure_type)+";"+str(self.info_type)+";"+str(self.type_duree)+";"+str(self.fail_type)

                self.evaltemps=""
                if self.task_type=="estimation":
                    self.evaltemps += self.selectbox() #time estimation "min;sec"
                else:
                    self.evaltemps += "n/a;n/a"

                if self.task_type=='production' or self.task_type=='prospective':
                    self.evaltemps += ";"+str(self.appuitemps) #elapsted time until key press
                else:
                    self.evaltemps+=";"


                #Maze time solving
                #Average duration
                #Number of pressed keys
                #Average distance to the ghost
                tmp = sum(self.distanceparticipantfantome)/len(self.distanceparticipantfantome)
                self.listresults.append(partie1+";"+str(self.tempsfinal)+";"+str(self.evaltemps)+";"+str(sum(self.participant_time)/len(self.participant_time))+";"+str(self.nbappuistouches)+";"+str(tmp))#


                done=True

            if self.gamemode==4:
                if self.task_type=='estimation':
                    #Display the exit after a delay
                    self.displayExitEstimationMode()


                self.ghostMovement()


		# Proceed keyboard events
                for event in pygame.event.get():


                    if pygame.key.get_pressed()[ pygame.K_RIGHT ]:
                        if self.cursor_x<=self.linelen and self.tablelevel[(self.cursor_x+1)+self.cursor_y*self.linelen]==' ':
                            self.playerMovement(1, 0)

                    elif pygame.key.get_pressed()[ pygame.K_LEFT ]:
                        if self.cursor_x>0 and self.tablelevel[(self.cursor_x-1)+self.cursor_y*self.linelen]==' ':
                            self.playerMovement(-1, 0)

                    elif pygame.key.get_pressed()[ pygame.K_DOWN ]:
                        if self.tablelevel[(self.cursor_x)+(self.cursor_y+1)*self.linelen]==' ':
                            self.playerMovement(0, 1)


                    elif pygame.key.get_pressed()[ pygame.K_UP ]:
                        if self.cursor_y>0 and self.tablelevel[(self.cursor_x)+(self.cursor_y-1)*self.linelen]==' ':
                            self.playerMovement(0, -1)


                    elif pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_KP0]:
                        if self.task_type=='production' or self.task_type=='prospective':
                            self.message = round(time.time()-self.start_game,0)

                            tmpk = self.last_good_position+5+random.randrange(5)
                            if tmpk>len(self.shortestpath)-1:
                                tmpk=len(self.shortestpath)-1
                            case_fruit = self.shortestpath[tmpk]
                            #print case_fruit
                            self.fruit_y=int(case_fruit/self.linelen)
                            self.fruit_x=case_fruit-(self.fruit_y*self.linelen)
                            self.appuitemps = time.time()-self.start_game

                            stringtosave = ";"+str(time.time()-self.start_game)+";FRUIT_PRODUCTION_GEN"+";-1;"+str(self.fruit_x)+";"+str(self.fruit_y)+str(self.floodcalc[(self.fruit_x)+self.fruit_y*self.linelen])+";"
                            self.results_to_save.append(stringtosave)

                    elif pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_KP_PERIOD]:
                        if self.task_type=='prospective':
                            if self.dialprospectie==0.0:
                                    stringtosave = ";"+str(time.time()-self.start_game)+";TRY_DISPLAY_DIAL_PROSPECTIVE"+";-1;;;"
                                    self.results_to_save.append(stringtosave)
                            else:
                                    self.dialprospective = round(time.time()-self.start_game,0)
                                    stringtosave = ";"+str(time.time()-self.start_game)+";DISPLAY_DIAL_PROSPECTIVE"+";-1;;;"
                                    self.results_to_save.append(stringtosave)

                    elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        done=True

            if done==True:

                self.nomfichier = os.path.join('results', str(id_sujet))+"/results"

                fz = open(self.nomfichier+"-"+self.fichier_level+"-details.csv", 'a')
                for tmpz in self.results_to_save:
                    fz.write(tmpz+"\n")
                fz.close()

                fz = open(self.nomfichier+"tmp.csv", 'a')
                for tmpz in self.listresults:
                    fz.write(tmpz+"\n")
                fz.close()

                pygame.quit()






    def inputbox(self, question):
      message = ""
      while 1:
        self.screen.fill((0, 0, 0))
        label = self.font_b.render(question, 1, (255, 255, 255))
        self.screen.blit(label, ((self.screen.get_size()[0]-label.get_size()[0])/2,(self.screen.get_size()[1]-label.get_size()[1]*4)/2) )
        if len(message) != 0:
          label = self.font_b.render(message, 1, (255, 255, 255))
          self.screen.blit(label, ((self.screen.get_size()[0]-label.get_size()[0])/2,(self.screen.get_size()[1]-label.get_size()[1])/2) )

        pygame.display.flip()

        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(message)>0:
                   message = message[0:-1]
            elif event.key == pygame.K_RETURN:
                if len(message)>0:
                    break
            elif event.key == pygame.K_ESCAPE:
                break
            else:
              message+=event.unicode
      return message



    def infobox(self, texte):
          rects_ok = False
          over = False

          while 1:
            self.screen.fill((0, 0, 0))
            labela = self.font_b.render(texte, 1, (255, 255, 255))
            self.screen.blit(labela, ((self.screen.get_size()[0]-labela.get_size()[0])/2,(self.screen.get_size()[1]-labela.get_size()[1])/2) )


            label = self.font_b.render("OK", 1, (255, 255, 255))

            pos_x=((self.screen.get_size()[0]-label.get_size()[0])/2)
            pos_y=((self.screen.get_size()[1]-labela.get_size()[1])/2)+labela.get_size()[1]
            self.screen.blit(label, (pos_x,pos_y) )

            if rects_ok == False:
                rect_valide = label.get_rect()
                rect_valide[0]=pos_x
                rect_valide[1]=pos_y
                rects_ok=True


            pygame.display.flip()

            event = pygame.event.poll()
            cursor = pygame.mouse.get_pos()

            if rect_valide.collidepoint(cursor):
                over=True
            else:
                over=False



            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if rect_valide.collidepoint(cursor):
                    return




    def selectbox(self):
          minutes_id = -1
          list_minutes = [x for x in range(10)]
          secondes_id = -1
          list_secondes = [x for x in range(60)]
          rects_minutes = []
          rects_minutes_over = -1
          rects_secondes = []
          rects_secondes_over = -1
          rects_ok = False

          while 1:
            self.screen.fill((0, 0, 0))
            label = self.font_b.render("minutes", 1, (255, 255, 255))
            self.screen.blit(label, ((self.screen.get_size()[0]-label.get_size()[0])/4,0) )

            label = self.font_b.render("seconds", 1, (255, 255, 255))
            self.screen.blit(label, ((self.screen.get_size()[0]-label.get_size()[0])/2,0) )


            label = self.font_b.render("OK", 1, (255, 255, 255))
            pos_x=self.screen.get_size()[0]-label.get_size()[0]
            pos_y=0

            if rects_ok == False:
                rect_valide = label.get_rect()
                rect_valide[0]=pos_x
                rect_valide[1]=pos_y
            if minutes_id!=-1 and secondes_id!=-1:
                self.screen.blit(label, (pos_x,pos_y) )


            pos_y=0
            for i in list_minutes:
                if i == minutes_id:
                    label = self.font_c.render("-> "+str(i)+" <-", 1, (255, 255, 255))

                elif i ==rects_minutes_over:
                    label = self.font_c.render("   "+str(i)+"   ", 1, (255, 255, 255))
                else:
                    label = self.font_c.render("   "+str(i)+"   ", 1, (125, 125, 125))
                pos_y+=label.get_size()[1]
                pos_x=(self.screen.get_size()[0]-label.get_size()[0])/4

                if rects_ok == False:
                    rect_tmp = label.get_rect()
                    rect_tmp[0]=pos_x
                    rect_tmp[1]=pos_y
                    rects_minutes.append(rect_tmp)
                self.screen.blit(label, (pos_x,pos_y) )


            pos_y=0
            pos_x=(self.screen.get_size()[0]-label.get_size()[0])/2
            for i in list_secondes:
                if i == secondes_id:
                    label = self.font_c.render("-> "+str(i)+" <-", 1, (255, 255, 255))
                elif i ==rects_secondes_over:
                    label = self.font_c.render("   "+str(i)+"   ", 1, (255, 255, 255))
                else:
                    label = self.font_c.render("   "+str(i)+"   ", 1, (125, 125, 125))
                pos_y+=label.get_size()[1]


                if i==16 or i==31 or i==46:
                    pos_x+=label.get_size()[0]*2
                    pos_y=label.get_size()[1]
                if rects_ok == False:
                    rect_tmp = label.get_rect()
                    rect_tmp[0]=pos_x
                    rect_tmp[1]=pos_y
                    rects_secondes.append(rect_tmp)
                self.screen.blit(label, (pos_x,pos_y) )


            rects_ok=True


            pygame.display.flip()

            event = pygame.event.poll()
            cursor = pygame.mouse.get_pos()
            rects_minutes_over = -1
            for idrect, rect in enumerate(rects_minutes):
                if rect.collidepoint(cursor):
                    rects_minutes_over = idrect
            for idrect, rect in enumerate(rects_secondes):
                if rect.collidepoint(cursor):
                    rects_secondes_over = idrect

            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                for idrect, rect in enumerate(rects_minutes):
                    if rect.collidepoint(cursor):
                        minutes_id = idrect
                for idrect, rect in enumerate(rects_secondes):
                    if rect.collidepoint(cursor):
                        secondes_id = idrect
                if rect_valide.collidepoint(cursor):
                    return str(list_minutes[minutes_id])+";"+str(list_secondes[secondes_id])

def _T(valeur):
        return valeur



class participant(QtGui.QDialog):
    def __init__(self, parent, id_sujet):
        QtGui.QDialog.__init__(self, parent)


        self.id_sujet=id_sujet


        self.scenario = QtGui.QLabel(_T(u'scenario'))
        self.firstname = QtGui.QLabel(_T(u'Your firstname'))
        self.birthdate = QtGui.QLabel(_T(u'Your birth date (dd/mm/yyyy)'))
        self.phonenumber = QtGui.QLabel(_T(u'Last 4 numbers of your phone number'))
        self.man = QtGui.QCheckBox(_T(u'Man'))
        self.woman= QtGui.QCheckBox(_T(u'Woman'))

        self.firstnameEdit = QtGui.QLineEdit()
        self.birthdateEdit = QtGui.QLineEdit()
        self.phonenumberEdit = QtGui.QLineEdit()
        self.scenarioEdit = QtGui.QLineEdit()
        self.okButton = QtGui.QPushButton(_T("Continue"))

        self.okButton.clicked.connect(self.userValidation)
        self.man.clicked.connect(self.setParticipantToMan)
        self.woman.clicked.connect(self.setParticipantToWoman)
        grid = QtGui.QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(self.firstname, 1, 0)
        grid.addWidget(self.firstnameEdit, 1, 1)

        grid.addWidget(self.birthdate, 2, 0)
        grid.addWidget(self.birthdateEdit, 2, 1)

        grid.addWidget(self.phonenumber, 3, 0)
        grid.addWidget(self.phonenumberEdit, 3, 1)


        grid.addWidget(self.man, 4,1)
        grid.addWidget(self.woman, 5,1)

        grid.addWidget(self.scenario, 6, 0)
        grid.addWidget(self.scenarioEdit, 6, 1)

        grid.addWidget(self.okButton, 8,0,8,2)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle(_T('Informations'))

        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

        self.start_time = time.clock()
        self.show()



    def setParticipantToMan(self):
        if self.woman.isChecked()==True:
            self.woman.toggle()

    def setParticipantToWoman(self):
        if self.man.isChecked()==True:
            self.man.toggle()

    def getFolderName(self):
        string = self.birthdateEdit.text()+"-"+self.firstnameEdit.text()+"-"+str(self.phonenumberEdit.text())
        return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')


    def userValidation(self):
        if self.firstnameEdit.text()=="":
            reply = QtGui.QMessageBox.information(self, _T("Warning"), _T(u"Don't forget to write your firstname"))
            return
        if self.birthdateEdit.text()=="":
            reply = QtGui.QMessageBox.information(self, _T("Attention"), _T(u"Dont forget to write your birthdate"))
            return
        if self.phonenumberEdit.text()=="":
            reply = QtGui.QMessageBox.information(self, _T("Attention"), _T(u"Dont forget to write your phone number"))
            return
        if self.scenarioEdit.text()=="":
            reply = QtGui.QMessageBox.information(self, _T("Attention"), _T(u"The scenario must be set (ask to the experimenter) !"))
            return
        if not self.man.isChecked() and not self.woman.isChecked():
            reply = QtGui.QMessageBox.information(self, _T("Attention"), _T(u"Don't forget to check man ou woman"))
            return


        if self.scenarioEdit.text().lower() not in scenarios.keys():
            reply = QtGui.QMessageBox.information(self, _T("Attention"), _T(u"This scenario is not known (ask to the experimenter)"))
            return


        heure = str(time.clock() - self.start_time)
        f = codecs.open(os.path.join("results", str(self.id_sujet), 'participant.txt'),'w', "utf-8-sig")
        f.write(heure+";firstname:;"+self.firstnameEdit.text()+"\r\n")
        f.write(heure+";birthdate:;"+self.birthdateEdit.text()+"\r\n")
        phone = ''.join(c for c in self.phonenumberEdit.text() if c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        f.write(heure+";phone:;"+phone+"\r\n")
        if phone!=self.phonenumberEdit.text():
            f.write(heure+";phone-set:;"+self.phonenumberEdit.text()+"\r\n")
        if self.man.isChecked()==True:
            self.sexe="M"
            f.write(heure+";sex:;M"+"\r\n")
        else:
            self.sexe="F"
            f.write(heure+";sex:;W"+"\r\n")
        f.close()

        f = open(os.path.join("results", str(self.id_sujet),'scenario.txt'), 'w')
        f.write(self.scenarioEdit.text().lower())
        f.close()

        self.accept()

    def getScenario(self):
        return self.scenarioEdit.text().lower()

    def getParticipantLine(self):
        phone = ''.join(c for c in self.phonenumberEdit.text() if c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        if self.man.isChecked()==True:
            sexe="M"
        else:
            sexe="W"
        return self.firstnameEdit.text()+";"+self.birthdateEdit.text()+";"+str(phone)+";"+sexe+";"



class instruction(QtGui.QDialog):
    def __init__(self, parent, fichier_instruction, id_sujet):
        QtGui.QDialog.__init__(self, parent)

        self.current_question = 0

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.id_sujet=id_sujet

        self.font = QtGui.QFont('Serif', 13, QtGui.QFont.Light)

        instruction=""
        if os.path.exists(os.path.join(os.getcwd(), 'res', fichier_instruction)):
            f = open(os.path.join(os.getcwd(), 'res', fichier_instruction), 'r')
            for tmp in f:
                instruction+=tmp
            f.close()



        self.setLayout(QtGui.QVBoxLayout())


        self.centralhbox=QtGui.QHBoxLayout()
        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/4))
        self.centralhbox.addWidget(b)

        self.instruction = QtGui.QLabel(instruction)
        self.instruction.setFont(self.font)
        self.instruction.setWordWrap(True)
        self.instruction.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignJustify)
        self.centralhbox.addWidget(self.instruction)


        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/4))
        self.centralhbox.addWidget(b)

        self.layout().addLayout(self.centralhbox)



        hbox=QtGui.QHBoxLayout()

        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/3))
        hbox.addWidget(b)

        btn = QtGui.QPushButton(_T(" Continue "))
        btn.setFont(self.font)
        hbox.addWidget(btn)

        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/3))
        hbox.addWidget(b)
        self.layout().addLayout(hbox)

        self.start_time = time.clock()
        self.connect(btn, QtCore.SIGNAL("clicked()"), self.saveresults)


    def saveresults(self):
        self.accept()



class mySlider(QtGui.QSlider):
    def __init__(self, orientation, parent, list):
        self.opt = QtGui.QStyleOptionSlider()
        QtGui.QSlider.__init__(self, orientation)

        self.list = list
        self.opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(self.opt)

        self.listcoord=[]
        self.valueChanged.connect(self._valueChanged)
        self.valeur=-1


    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        return QtCore.QSize(218, 70)


    def paintEvent(self, pe):
        p = QtGui.QPainter(self)

        self.initStyleOption(self.opt)
        center = self.opt.rect.center()

        grooveRect = self.style().subControlRect(QtGui.QStyle.CC_Slider, self.opt, QtGui.QStyle.SC_SliderGroove, self)
        handleRect = self.style().subControlRect(QtGui.QStyle.CC_Slider, self.opt, QtGui.QStyle.SC_SliderHandle, self)
        taille = (grooveRect.width()-handleRect.width())/(len(self.list))


        height =grooveRect.height()*0.50


        rect = QtCore.QRect(0, height/2, self.opt.rect.width(), 1).adjusted((taille/2)+6, 0, -(taille/2)-10, 0)

        p.setPen(QtGui.QPen(QtCore.Qt.black))
        p.drawRect(rect)
        p.setBrush(QtGui.QColor(0, 0, 0))
        p.drawRect(handleRect.adjusted(0, 0, -1, -height))



        self.listcoord=[]

        for i in range(0, len(self.list)):
            rect = QtCore.QRect(i*taille+handleRect.width()/2+(taille/2), 0, 1, height) # draw tick
            p.drawRect(rect)
            p.drawText(i*taille+6,grooveRect.height()*0.55, taille, height, QtCore.Qt.AlignHCenter|QtCore.Qt.TextWordWrap, self.list[i])
            self.listcoord.append((i*taille+6)*100/self.width())

        p.end()


    def _valueChanged(self, value):
        for i, tmp in enumerate(self.listcoord):
            if value<self.listcoord[1]/2:
                tmp=(self.listcoord[1])/2
                self.setValue(tmp)
                self.valeur = 0
                break
            elif i==len(self.listcoord)-1:
                self.valeur = len(self.listcoord)-1

                max=(99-self.listcoord[len(self.listcoord)-1])/2+self.listcoord[len(self.listcoord)-1]
                self.setValue(max)
                break
            else:
                if value>=self.listcoord[i] and value<self.listcoord[i+1]:
                    tmp=(self.listcoord[i+1]-self.listcoord[i])/2+self.listcoord[i]
                    self.setValue(tmp)
                    self.valeur = i
                    break


    def mouseReleaseEvent(self, event):
        value = event.x()*100/self.width()
        self._valueChanged(value)
        event.accept()


class scales(QtGui.QDialog):
    def __init__(self, parent, dossier, id_sujet):
        QtGui.QDialog.__init__(self, parent)

        self.current_question = 0

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.id_sujet=id_sujet
        self.dossier=dossier


        self.font = QtGui.QFont('Serif', 13, QtGui.QFont.Light)

        instruction=""
        if os.path.exists(os.path.join(os.getcwd(), 'res', dossier, 'instruction.txt')):
            f = open(os.path.join(os.getcwd(), 'res', dossier, 'instruction.txt'), 'r')
            for tmp in f:
                tmp = unicode(tmp, "utf-8")
                instruction+=tmp
            f.close()


        self.graduations=[]
        f = open(os.path.join(os.getcwd(), 'res', dossier, 'graduations.txt'), 'r')
        for tmp in f:
            tmp = unicode(tmp, "utf-8")
            self.graduations.append(tmp.strip("\r\n"))
        f.close()


        self.setLayout(QtGui.QVBoxLayout())


        self.centralhbox=QtGui.QHBoxLayout()
        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/4))
        self.centralhbox.addWidget(b)

        self.instruction = QtGui.QLabel(instruction)
        self.instruction.setFont(self.font)
        self.instruction.setWordWrap(True)
        self.centralhbox.addWidget(self.instruction)


        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/4))
        self.centralhbox.addWidget(b)

        self.layout().addLayout(self.centralhbox)



        hbox=QtGui.QHBoxLayout()

        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/3))
        hbox.addWidget(b)

        btn = QtGui.QPushButton(_T(" Continue "))
        btn.setFont(self.font)
        hbox.addWidget(btn)

        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/3))
        hbox.addWidget(b)
        self.layout().addLayout(hbox)


        self.reponses = []
        self.reponsesvaleurs = []
        self.connect(btn, QtCore.SIGNAL("clicked()"), self.affichequestionsuivante)


        self.start_time = time.clock()

        if len(instruction.strip())==0:
            self.affichequestionsuivante()

    def deleteItems(self, layout):
     if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.deleteLater()
             else:
                 self.deleteItems(item.layout())


    def affichequestionsuivante(self):
        if self.current_question>0:

            if self.slider.valeur==-1:
                reply = QtGui.QMessageBox.information(self, _T("Warning"), _T(u"Don't forget to enter a value"))
                return


            heure = str(time.clock() - self.start_time)
            ligne = heure+";"+(self.instruction).replace("\r\n", "")+";"+str(self.slider.valeur+1).replace("\r\n", "")+";"+(self.graduations[self.slider.valeur])
            self.reponses.append(ligne)
            self.reponsesvaleurs.append(self.slider.valeur+1)


        screen = QtGui.QDesktopWidget().screenGeometry()
        self.current_question+=1


        fichier = os.path.join(os.getcwd(), 'res', self.dossier, 'question'+str(self.current_question)+'.txt')
        if not os.path.exists(fichier):
            self.saveresults()
            return




        self.instruction=""
        f = open(fichier, 'r')
        for tmp in f:
            self.instruction+= unicode(tmp, "utf-8")



        self.deleteItems(self.centralhbox)



        self.centralhbox=QtGui.QHBoxLayout()




        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/4))
        self.centralhbox.addWidget(b)

        vbox=QtGui.QVBoxLayout()

        b=QtGui.QLabel(" ")
        b.setMinimumHeight(screen.height()/5)
        vbox.addWidget(b)

        b=QtGui.QLabel(self.instruction)
        b.setFont(self.font)
        b.setWordWrap(True)
        vbox.addWidget(b)

        hbox=QtGui.QHBoxLayout()



        self.slider=mySlider(QtCore.Qt.Horizontal, self, self.graduations) #QtGui.QSlider(QtCore.Qt.Horizontal, self)
        hbox.addWidget(self.slider)
##        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
##        self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)
##        self.slider.setTickInterval(1)
##        self.slider.setSingleStep(1)
##        self.slider.setMinimum(1)
##        self.slider.setMaximum(len(self.graduations))



        vbox.addLayout(hbox)





        vbox.stretch(1)


        self.centralhbox.addLayout(vbox)

        b=QtGui.QLabel(" ")
        b.setMinimumWidth((screen.width()/4))
        self.centralhbox.addWidget(b)


        b=QtGui.QLabel(" ")
        b.setMinimumWidth(screen.width()/25)
        self.centralhbox.addWidget(b)

        self.layout().insertLayout(0, self.centralhbox)




    def saveresults(self):
        #print "save"
        f = codecs.open(os.path.join("results", str(self.id_sujet), 'echelle_'+self.dossier+'.txt'),'w', "utf-8-sig")
        f.write(u"0;nb questions:;"+str(self.current_question-1)+"\r\n")
        for tmp in self.reponses:
            f.write(tmp+"\r\n")
        f.close()
        self.accept()


    def returnligneechelle(self):
        tmp = ""
        for i in self.reponsesvaleurs:
            tmp+=str(i)+";"
        return tmp



if __name__ == '__main__':

    if not os.path.exists("results"):
        os.makedirs("results")

    id_sujet=1

    trouvesujet=False
    while (trouvesujet==False):
        if os.path.exists(os.path.join("results", str(id_sujet))):
            id_sujet+=1
        else:
            os.makedirs(os.path.join("results", str(id_sujet)))
            trouvesujet=True



    app = QtGui.QApplication(sys.argv)

    mode_debug_labyrinthe = '' #Long-2A.txt'# 'short-training-3.txt'

    if mode_debug_labyrinthe!='':
        partie(mode_debug_labyrinthe, 'A', 1)
        sys.exit(1)


    tmp = participant(None, id_sujet)
    tmp.show()
    app.exec_()
    scenario = tmp.getScenario()
    ligneparticipant = tmp.getParticipantLine()

    if scenario=='':
        scenario='A'


    reply = QtGui.QMessageBox.No
    while reply == QtGui.QMessageBox.No:
        tmp = instruction(None, "instruction_before_training_"+scenario+".txt", id_sujet)
        tmp.showFullScreen()
        app.exec_()

        tmplist = []
        fz = open (os.path.join('res', '_listtrainingfiles.txt'))
        for tmp in fz:
                if len(tmp.strip())>0:
                    if os.path.isfile(os.path.join('res',tmp.strip("\n"))):
                        tmplist.append(tmp.strip("\n"))
                    else:
                        print "ERROR. File "+tmp+" NOT FOUND!"
        fz.close()

        #training 1
        choix = random.choice(tmplist)
        tmplist.remove(choix)
        partie(choix, scenario, id_sujet)

        #training 2
        choix = random.choice(tmplist)
        partie(choix, scenario, id_sujet)

        reply = QtGui.QMessageBox.question(None, 'Training', u"Did you understand how to play this game?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)



    tmp = instruction(None, "instruction_before_scenario_"+scenario+".txt", id_sujet)
    tmp.showFullScreen()
    app.exec_()


    tmplist = []
    fz = open (os.path.join('res', '_listscenariosfiles.txt'))
    for tmp in fz:
            if len(tmp.strip())>0:
                tmplist.append(tmp.strip("\n"))

    fz.close()


    choix = random.choice(tmplist)


    tmplist = choix.split('/')




    for lab in tmplist:
        if not os.path.isfile(os.path.join('res',lab.strip("\n"))):
            print "ERROR. File "+lab+" not found"
        else:
            partie(lab, scenario, id_sujet)

    QtGui.QMessageBox.information(None, 'End', u"The game is now finished! Thank you for your contribution.", QtGui.QMessageBox.Ok)


    legende = "firstname;birthday;phone;sex"
    nomfichier = os.path.join('results', str(id_sujet))+"/results"
    fa = open(nomfichier+"tmp.csv", 'r')
    fz = open(nomfichier+".csv", 'a')
    fz.write(legende+";"+"subject_id;scenario;maze_filename;task_type;pressure_type (1=with 0=without);dial_type (1=dial 0=ghost);duration_type;fail_type (1=yes 0=no);total_time;time_estimation_min;time_estimation_sec;production_time;time_by_case;nb_keys;average_ghost_distance\n")

    for k in fa:
        fz.write(ligneparticipant+k.strip("\n")+"\n")
    fa.close()
    fz.close()
