try:
    from PyQt5.QtWidgets import *
    from PyQt5.uic import loadUi
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtGui import QIcon
    from send2trash import send2trash
except ImportError as e:
    with open(os.getcwd()+"/log.txt", "w") as file:
        file.write(os.popen(f"pip install -r {os.getcwd()}/requirements.txt").read())
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.uic import loadUi
        from PyQt5.QtCore import QCoreApplication
        from PyQt5.QtGui import QIcon
        from send2trash import send2trash
    except ImportError as e:
        print("[EXCEPTION] Something has gone wrong. Please provide requirements.txt before running again.")
        sys.exit()
        
import os
import sys
import threading
import time
import getpass
user = getpass.getuser()

# Extras
# os.makedirs("/home/kali/Desktop/have/even/never/done.py") # creates all the missing folders for create done.py
# os.removedirs("/home/kali/Desktop/have/even/never) # python will try to delete all the folders to the end <!!folders must be empty!!>

# os.path.exists("user.txt"): #boolean: true if the folder exists, false unless
class MyApp(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        loadUi(os.getcwd()+"/design.ui", self)
        
        self._translate = QCoreApplication.translate

        self.history=[]
        self.future=[]
        self.baseTree.setColumnWidth(0, 430)
        self.redoButton.setEnabled(0)

        self.main=os.getcwd()
        self.home="C:\\Users\\"+user
        os.chdir(self.home) # cd {directory} => change directory
        self.draw()

        self.baseTree.clicked.connect(self.opener)

        self.undoButton.clicked.connect(self.undoFunction)
        self.homeButton.clicked.connect(self.homeFunction)
        self.redoButton.clicked.connect(self.redoFunction)
        
        self.baseTree.doubleClicked.connect(self.goInFunction)

        self.renameButton.clicked.connect(self.renameFunction)
        self.removeButton.clicked.connect(self.removeFunction)
        self.newFolderButton.clicked.connect(self.newFolderFunction)

        self.goButton.clicked.connect(self.goFunction)
        self.execButton.clicked.connect(self.execFunction)

        self.directoryLabel.returnPressed.connect(self.goFunction)
        self.commandArea.returnPressed.connect(self.execFunction)

    def draw(self):
        try:
            self.sorted_list = sorted(os.listdir(), key=str.lower) #ls; but shows all the items as python;list
        except PermissionError as e:
            print("Access is denied.")
            self.undoFunction()
            self.future.pop()
            if len(self.future)==0: self.redoButton.setEnabled(0)
            return

        if len(self.history)==0: self.undoButton.setEnabled(0)
        else: self.undoButton.setEnabled(1)
        if len(self.future)==0: self.redoButton.setEnabled(0)
        else: self.redoButton.setEnabled(1)

        self.directoryLabel.setText(os.getcwd()) # pwd => current directory
        self.baseTree.clear()

        for i in range(len(self.sorted_list)):
            try: size = os.stat(self.sorted_list[i])[6]
            except Exception as e: size = 0
            try: lastAccess = time.strftime('%H:%M %d/%m/%Y', time.localtime(os.stat(self.sorted_list[i])[7]))
            except Exception as e: lastAccess = "Unknown"
            try: lastModification = time.strftime('%H:%M %d/%m/%Y', time.localtime(os.stat(self.sorted_list[i])[8]))
            except Exception as e: lastModification = "Unknown"
            c = 0
            while size>1024 and c<3: # 3 -> terabytes (TiB (1024*GiB))
                size/=1024
                c += 1
            c = "KiB" if c==0 else ["MiB" if c==1 else "GiB"][0]
            temp = QTreeWidgetItem([
                self._translate("form", self.sorted_list[i]),
                "Folder" if os.path.isdir(self.sorted_list[i]) else "File",
                f"{size:.1f}"+" "+c,
                lastAccess,
                lastModification
            ])
            type = "/folder.png" if os.path.isdir(self.sorted_list[i]) else ["/gear.png" if self.sorted_list[i].endswith(".lnk") else "/file.png"][0]
            temp.setIcon(0, QIcon(self.main+"/icons"+type))
            self.baseTree.addTopLevelItems([temp])

    def opener(self):
        self.renameButton.setEnabled(1)
        self.removeButton.setEnabled(1)
        selectedName = self.baseTree.selectedItems()[0].text(0)
        if not os.path.isdir(selectedName):
            if selectedName.endswith(".lnk"):
                self.commandArea.setText("\""+selectedName+"\"")
            else:
                self.commandArea.setText('notepad "'+selectedName+'"')
        else:
            self.commandArea.setText('cd "'+selectedName+'"')
    
    def closer(self):
        self.renameButton.setEnabled(0)
        self.removeButton.setEnabled(0)

    def goInFunction(self):
        # selectedIndex = self.baseTree.selectedIndexes()[0].row()
        selectedName = self.baseTree.selectedItems()[0].text(0)
        if os.path.isdir(selectedName):
            path = os.getcwd()+"/"+selectedName
            self.history.append(os.getcwd())
            self.undoButton.setEnabled(1)
            self.future=[]
            self.redoButton.setEnabled(0)
            os.chdir(path)
            self.future.clear()
            self.draw()
        else:
            try:
                # self.commandArea.setText('notepad '+selectedName)
                # os.system('notepad '+selectedName)
                threading.Thread(target=os.system, args=(self.commandArea.text(),)).start()
                # os.system(self.commandArea.text())
            except Exception as e:
                print(type(e), e)
            # self.ext=os.path.splitext(selectedName)[1] #splits file's name and its extension ==> ("file",".py")
            # if self.ext=='.txt': os.system('notepad '+selectedName)
            # else: print("Unsupported filetype.")
        self.closer()

    def goFunction(self):
        path = self.directoryLabel.text()
        if path==os.getcwd(): return
        if os.path.exists(path) and os.path.isdir(path):
            self.history.append(os.getcwd())
            self.undoButton.setEnabled(1)
            self.future=[]
            self.redoButton.setEnabled(0)
            os.chdir(path)

            self.future.clear()
            self.closer()
            self.draw()
        else:
            if not path.endswith("(?)"):
                self.directoryLabel.setText(path+" (?)")

    def execFunction(self):
        cmd = self.commandArea.text()
        if cmd=="": return
        os.system(cmd+' > '+os.getcwd()+'\\results.txt')
        see=open(os.getcwd()+'\\results.txt').read()
        if see!="":
            QMessageBox.information(self,"Result(s)",see,QMessageBox.Ok)
        else:
            os.remove(os.getcwd()+"\\results.txt")
            QMessageBox.information(self,"Result(s)","Command did not produce an output.",QMessageBox.Ok)
        self.draw()

    def homeFunction(self):
        if self.home==os.getcwd(): return
        self.history.append(os.getcwd())
        self.undoButton.setEnabled(1)
        self.future=[]
        self.redoButton.setEnabled(0)
        os.chdir(self.home)
        self.closer()
        self.draw()

    def undoFunction(self):
        self.future.append(os.getcwd())
        self.redoButton.setEnabled(1)

        path = self.history[-1]
        os.chdir(path)
        while self.history[-1]==path:
            self.history.pop()
            if len(self.history)==0:
                self.undoButton.setEnabled(0)
                break
        self.closer()
        self.draw()

    def redoFunction(self):
        self.history.append(os.getcwd())
        self.undoButton.setEnabled(1)

        path = self.future[-1]
        os.chdir(path)
        while self.future[-1]==path:
            self.future.pop()
            if len(self.future)==0:
                self.redoButton.setEnabled(0)
                break
        self.closer()
        self.draw()

    def renameFunction(self):
        # selectedIndex = self.baseTree.selectedIndexes()[0].row()
        selectedName = self.baseTree.selectedItems()[0].text(0)

        name, accept = QInputDialog.getText(self, 'Change folder name', "Put the new name you want.",text=selectedName)
        if accept and len(name)>0:
            sureness=QMessageBox.question(self,"Confirm","Are you sure?",QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)
            if sureness==QMessageBox.Yes:
                try:
                    os.rename(selectedName,name) #changes name of file/folder
                    self.draw()
                    QMessageBox.information(self,"Information","Successfully changed.",QMessageBox.Ok)
                except Exception as error:
                    QMessageBox.information(self,"Information","Couldn't change.",QMessageBox.Ok)

    def removeFunction(self):
        # selectedIndex = self.baseTree.selectedIndexes()[0].row()
        selectedName = self.baseTree.selectedItems()[0].text(0)

        sureness=QMessageBox.question(self,"Confirm","Are you sure?",QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)
        if sureness==QMessageBox.Yes:
            try:
                # rmdir(selectedName) #deletes a folder as {name} from current directory.
                send2trash(os.getcwd()+"\\"+selectedName)
                # os.system(f"move '{selectedName}' C:/$Recycle.Bin")
                self.draw()
                QMessageBox.information(self,"Information","Successfully deleted.",QMessageBox.Ok)
            except Exception as e:
                print(type(e), e)
                QMessageBox.information(self,"Information","Couldn't delete.",QMessageBox.Ok)
        self.closer()

    def newFolderFunction(self):
        name, accept = QInputDialog.getText(self, 'Create a folder', "Put the folder's name you want.",text="New Folder")
        if accept and len(name)>0 and not os.path.exists(name):
            os.mkdir(name) #creates a folder to current directory as name
            QMessageBox.information(self,"Information",f"{name} created.",QMessageBox.Ok)
        elif os.path.exists(name):
            QMessageBox.information(self,"Information",f"{name} already exists.",QMessageBox.Ok)
        elif len(name)==0:
            QMessageBox.information(self,"Information","Need to put a name.",QMessageBox.Ok)
        self.closer()
        self.draw()

if __name__=='__main__':
    app = QApplication([])
    win = MyApp()
    win.show()
    app.exec_()