from owlready2 import *
import types
from copy import copy
import datetime
import requests
from pydoc import locate
import wx
import threading
import yaml
import json
from pango_aliasor.aliasor import Aliasor
import csv




class Window(threading.Thread,wx.Frame):
    def __init__(self, parent, ID, title): 
        threading.Thread.__init__(self)
        self.urlOnto=os.getcwd()
        wx.Frame.__init__(self, parent, -1, title, pos=(200, 100), size=(800, 600)) 
        self.SetBackgroundColour("#F2F6FC")
        self.panel = wx.Panel(self, -1)  
        libele = wx.StaticText(self.panel, -1, "SARSMutOnto Generator", wx.Point(200,10), wx.Size(-1, -1) )               
        libele.SetFont(wx.Font(24, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD, 0, ""))
        libele.SetForegroundColour("#F4A100")

        self.lineageBox = wx.TextCtrl(self.panel, pos=(10, 110), size=(490,420), style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.mutationBox = wx.TextCtrl(self.panel, pos=(515, 110), size=(260,420), style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.displayLine('Choose a target directory for the ontology')
        self.dirDlgBtn = wx.Button(self.panel, -1, "Choose directory",  wx.Point(210,60), wx.Size(160, 35))      
        self.dirDlgBtn.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,0, ""))
        self.dirDlgBtn.SetBackgroundColour("#00AC69")
        self.dirDlgBtn.SetForegroundColour("#FFFFFF")
        
        self.Bind(wx.EVT_BUTTON, self.onDir, self.dirDlgBtn)  
        
        self.StartButton = wx.Button(self.panel, -1, "Generate",  wx.Point(380, 60), wx.Size(150, 35))      
        self.StartButton.SetFont(wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,0, ""))
        self.Bind(wx.EVT_BUTTON, self.lancerGeneration, self.StartButton)  
        self.StartButton.SetBackgroundColour("#0061F2")
        self.StartButton.SetForegroundColour("#FFFFFF")
        self.StartButton.Disable()
        self.Show(True)

