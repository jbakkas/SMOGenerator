import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from owlready2 import *
import types
from copy import copy
import datetime
import inspect
from pydoc import locate
import wx
import threading
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

            class mutation_type(mutation):
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
            self.genes["ORF1a"]=self.onto.non_structural_gene("ORF1a")
            self.genes["ORF1b"]=self.onto.non_structural_gene("ORF1b")
            self.genes["S"]=self.onto.structural_gene("S", namespace = self.onto)
            self.genes["ORF3a"]=self.onto.accessory_gene("ORF3a", namespace = self.onto)
            self.genes["ORF3a"]=self.onto.accessory_gene("ORF3b", namespace = self.onto)
            self.genes["E"]=self.onto.structural_gene("E", namespace = self.onto)
            self.genes["M"]=self.onto.structural_gene("M", namespace = self.onto)
            self.genes["ORF6"]=self.onto.accessory_gene("ORF6", namespace = self.onto)
            self.genes["ORF7a"]=self.onto.accessory_gene("ORF7a", namespace = self.onto)
            self.genes["ORF7b"]=self.onto.accessory_gene("ORF7b", namespace = self.onto)
            self.genes["ORF8"]=self.onto.accessory_gene("ORF8", namespace = self.onto)
            self.genes["N"]=self.onto.structural_gene("N", namespace = self.onto)
            self.genes["ORF9a"]=self.onto.accessory_gene("ORF9a", namespace = self.onto)
            self.genes["ORF9b"]=self.onto.accessory_gene("ORF9b", namespace = self.onto)
            self.genes["ORF10"]=self.onto.accessory_gene("ORF10", namespace = self.onto)
        self.onto.save(format = "rdfxml")
        

class Generator(threading.Thread):
    def __init__(self, parent,cadre,urlOnto):
        threading.Thread.__init__(self)
        self.url=urlOnto
        profile_path = r'C:/Users/Administrator/AppData/Roaming/Mozilla/Firefox/Profiles/oictni5e.default'
        options=Options()
        options.set_preference('profile', profile_path)
        service = Service('../WebDriver/bin/geckodriver.exe')  
        self.driver = Firefox(options=options)   
        self.model=Ontology(self.url)

       

    def lancer(self,cadre):
        self.model.classCreation()
        self.model.genesCreation()
        URL = "https://cov-lineages.org/lineage_list.html"
        ligne="Consultation of the link : "+URL+"  ..."
        cadre.displayLine(ligne)        
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")
        table = soup.find(id="myTable")
        links= table.find_all("a")
        lineages_list=[]
        self.modelisedLineages=[]
        with self.model.onto:
            class A(self.model.onto.lineage):
                pass
            self.modelisedLineages.append('A')
        for lineage_v in links :
            lineages_list.append(lineage_v.text)
        for nom in lineages_list :
            self.displayVariant(nom,'',A,cadre);
        cadre.displayMutation("******* the end of generation *******")
        
    def displayVariant(self,variant,tab,pere,cadre):      
            self.ouvrirPage(variant)
            table = self.chargerTableSousVariants()
            elements = table.find_elements(By.TAG_NAME, 'tr')
            ligne=tab+"the "+variant+" lineage "+"("+str(len(elements[2:]))+' sub-lineages) ...'            
            cadre.displayLine(ligne)       
            print(ligne)
            if (len(elements[2:])>0) :
                self.sousVariants(elements,variant,tab,pere,cadre)
         
    def sousVariants(self,elements,variant,tab,pere,cadre):
        ss_var_list=[]
        nomClasse=variant
        for row in elements[2:]:
            cols = row.find_elements(By.TAG_NAME,'td')
            sous_variant=cols[0].text
            ss_var_list.append([cols[0].text,cols[2].text,cols[5].text,cols[6].text])
        for ssVar in ss_var_list:
            ssvariant=ssVar[0]
            if ssvariant not in self.modelisedLineages:
                description=ssVar[2]
                alias=ssVar[3]
                apparuLeObj = ssVar[1]
                self.modelisedLineages.append(ssvariant)
                with self.model.onto:
                    s_variantClass = type(ssvariant, (pere,), {} )
                sub_lin=s_variantClass(ssvariant+"__lineage")
                sub_lin.label=[ssvariant]
                sub_lin.has_for_description=[description]
                cadre.displayMutation("\t_______"+ssvariant+"_______")                    
                if(len(alias)>0):
                    print(tab,alias)
                    sub_lin.has_for_WHO_name=[alias] 
                    ligne="["+alias+"]"
                    cadre.displayLine("****** "+alias+"******") 
                    cadre.displayMutation("\t WHO name  : "+alias)                        
                if(description[:8]=="Alias of"):
                    alias=description[9:description.find(',')]
                    sub_lin.has_for_alias=[alias]
                if(len(apparuLeObj)):
                    #apparuLeObj=datetime.datetime.strptime(apparuLeObj, '%Y-%m-%d')
                    sub_lin.appeared_on=[apparuLeObj]
                    self.mutations(sous_variant,sub_lin,cadre)
                self.model.onto.save(format = "rdfxml")
                self.displayVariant(ssvariant,'\t'+tab,s_variantClass,cadre)
    def mutations(self,sous_variant,sub_lin,cadre):
        self.driver.get('https://outbreak.info/situation-reports?pango='+sous_variant)
        btn = WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-mut')))
        btn.click()
        mutations_table=self.driver.find_element_by_tag_name('table')
        mutation_rows=mutations_table.find_elements_by_tag_name("tr")
        for mutation_row in mutation_rows[1:] :
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.TAG_NAME, 'td')))
            mutation=mutation_row.find_elements(By.TAG_NAME, "td")
            g=mutation[0].text
            aa=mutation[1].text
            if(g!=''):
                with self.model.onto:
                    my_snp = self.model.onto.SNP(aa, namespace = self.model.onto)
                my_snp.mutation_name=[aa]
                my_snp.has_for_gene.append(self.model.genes[g])
                my_snp.has_for_lineage.append(sub_lin)
                cadre.displayMutation(g+"\t\t--> \t"+aa)
            else:
                cadre.displayMutation("++++++ reading error ++++++")
    
    def ouvrirPage(self,v):  
        self.driver.get('https://cov-lineages.org/lineage.html?lineage='+v)
    def chargerTableSousVariants(self):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "myTable")))
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
    
    