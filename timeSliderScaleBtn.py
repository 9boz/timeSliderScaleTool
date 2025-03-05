import maya.cmds as cmds
from PySide2 import QtWidgets,QtGui,QtCore
import math

def resetTimeSlider(scaledStart,scaledEnd):

    startLimit = cmds.playbackOptions(q = True, animationStartTime =True)
    endLimit = cmds.playbackOptions(q = True, animationEndTime=True)
    
    curStartTime = cmds.playbackOptions(q = True, min =True)
    curEndTime = cmds.playbackOptions(q = True, max =True)

    if scaledStart == None or scaledEnd == None:
        cmds.playbackOptions(min = startLimit, max = endLimit)
        return curStartTime,curEndTime
    
    elif curStartTime == startLimit and curEndTime == endLimit:
        cmds.playbackOptions(min = scaledStart, max = scaledEnd)
        return scaledStart,scaledEnd
    
    else:
        cmds.playbackOptions(min = startLimit, max = endLimit)
        return curStartTime,curEndTime
        
def scaleTimeSlider(wheelDelta):
    currentTime = cmds.currentTime(q = True)

    startLimit = cmds.playbackOptions(q = True, animationStartTime =True)
    endLimit = cmds.playbackOptions(q = True, animationEndTime=True)
    
    newStartTime = cmds.playbackOptions(q = True, min =True)
    newEndTime = cmds.playbackOptions(q = True, max =True)
    
    startSideRange = (currentTime - newStartTime)
    endSideRange = (newEndTime - currentTime)    
    scaleFactor =  abs(wheelDelta) * 0.01    

    if wheelDelta > 0:                
        newStartTime = math.floor(currentTime - startSideRange * scaleFactor)        
        newEndTime = math.ceil(currentTime + endSideRange * scaleFactor)
    else:
        newStartTime = math.floor(currentTime - startSideRange / scaleFactor)        
        newEndTime = math.ceil(currentTime + endSideRange / scaleFactor)
    
    if newStartTime == currentTime:
        newStartTime = currentTime - 1
    
    if newEndTime == currentTime:
        newEndTime = newEndTime + 1

    newStartTime = max(int(newStartTime),startLimit)
    newEndTime = min(int(newEndTime),endLimit)
        
    cmds.playbackOptions(min = newStartTime, max = newEndTime)

    return newStartTime, newEndTime


def templateExtendTimeSlider(expandFrame):
    currentTime = cmds.currentTime(q = True)
    startLimit = cmds.playbackOptions(q = True, animationStartTime =True)
    endLimit = cmds.playbackOptions(q = True, animationEndTime=True)
    
    newStartTime = currentTime + 1 - (expandFrame / 2)
    newEndTime = currentTime + (expandFrame / 2)
    
    offset = 0
    if newStartTime < startLimit:
        offset = startLimit - newStartTime

    elif newEndTime > endLimit:
        offset = endLimit - newEndTime
        
    newStartTime = newStartTime + offset
    newEndTime = newEndTime + offset
    
    resetTimeSlider(newStartTime,newEndTime)

    return newStartTime, newEndTime

##-----------------------------------------------------------------
def getTopLevelWidget(name):
    for widget in QtWidgets.QApplication.topLevelWidgets():    
        if widget.objectName() == name:
            return widget
    return None


def windowCheck(object,parent,arrowMulti = False):
    
    if arrowMulti:        
        allChildrenName = []
        renameObject = str(object)

        for child in parent.children():
            allChildrenName.append(child.objectName())
        
        i = 1
        
        while renameObject in allChildrenName:
            renameObject = object + str(i)
            i = i+1
                
        return renameObject
            
    else:
        for child in parent.children():
            if child.objectName() == object:
                child.deleteLater()

        return object


class ApplyFunc(object):
    def __init__(self, func, *args, **kwargs):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
                        
    def __call__(self, *args, **kwargs):
        error = None        
        try:            
            cmds.undoInfo(openChunk =True)

            self.__func(*self.__args, **self.__kwargs)			
                        
        except Exception as e:
            import traceback
            traceback.print_exc()

        finally:
            cmds.undoInfo(closeChunk =True)


