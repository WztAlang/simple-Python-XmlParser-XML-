import re

class XmlTree:
    def __init__(self):
        self.tag = ""
        self.text = ""
        self.attrs = {}
        self.children =[]
        self.parent = None

    def findElementsByTagName(self, name):
        children = self.children[:]
        trees = []
        for child in children:
            if (child.tag == name):
                trees.append(child)
            sub = child.children[:]
            for i in sub:
                children.append(i)
        return trees

    def hasAttribute(self,attr):
        has=False
        for key,value in self.attrs.items():
            if(key==attr.strip("\"")):
                has=True
                break
        return has
    def getAttribute(self,attr):
        if(self.hasAttribute(attr)):
            return self.attrs[attr]
        else:
            raise Exception("No such Attribute:%s"%attr)

class XmlParser():
    space = re.compile(r"\s")
    tagStack = []
    attr_Error="Attribute [%s] should be included by \" \""
    tag_Unclosed_Error="No closed tag matches :\"%s\""
    tag_Unmatched_Error="pop tag:%s  red tag:%s."
    def __init__(self,path):
        self.path=path
        self.document=self.getRoot()

    def getRoot(self):
        root = XmlTree()
        file = open(self.path, "r")
        firstLine= file.readline()
        if(firstLine.find("<?xml")>=0):
            root.text=firstLine
        else:
            file.close()
            file=open(self.path, "r")
        self.beginTag(file, root)
        return root

    def beginTag(self,file, parent, has=None):
        if (has == None):
            byte = file.read(1)#read "<"
            byte = self.ignoreWhiteSpace(file, byte)
            byte=file.read(1)
            if (byte == ""):
                self.tryRaiseTagError(file)
                return
            elif(byte=='/'):
                self.endTag(file,parent.parent)
            elif(byte=="!"):
                self.ignoreNote(file,parent)
            s=byte
        else:
            byte = has
            s = has

        if (byte != ""):
            me = XmlTree()
            parent.children.append(me)
            me.parent = parent
            byte = file.read(1)
            while (byte != '>'and byte!=""):
                s += byte
                byte = file.read(1)

            if (byte == ""):
                self.tryRaiseTagError(file)
                return

            attrs = s.split()
            if (len(attrs) > 1):
                for i in range(1, len(attrs)):
                    # print attrs[i]
                    key, value = attrs[i].split('=')
                    if(value.startswith("\"")==False or value.endswith("\"")==False):
                        self.raiseAttributeError(file,value)
                    me.attrs[key] = value.strip("\"")
            me.tag = attrs[0]
            '''print "tag:%s"%me["tag"]
            print "parent:%s"%me["parent"]["tag"]
            print "parent's chlildren:%s"%me["parent"]["children"]'''
            self.tagStack.append(attrs[0])
            self.Content(file, parent, me)
        else:
            self.tryRaiseTagError(file)
            return

    def Content(self,file, parent, me):
        byte = file.read(1)
        if (byte == ""):
            self.tryRaiseTagError(file)
            return
        byte = self.ignoreWhiteSpace(file, byte)
        if (byte != "<"):
            s = byte
            while (byte != "<"and byte!=""):
                s += byte
                byte = file.read(1)
                
            if (byte == ""):
                self.tryRaiseTagError(file)
                return
            me.text = s
            self.endTag(file, parent)
        else:
            byte = file.read(1)
            if (byte == ""):
                self.tryRaiseTagError(file)
                return
            if (byte == "/"):
                self.endTag(file, parent)
            elif(byte=="!"):
                self.ignoreNote(file, parent)
            else:
                self.beginTag(file, me, byte)




    def endTag(self,file, parent):
        byte = file.read(1)
        s=byte
        if (byte == ""):
            self.tryRaiseTagError(file)
            return
        while (byte != ">" and byte!=""):
            byte = file.read(1)
            s+=byte
        if (byte == ""):
            self.tryRaiseTagError(file)
            return

        tag=self.tagStack.pop()
        if(s.find(tag)<0):
            file.close()
            raise  Exception("Tag Unmatched!",self.tag_Unmatched_Error%(tag,s))
        else:
            self.beginTag(file, parent)

    def tryRaiseTagError(self,file):
        if (len(self.tagStack) > 0):
            file.close()
            unclosed = " "
            for i in self.tagStack:
                unclosed += i + " "
            raise Exception("Tag Unclosed!", self.tag_Unclosed_Error % unclosed)
        else:
            pass

    def raiseAttributeError(self,file,attr):
        file.close()
        raise  Exception("Attribute formate Error!",self.attr_Error%attr)

    def ignoreNote(self, file, parent):
        byte = file.read(1)
        s = byte
        if (byte == ""):
            self.tryRaiseTagError(file)
            return
        while (byte != ">" and byte != ""):
            byte = file.read(1)
            s += byte
        print s
        if (byte == ""):
            self.tryRaiseTagError(file)
            return
        if (s.startswith("--") == False or s.endswith("-->") == False):
            file.close()
            raise Exception("Note formate Error :""<%s""" % s)
        else:
            self.beginTag(file, parent)

    def ignoreWhiteSpace(self,file, byte):
        if (byte == ""):
            self.tryRaiseTagError(file)
        while (self.space.match(byte)):
            byte = file.read(1)
        return byte

parser=XmlParser(r"C:\Users\zitengwa\Desktop\a.xml")
document= parser.document
print document.text,
book=document.findElementsByTagName("book")[0]
print book.hasAttribute("category")
print book.getAttribute("category")
author=book.findElementsByTagName("author")[0]
print author.text


