# File Information ---------------------------------------------
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
# 	File Name: vubernetes.py
#
# 	File Description: 
# 
# 	File History:
# 		- 2022-08-02: Created by Rohit S.
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 

# Imports --------------------------------------------------------
import yaml
import networkx as nx
import matplotlib.pyplot as plt

# Global Variables -----------------------------------------------

# Class Declarations ---------------------------------------------
class Vubernetes():
    def __init__(self, filename):
        self.appManager     = AppManager()
        self.apps           = self.appManager.getApps()
        self.filename       = filename
        self.definitions    = [] 
        self.parseYaml()
        self.createAppGraph()

    def parseYaml(self):
        with open(self.filename, "r") as f:
            tmpFile         = open('tmpFile.yaml', "w+")
            for line in f.readlines():
                # Create an array to store the definition info
                # Remove the newline characters for easier processing
                parsedLine = line.replace("\n", "")
                # Skip empty lines
                if len(parsedLine) != 0:
                    if parsedLine[0] == "#":
                        # If we have a comment, don't do anything
                        pass
                    else:
                        if parsedLine == "---":
                            # We reached the end of a definition
                            # Add the info to the full list of definitions
                            tmpFile.close()
                            with open('tmpFile.yaml', 'r') as t:
                                jsonData = yaml.safe_load(t)
                            
                            definition = Definition(jsonData, self.appManager)

                            # Reset the tempFile
                            tmpFile.close()
                            tmpFile         = open('tmpFile.yaml', "w+")
                        else:
                            # We are still definining the current definition
                            tmpFile.write(f"{parsedLine}\n")

    def createAppGraph(self):
        # Create graph
        for app in self.apps:
            G = nx.DiGraph()
            # Create a master node of the app
            appNode = G.add_nodes_from([(app.name, {'color': 'red'})])
            resourceCount = {
                "Deployment": 0,
                "Service": 0
            }
            for resource in app.resources:
                resourceCount[resource.kind] += 1
                # Add edge between appNode and resourceNode
                e = G.add_edge(app.name, f"{app.name} {resource.kind} {resourceCount[resource.kind]}")

            # same layout using matplotlib with no labels
            p=nx.drawing.nx_pydot.to_pydot(G)
            p.write_png(f'./output/bookinfo_graphs/{app}.png')
        


class AppManager():
    def __init__(self):
        self.__apps = []
        pass

    def checkIfAppExists(self, appName):
        for app in self.__apps:
            if app.name == appName:
                return True 
        return False

    def createApp(self, appName):
        self.__apps.append(App(appName))

    def getAppByName(self, appName):
        for app in self.__apps:
            if app.name == appName:
                return app

    def getApps(self):
        return self.__apps


class App():
    def __init__(self, appName):
        self.name       = appName
        self.resources  = []

    def addResource(self, definintion):
        self.resources.append(definintion)

    def __str__(self):
        return self.name

class Definition():
    def __init__(self, jsonDef, appManager):
        self.jsonDef    = jsonDef
        self.appManager = appManager
        self.parseJson()

    def parseJson(self):
        self.apiVersion             = self.jsonDef["apiVersion"]
        self.kind                   = self.jsonDef["kind"]
        self.metadata               = self.jsonDef["metadata"]
        # Get the app associated with the definition
        if self.kind in ["Deployment", "Service"]:
            self.appName                    = self.metadata["labels"]["app"]
            if self.appManager.checkIfAppExists(self.appName) == False:
                self.appManager.createApp(self.appName)
            app = self.appManager.getAppByName(self.appName)
            app.addResource(self)

# Main Call ------------------------------------------------------