#--------------------------- dialogue-----------------------------
    def onDir(self, event):
        url=self.targetDir("Choose a target directory")+"\SARSMutOnto.owl"
        url=url.replace('\\','/')
        self.urlOnto ="file://"+url
        texte = wx.StaticText(self.panel, -1, "SARSMutOnto directory target :"+url, wx.Point(10,540), wx.Size(-1, -1) )  
        texte.SetFont(wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD, 0, ""))
        self.StartButton.Enable()
        self.displayLine('Click on the button "Generate" to start generation')
    def targetDir(self, message):
        dlg = wx.DirDialog(self, message=message,defaultPath= self.urlOnto,style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        else:
            path = 'c:/'
        dlg.Destroy()
        self.dirDlgBtn.Disable()
        return path 
#-----------------------------------------------------------------------
    def lancerGeneration(self, event):
        self.StartButton.Disable()
        self.displayLine('It may take a few minutes, Please waite ...')
        generator=Generator(None,self,self.urlOnto)
        generator.start()
        t = threading.Thread(target=generator.lancer, args=(self,))
        t.start()
#------------------------display------------------------------------         
    def displayLine(self,ch):
        self.lineageBox.AppendText(ch+"\n")
    def displayMutation(self,ch):
        self.mutationBox.AppendText(ch+"\n")
#------------------------------------------------------------------    

#________________ create model________________def createModel():
class Ontology:
    def __init__(self,url):
        self.onto = get_ontology(url)
        self.onto.metadata.comment.append("SARSMutOnto is an ontology that describes the SARS-CoV2 genome structure by detailing its component genes. It also describes all the variants listed by the researchers while keeping the hierarchical relationship (variant / sub-variant) between the variants")
        self.genes={}
    def classCreation(self):
        
        with self.onto:
            class SARS_CoV2(Thing):
                pass
            class genome(SARS_CoV2):
                pass
            class gene(genome):
                pass
            class label(DatatypeProperty):
                domain    = [gene]
                range = [str]
            class structural_gene(gene):
                pass
            class non_structural_gene(gene):
                pass
            class accessory_gene (gene):
                pass
            class variant(SARS_CoV2):
                pass
            class lineage(variant):
                pass
            class has_for_alias(DatatypeProperty):
                domain    = [lineage]
                range = [str]
            class has_for_WHO_name(DatatypeProperty):
                domain    = [lineage]
                range = [str]
            class appeared_on(DatatypeProperty):
                domain    = [lineage]
                range = [datetime.date]
            class has_for_description(DatatypeProperty):
                domain    = [lineage]
                range = [str]

            class mutation(Thing):
                pass
            class recombinant(variant):
                pass


            class SNP(mutation):
                pass
            
            class mutation_name(DatatypeProperty):
                domain    = [SNP]
                range = [str]

            class has_for_gene(ObjectProperty):
                domain    = [SNP]
                range     = [gene]
            class has_for_lineage(ObjectProperty):
                domain    = [SNP]
                range     = [lineage]
    def genesCreation(self):
        
        with self.onto:
            self.genes["orf1a"]=self.onto.non_structural_gene("orf1a")
            self.genes["orf1b"]=self.onto.non_structural_gene("orf1b")
            self.genes["s"]=self.onto.structural_gene("s")
            self.genes["orf3a"]=self.onto.accessory_gene("orf3a")
            self.genes["orf3b"]=self.onto.accessory_gene("orf3b")
            self.genes["e"]=self.onto.structural_gene("e")
            self.genes["m"]=self.onto.structural_gene("m")
            self.genes["orf6"]=self.onto.accessory_gene("orf6")
            self.genes["orf7a"]=self.onto.accessory_gene("orf7a")
            self.genes["orf7b"]=self.onto.accessory_gene("orf7b")
            self.genes["orf8"]=self.onto.accessory_gene("orf8")
            self.genes["n"]=self.onto.structural_gene("n")
            self.genes["orf9a"]=self.onto.accessory_gene("orf9a")
            self.genes["orf9b"]=self.onto.accessory_gene("orf9b")
            self.genes["orf10"]=self.onto.accessory_gene("orf10")
        self.onto.save(format = "rdfxml")
        
who_names={"B.1.1.7":"Alpha", "B.1.351":"Beta", "P.1":"Gamma", "B.1.617.2":"Delta", "B.1.617.1":"Delta", "B.1.617.1":"Delta", "BA.1":"Omicron", "BA.2":"Omicron", "BA.4":"Omicron", "BA.5":"Omicron", "BA.2.12.1":"Omicron", "BA.2.75":"Omicron", "BQ.1":"Omicron", "XBB":"Omicron", "XBB.1.5":"Omicron", "B.1.617.1":"Kappa", "B.1.525":"Eta", "B.1.526":"Iota", "C.37":"Lambda", "B.1.621":"Mu", "B.1.427":"Epsilon" }
class Generator(threading.Thread):
    def __init__(self, parent,cadre,urlOnto):
        
        self.url=urlOnto           
        threading.Thread.__init__(self)
        self.model=Ontology(self.url)
        self.lineagesLists=[]

    def classHierarchyCreation(self):  
        url="https://raw.githubusercontent.com/cov-lineages/pango-designation/master/lineage_notes.txt"  
        notes=requests.get(url)
        reader = csv.DictReader(notes.content, delimiter=',')
        strings = notes.text.split('\n')
        data=[]
        i=0
        for s in strings[1:]:
            data.append(s.split('\t'))
        descriptionLineages={}
        for row in data:
            lineage=row[0]
            i=i+1
            if(len(row)==1): 
                row.append(" ")
            description=row[1]
            descriptionLineages[lineage]=description
        nbChildren=0
        f=requests.get("https://raw.githubusercontent.com/outbreak-info/outbreak.info/master/curated_reports_prep/lineages.yml")
        try:
            self.lineagesLists = yaml.load(f.content, Loader=yaml.FullLoader)                
            for i in range(len( self.lineagesLists)):
                    nbChildren=len(self.lineagesLists[i]["children"])
                    self.lineagesLists[i].pop("children")
                    self.lineagesLists[i]["nbChildren"]=nbChildren
                    self.lineagesLists[i]["description"]=descriptionLineages[self.lineagesLists[i]["name"]]  
        except yaml.YAMLError as e:
            print(e)  


    def lancer(self,cadre):
        self.model.classCreation()
        self.model.genesCreation()
        self.classHierarchyCreation()   
        aliasor = Aliasor()  
        for i in range(len(self.lineagesLists)):
            variant=self.lineagesLists[i]
            alias=aliasor.uncompress(variant["name"])
            self.classAndIndividual(variant,alias,cadre,aliasor)
            self.model.onto.save(format = "rdfxml")
        cadre.displayLine("====================== THE END ======================")   
       # self.displayVariant("A",cadre)
#---------------------------------------------------------------------------
    def findParent(self,key):
        for i in range(len(self.lineagesLists)):
            if key == self.lineagesLists[i]["name"]:
                return  self.lineagesLists[i] 
        return -1

#-----------------------------------------------------------------------------
    def classAndIndividual(self,variant,alias,cadre,aliasor):
            name=variant["name"]
            nbCh=variant["nbChildren"]
            description=variant["description"]
            cadre.displayLine("\t Lineage "+name+" : ("+str(nbCh)+") sub-lineages  ...")
            with self.model.onto:
                if ("parent" in variant.keys()) :
                    parent=variant["parent"]
                    try:
                        variantClass = types.new_class(name, (self.model.onto[parent],))                    
                    except Exception as e:
                        if(not self.model.onto[parent]):
                            vparent=self.findParent(parent) 
                            aliasp=aliasor.uncompress(parent)                               
                            self.classAndIndividual(vparent,aliasp,cadre,aliasp)
                            i=self.lineagesLists.find(vparent)
                            del self.lineagesLists[i] 
                    
                elif ("recombinant_parents"  in variant.keys()):
                    parents=variant["recombinant_parents"].split(",")
                    f1=parents[0].find("*")
                    f2=parents[1].find("*")
                    parent1=parents[0]
                    parent2=parents[1]
                    if parents[1][0:6]=="BA.4/5" : 
                        parent2="BA.4"
                        f2=-1
                    if f1!=-1 :
                        if(parents[0][f1-1]=='.') : 
                            parent1=parents[0][0:f1]+"1"
                            f1=f1+1
                        parent1=parent1[0:f1]
                    if f2!=-1 :
                        if(parents[1][f2-1]=='.') : 
                            parent2=parents[1][0:f2]+"1"
                            f2=f2+1
                        parent2=parent2[0:f2]

                    try :
                        variantClass = types.new_class(name, (self.model.onto["recombinant"],self.model.onto[parent1],self.model.onto[parent2]))
                    except Exception as e:
                        print("========"+name+"====Exception====>"+ repr(e))
                    # variantClass.is_a.append(self.model.onto[parent1])
                else: 
                    variantClass = types.new_class(name, (self.model.onto["lineage"],)) 

                indvidual=variantClass(name+"__lineage")
                indvidual.label=[name]
                indvidual.has_for_description=[description]
                if name in who_names:
                    indvidual.has_for_WHO_name=[who_names[name]]
                if alias != variant["name"]:
                    indvidual.has_for_alias=[alias]
                if(name!='A' and name!='B'):
                    self.mutation(name,indvidual,cadre,0)
#----------------------------------------------------------------------------        
    def mutation(self,name,indvidual,cadre,i):
        cadre.displayMutation("\t__________"+name+"__________")  
        if name in who_names:
             cadre.displayMutation("\t WHO name :"+who_names[name])   
        url="https://api.outbreak.info/genomics/lineage-mutations?pangolin_lineage="+name+"&frequency=0.75"
        r=requests.get(url)
        #cadre.displayLine(url)
        try:
            data = r.json()
            if(name not in data["results"]):
                    if(i<1) : self.mutation(name,indvidual,cadre,i+1)
                    return
        except :  # includes simplejson.decoder.JSONDecodeError
            cadre.displayLine('\t Retrieve of '+name+' retry '+str(i+1))
            if(i<1) : self.mutation(name,indvidual,cadre,i+1)
            else :  
                cadre.displayLine('\t Mutations of  '+name+'\t not provided by API')
                cadre.displayLine('\t Class of lineage '+name+' created without mutations')
            return
        
        for mut in data["results"][name]:
            indexdp=mut["mutation"].find(":")
            g=mut["mutation"][:indexdp]
            aa=mut["mutation"][indexdp+1:]
            with self.model.onto:
                my_snp = self.model.onto["SNP"](aa)
                my_snp.mutation_name=[aa]
                my_snp.has_for_gene.append(self.model.genes[g])
                my_snp.has_for_lineage.append(indvidual)
                cadre.displayMutation("      "+g+"\t--\t"+aa)     
                    
class mainApp(wx.App):
    def OnInit(self):
        frame = Window(None,-1,"SARSMutOnto Generator")
        frame.start()
        self.SetTopWindow(frame)        
        return True
 #-----------------------------------------------------------------------------
if __name__ == '__main__':
    app = mainApp(0) 
    app.MainLoop()   
    

#Go to parent lineage: B.1.617.2