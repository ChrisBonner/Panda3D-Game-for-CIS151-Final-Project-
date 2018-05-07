##from pandac.PandaModules import loadPrcFileData
##loadPrcFileData("", "want-directtools #t")
##loadPrcFileData("", "want-tk #t")

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.interval.IntervalGlobal import LerpFunc
from direct.gui.OnscreenImage import OnscreenImage
from libpandaai import *
import sys, os

SCAR_POS = (-3.75,1.6,-.3)
SCAR_HPR = (5, -90, 0)
M4_POS = (.25, 1.75,-.3)
M4_HPR = (5,-85,0)
SHOTGUN_POS = (.25, 1.80,-.3)
SHOTGUN_HPR = (180,0,0)
RIFLE_SCALE = (1,1,1)
USP45_POS = (.25, 1.80,-.3)
USP45_HPR = (185,-5,0)
PISTOL_SCALE = (1.5,1.5,1.5)

class FPS(object,DirectObject):
    def __init__(self):
        self.winXhalf = base.win.getXSize()/2
        self.winYhalf = base.win.getYSize()/2
        winprops=WindowProperties()
        winprops.setCursorHidden(True)      
        base.win.requestProperties(winprops)
        self.model = loader.loadModel('models/Guns/45.x')
        self.model.reparentTo(base.camera)
        self.model.setPos(USP45_POS)
        self.model.setHpr(USP45_HPR)
        self.model.setScale(PISTOL_SCALE)
        self.gun = 1
        
        self.initSound()
        self.initCollision()
        self.loadLevel()
        self.initPlayer()
        self.setupMouseCollision()
        self.loadCrosshairs()
        self.loadRalph()
        
        
    def initSound(self):
        self.deathSnd = base.loader.loadSfx("models/sounds/and.ogg")
        self.spawnSnd = base.loader.loadSfx("models/sounds/faster.ogg")
        self.fireSnd = base.loader.loadSfx("models/sounds/rifle.ogg")
        
    def loadCrosshairs(self): 
        self.crosshairs = OnscreenImage(image = 'models/crosshair.png', pos = base.win.getPointer(0))
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        self.crosshairs.setScale(.04,.04,.04)

    def initCollision(self):    
        #initialize traverser
        base.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)
        base.cTrav.showCollisions(render)
        self.mPicker = CollisionTraverser()
        self.mPicker.showCollisions(render)
        self.mCQue = CollisionHandlerQueue()