class TimeScaleBtn(QtWidgets.QPushButton):
    def __init__(self,parent,*args , **kwargs):
        super(TimeScaleBtn,self).__init__(*args)

        self.clicked.connect(self.toggleTimeRange)
        self.parent = parent    
        
        self.clickPoint = None
        self.pastPoint = None
        

    def wheelEvent(self, event):
        wheelAngle = event.angleDelta().y()
        self.scaledStartTime,self.scaledEndTime = scaleTimeSlider(wheelAngle)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.clickPoint = event.pos()
            self.pastPoint = event.pos()
            self.parent.curStartTime = cmds.playbackOptions(q = True, min =True)
            self.parent.curEndTime = cmds.playbackOptions(q = True, max =True)
        else:
            super(TimeScaleBtn, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.clickPoint != None:
            delta = event.pos() - self.pastPoint
            offset = (abs(delta.x())//10)

            if offset != 0:
                if delta.x() > 0:
                    offset = offset * -1

                self.parent.scaledStartTime,self.parent.scaledEndTime = scaleTimeSlider(120*offset)
                self.pastPoint = event.pos()
        else:
            super(TimeScaleBtn, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.clickPoint = None
        else:
            super(TimeScaleBtn, self).mouseReleaseEvent(event)

    def toggleTimeRange(self):        
        self.parent.scaledStartTime,self.parent.scaledEndTime = resetTimeSlider(self.parent.scaledStartTime,self.parent.scaledEndTime)

class TimeSettingDialog(QtWidgets.QDialog):
    def __init__(self,curValue,*args, **kwargs):
        super(TimeSettingDialog,self).__init__(*args,**kwargs)
        self.setValue = curValue
        mainLayout = QtWidgets.QVBoxLayout(self)

        self.inputFld = QtWidgets.QSpinBox()
        self.inputFld.setMinimum(1)
        self.inputFld.setMaximum(9999)
        self.inputFld.setSingleStep(1)
        self.inputFld.setValue(curValue)

        mainLayout.addWidget(self.inputFld)

        cmdLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(cmdLayout)

        applyBtn = QtWidgets.QPushButton("set")
        applyBtn.setFixedSize(80,20)
        cmdLayout.addWidget(applyBtn)
        applyBtn.clicked.connect(self.apply)

        cancelBtn = QtWidgets.QPushButton("cancel")
        cancelBtn.setFixedSize(80,20)
        cmdLayout.addWidget(cancelBtn)
        cancelBtn.clicked.connect(self.reject)

    def apply(self):
        self.setValue = self.inputFld.value()
        self.accept()


class TimeExpandBtn(QtWidgets.QPushButton):
    
    def __init__(self,parent,*args, **kwargs):
        super(TimeExpandBtn,self).__init__(*args,**kwargs)        
        self.btnDict = {}
        self.parent = parent

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.createTempalteRangeMenu(event)
        else:
            super(TimeExpandBtn, self).mouseReleaseEvent(event)

    def createTempalteRangeMenu(self,event):        
        bookMarkMenu = QtWidgets.QMenu()
        Act = QtWidgets.QAction("expandFrame setting")
        bookMarkMenu.addAction(Act)
        Act.triggered.connect(self.parent.editFrameExpandValue)
        bookMarkMenu.exec_(self.mapToGlobal(event.pos()))

class MainGUI(QtWidgets.QMainWindow):
    def __init__(self,*args, **kwargs):
        super(MainGUI,self).__init__(*args,**kwargs)
        
        self.scaledStartTime = None
        self.scaledEndTime = None        
        self.curStartTime = None
        self.curEndTime = None
        self.expandFrame = 100
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.mainWidget = QtWidgets.QWidget(self)
        mainLayout = QtWidgets.QHBoxLayout(self.mainWidget)
        btn = TimeScaleBtn(self)
        btn.setText("< scroll scale >")
        btn.setMinimumSize(90,20)
        btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        mainLayout.addWidget(btn)
        
        self.extendFrameBtn = TimeExpandBtn(self)
        self.extendFrameBtn.setMinimumSize(90,20)
        self.extendFrameBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.extendFrameBtn.clicked.connect(ApplyFunc(self.templateToggleTimeRange))
        mainLayout.addWidget(self.extendFrameBtn)

        self.setCentralWidget(self.mainWidget)
        self.loadOption()

    def templateToggleTimeRange(self):
        self.saveOption()
        self.scaledStartTime,self.scaledEndTime = templateExtendTimeSlider(int(self.expandFrame))

    def editFrameExpandValue(self):
        dialog = TimeSettingDialog(curValue=self.expandFrame,parent= self)
        
        if dialog.exec_():
            self.setFrameExpandValue(dialog.setValue)
            
    def setFrameExpandValue(self,frame):
        self.expandFrame = frame
        self.extendFrameBtn.setText(str(frame))

    def saveOption(self):    
        cmds.optionVar(stringValue = [self.objectName,self.expandFrame])

    def loadOption(self):    
        if cmds.optionVar(exists = self.objectName):
            self.expandFrame = int(cmds.optionVar(q = objectName))
        
        self.setFrameExpandValue(self.expandFrame)

def main():
    objectName = "timeSliderScaleTool"

    desktop       = QtWidgets.QApplication.desktop()
    mayaMainWindow = getTopLevelWidget('MayaWindow')
    activeScreen  = desktop.screenNumber(mayaMainWindow)
    desktopRect = desktop.screenGeometry(activeScreen)
        
    windowCenter = mayaMainWindow.rect().center()
    windowCheck(objectName,mayaMainWindow)

    mainGUI = MainGUI(mayaMainWindow)
    mainGUI.setObjectName(objectName)
    mainGUI.loadOption()

    mainGUI.setWindowTitle(objectName)
    mainGUI.resize(50,40)

    mainGUI.show()
    mainGUI.move(desktopRect.topLeft() + mayaMainWindow.rect().topLeft() + windowCenter)
