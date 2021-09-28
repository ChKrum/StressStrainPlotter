class DataSet():

    def __init__(self, number, width, thickness, length, fOffset, isValid, color, fileName):
        self.number = number
        self.width = width
        self.thickness = thickness
        self.length = length
        self.fOffset = fOffset
        self.isValid = isValid
        self.color = color
        self.fileName = fileName
        self.strainList = []
        self.stressList =[]
        self.maxStress = 0
        self.maxStrain = 0
        self.size = 0

    def appendDataPoint (self, stress, strain):
        self.stressList.append(stress)
        self.strainList.append(strain)

    def calcMax(self):
        i = self.stressList.index(max(self.stressList))
        self.maxStress = self.stressList[i]
        self.maxStrain = self.strainList[i]

    def calcSize(self):
        self.size = len(self.strainList)