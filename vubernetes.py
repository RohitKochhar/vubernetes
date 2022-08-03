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
        # Create a graph for each app
        for app in self.apps:
            G = nx.DiGraph()    # Graph should be directional
            # Create a master node of the app
            appNode = G.add_nodes_from([(app.name, {'color': 'red', 'shape': 'invtriangle'})])
            resourceCount = {
                "Deployment": 0,
                "Service": 0
            }
            for resource in app.resources:
                # Keep a unique count so that nodes don't double up
                resourceCount[resource.kind] += 1
                # Add edge between appNode and resourceNode
                resourceNodeName = f"{app.name}-{resource.kind.lower()}-{resourceCount[resource.kind]}"
                G.add_nodes_from([(resourceNodeName, {'color':'blue'})])
                G.add_edge(app.name, resourceNodeName)
                if resource.kind == "Service":
                    portNodeName = f"{resource.spec['ports'][0]['name']} {resource.spec['ports'][0]['port']}"
                    G.add_nodes_from([(portNodeName, {'color': 'orange', 'shape':'cds'})])
                    G.add_edge(resourceNodeName, portNodeName)
                if resource.kind == "Deployment":
                    numReplicas = int(resource.spec['replicas'])
                    for i in range(0, numReplicas):
                        try: 
                            volumes = resource.spec['template']['spec']['volumes']
                            for v in range(0, len(volumes)):
                                volumeNodeName = f"{volumes[v]['name']} Volume"
                                G.add_nodes_from([(volumeNodeName, {'color': 'purple', 'shape':'cylinder'})])
                                G.add_edge(resourceNodeName, volumeNodeName)
                        except KeyError:
                            pass
                        containers = resource.spec['template']['spec']['containers']
                        for c in range(0, len(containers)):
                            containerNodeName = f"{containers[c]['name']}-{resourceCount[resource.kind]}"
                            G.add_nodes_from([(containerNodeName, {'color': 'green', 'shape': 'box'})])
                            G.add_edge(resourceNodeName, containerNodeName)
                            try:
                                volumeMounts = containers[c]["volumeMounts"]
                                for vm in range(0, len(volumeMounts)):
                                    mountPathNodeName = volumeMounts[vm]["mountPath"]
                                    G.add_nodes_from([(mountPathNodeName, {'color': 'violet', 'shape':'tab'})])
                                    G.add_edge(containerNodeName, mountPathNodeName)
                                    G.add_edge(volumeMounts[vm]["mountPath"], f"{volumeMounts[vm]['name']} Volume" )
                            except KeyError:
                                pass
            # Create legend
            G.add_nodes_from([
                ("App", {'color':'red', 'shape': 'invtriangle'}), 
                ("Resource", {'color':'blue'}), 
                ("Port", {'color': 'orange', 'shape':'cds'}),
                ("Volume", {'color': 'purple', 'shape':'cylinder'}),
                ("Container", {'color': 'green', 'shape':'box'}),
                ("Mount Path", {'color': 'violet', 'shape':'tab'})
            ])
            G.add_edges_from([
                ("App", "Resource", {'color': "white"}),
                ("Resource", "Volume", {'color': "white"}),
                # ("Volume", "Port", {'color': "white"}),
                ("Port", "Container", {'color': "white"}),
                ("Container", "Mount Path", {'color': "white"}),
            ])
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
            self.spec                       = self.jsonDef["spec"]
            self.appName                    = self.metadata["labels"]["app"]
            if self.appManager.checkIfAppExists(self.appName) == False:
                self.appManager.createApp(self.appName)
            app = self.appManager.getAppByName(self.appName)
            app.addResource(self)

# Main Call ------------------------------------------------------