#         base.cTrav.showCollisions(render)
        #initialize pusher
        self.pusher = CollisionHandlerPusher()
        # collision bits
        self.groundCollBit = BitMask32.bit(0)
        self.collBitOff = BitMask32.allOff()
        self.zombieColBitFrom = BitMask32.bit(2)
        self.zombieColBitInto = BitMask32.bit(2)
        self.zombieColBitOff = BitMask32.allOff()

    def loadLevel(self):

        self.level = loader.loadModel('models/world')
        self.level.reparentTo(render)
        self.level.setPos(0,0,0)
        self.level.setColor(1,1,1,.5)
        self.level.setCollideMask(self.groundCollBit)
        
        self.box = loader.loadModel("models/box")  
        self.box.reparentTo(render)
        self.box.setPos(-29.83,0,0)
        self.box.setScale(1)
        self.box.setCollideMask(self.groundCollBit)
        self.box1 = loader.loadModel("models/box")  
        self.box1.reparentTo(render)
        self.box1.setPos(-51.14,-17.90,0)
        self.box1.setScale(1)
        self.box1.setCollideMask(self.groundCollBit)

    def loadRalph(self):
        ralphStartPos = Vec3(-98.64,-20.60,0)
        self.ralph = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setPos(ralphStartPos)
        self.ralph.setScale(.3)
        self.ralphLife = 10
        ralphaiStartPos = Vec3(-50,20,0)
        self.ralphai = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)
        
        self.ralphHeadSphere = CollisionSphere(0,-.2,4.5,.7)
        self.ralphHeadCol = CollisionNode('ralphHeadColSphere')
        self.ralphHeadCol.addSolid(self.ralphHeadSphere)
        self.ralphHeadCol.setFromCollideMask(self.zombieColBitFrom)
        self.ralphHeadCol.setIntoCollideMask(self.zombieColBitInto)
        self.ralphHeadColNp = self.ralph.attachNewNode(self.ralphHeadCol)
        self.mPicker.addCollider(self.ralphHeadColNp, self.mCQue)
        
        self.ralphBodySphere = CollisionSphere(0,-.2,2,1)
        self.ralphBodyCol = CollisionNode('ralphBodyColSphere')
        self.ralphBodyCol.addSolid(self.ralphBodySphere)
        self.ralphBodyCol.setFromCollideMask(self.zombieColBitFrom)
        self.ralphBodyCol.setIntoCollideMask(self.zombieColBitInto)
        self.ralphBodyColNp = self.ralph.attachNewNode(self.ralphBodyCol)
        self.mPicker.addCollider(self.ralphBodyColNp, self.mCQue)
        self.ralphHeadColNp.show()
        self.ralphBodyColNp.show()
        
        base.taskMgr.doMethodLater(.7,self.spawnSound,"spawnSound")
        self.isMoving = False
        self.setAI()
        
    def spawnSound(self, task):
        self.spawnSnd.play()
        return task.done

    def Scar(self):
        self.model.removeNode()        
        self.model = loader.loadModel('models/Guns/SCAR.x')
        self.model.reparentTo(base.camera)
        self.model.setPos(SCAR_POS)
        self.model.setHpr(SCAR_HPR)
        self.model.setScale(RIFLE_SCALE)
        self.gun = 4
        
    def M4(self):
        self.model.removeNode()
        self.model = loader.loadModel('models/Guns/M4.x')
        self.model.reparentTo(base.camera)
        self.model.setPos(M4_POS)
        self.model.setHpr(M4_HPR)
        self.model.setScale(RIFLE_SCALE)
        self.gun = 3
        
    def Shotgun(self):
        self.model.removeNode()
        self.model = loader.loadModel('models/Guns/Shotgun.x')
        self.model.reparentTo(base.camera)
        self.model.setPos(SHOTGUN_POS)
        self.model.setHpr(SHOTGUN_HPR)
        self.model.setScale(RIFLE_SCALE)
        self.gun = 2
           
    def Pistol(self):
        self.model.removeNode()
        self.model = loader.loadModel('models/Guns/45.x')
        self.model.reparentTo(base.camera)
        self.model.setPos(USP45_POS)
        self.model.setHpr(USP45_HPR)
        self.model.setScale(PISTOL_SCALE)
        self.gun = 1
        
    def setupMouseCollision(self):
        
        self.mRay = CollisionRay()
        self.mRayNode = CollisionNode('pickRay')
        self.mRayNode.addSolid(self.mRay)
        self.mRayNode.setFromCollideMask(self.zombieColBitFrom)
        self.mRayNode.setIntoCollideMask(self.zombieColBitOff)
        self.mPickNp = base.camera.attachNewNode(self.mRayNode)
        self.mPicker.addCollider(self.mPickNp, self.mCQue)

        self.mPickNp.show()
        
    def initPlayer(self):
        #load man
        self.man = render.attachNewNode('man') # keep this node scaled to identity
        self.man.setPos(0,0,10)

        # camera
        base.camera.reparentTo(self.man)
        base.camera.setPos(0,0,1.7)
        base.camLens.setNearFar(.1,1000)
        base.disableMouse()
        #create a collsion solid around the man
        manC = self.man.attachCollisionSphere('manSphere', 0,0,1, .4, self.groundCollBit,self.collBitOff)
        self.pusher.addCollider(manC,self.man)
        base.cTrav.addCollider(manC,self.pusher)

        speed = 4
        Forward = Vec3(0,speed*2,0)
        Back = Vec3(0,-speed,0)
        Left = Vec3(-speed,0,0)
        Right = Vec3(speed,0,0)
        Stop = Vec3(0)
        self.walk = Stop
        self.strife = Stop
        self.jump = 0
        taskMgr.add(self.move, 'move-task')
        self.jumping = LerpFunc( Functor(self.__setattr__,"jump"),
                                 duration=.5, fromData=.4, toData=0)

        self.accept( "escape",sys.exit )
        self.accept( "space" , self.startJump)
        self.accept( "s" , self.__setattr__,["walk",Back] )
        self.accept( "w" , self.__setattr__,["walk",Forward])
        self.accept( "s-up" , self.__setattr__,["walk",Stop] )
        self.accept( "w-up" , self.__setattr__,["walk",Stop] )
        self.accept( "a" , self.__setattr__,["strife",Left])
        self.accept( "d" , self.__setattr__,["strife",Right] )
        self.accept( "a-up" , self.__setattr__,["strife",Stop] )
        self.accept( "d-up" , self.__setattr__,["strife",Stop] )
        self.accept( "wheel_up", self.nextWeapon)
        self.accept( "wheel_down", self.prevWeapon)
        self.accept( "1", self.Pistol)
        self.accept( "2", self.Shotgun)
        self.accept( "3", self.M4)
        self.accept( "4", self.Scar)
        self.accept('mouse1', self.onMouseTask)
        #add mouse collision to our world
        self.setupMouseCollision()
        self.manGroundColNp = self.man.attachCollisionRay( 'manRay',
                                                           0,0,.6, 0,0,-1,
                                                           self.groundCollBit,self.collBitOff)
        self.manGroundHandler = CollisionHandlerGravity()
        self.manGroundHandler.addCollider(self.manGroundColNp,self.man)
        base.cTrav.addCollider(self.manGroundColNp, self.manGroundHandler)
        
        
    def nextWeapon(self):
        if self.gun == 1:
            self.Shotgun()
        elif self.gun == 2:
            self.M4()
        elif self.gun == 3:
            self.Scar()
        elif self.gun == 4:
            self.Pistol()
        
    def prevWeapon(self):
        if self.gun == 1:
            self.Scar()
        elif self.gun == 2:
            self.Pistol()
        elif self.gun == 3:
            self.Shotgun()
        elif self.gun == 4:
            self.M4()
            
    def startJump(self):
        if self.manGroundHandler.isOnGround():
           self.jumping.start()

    def move(self,task):
        dt=globalClock.getDt()
        # mouse
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, self.winXhalf, self.winYhalf):
            self.man.setH(self.man, (x - self.winXhalf)*-0.1)
            base.camera.setP( clampScalar(-90,90, base.camera.getP() - (y - self.winYhalf)*0.1) )
        # move where the keys set it
        moveVec=(self.walk+self.strife)*dt # horisontal
        moveVec.setZ( self.jump )          # vertical
        self.man.setFluidPos(self.man,moveVec)
        # jump damping
        if self.jump>0:
           self.jump = clampScalar( 0,1, self.jump*.9 )
        
        return task.cont
    
    def onMouseTask(self):

        mpos = base.mouseWatcherNode.getMouse()
        self.mRay.setDirection(render.getRelativeVector(camera, Vec3(0,1,0)))
        self.mRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
        self.mPicker.traverse(render)
        self.fireSnd.play()
        entries = []
        for i in range(self.mCQue.getNumEntries()):
            entry = self.mCQue.getEntry(i)
            print entry
            entries.append(entry)
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == 'terrain'):
           print 'terrain'
        
        entries = []
        for i in range(self.mCQue.getNumEntries()):
            entry = self.mCQue.getEntry(i)
            print entry
            entries.append(entry)
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == 'ralphHeadColSphere'):
            self.ralphLife -= 10
            base.taskMgr.doMethodLater(.3,self.deathSound,"deathSound")
            
        entries = []
        for i in range(self.mCQue.getNumEntries()):
            entry = self.mCQue.getEntry(i)
            print entry
            entries.append(entry)
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == 'ralphBodyColSphere'):
            self.ralphLife -= 5
            if self.ralphLife < 5:
                base.taskMgr.doMethodLater(.3,self.deathSound,"deathSound")
        
        if self.ralphLife <= 0:
            self.ralph.cleanup()
            self.ralphai.cleanup()
            self.loadRalph()
            
    def deathSound(self, task):
        self.deathSnd.play()
        return task.done

    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
        self.AIchar = AICharacter("ralph",self.ralph, 130, 0.05, 25)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
        
        self.AIbehaviors.initPathFind("models/navmesh.csv")
        self.setMove()
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
        
    def setMove(self):
        self.AIbehaviors.addStaticObstacle(self.box)
        self.AIbehaviors.addStaticObstacle(self.box1)
        self.AIbehaviors.pathFindTo(self.man)
        self.ralph.loop("run")
    
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.AIworld.update()
        self.ralphMove()

        return Task.cont

    def ralphMove(self):

        startpos = self.ralph.getPos()

        # Now check for collisions.

        self.cTrav.traverse(render)

        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)

        self.ralph.setP(0)
        return Task.cont
FPS()
render.setShaderAuto()
run()