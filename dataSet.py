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
        self.youngsModulus = 0
        self.size = 0

    def appendDataPoint (self, stress, strain):
        self.stressList.append(stress)
        self.strainList.append(strain)

    def calcMax(self):
        i = self.stressList.index(max(self.stressList))
        self.maxStress = self.stressList[i]
        self.maxStrain = self.strainList[i]

    def calcYoungsModulus(self):
        epsilon1 = 0.05
        epsilon2 = 0.25

        list1 = [abs(x - epsilon1) for x in self.strainList]
        i1 = list1.index(min(list1))
        epsilon1 = self.strainList[i1]
        sigma1 = self.stressList[i1]

        list2 = [abs(x - epsilon2) for x in self.strainList]
        i2 = list2.index(min(list2))
        epsilon2 = self.strainList[i2]
        sigma2 = self.stressList[i2]

        dEpsilon = epsilon2 - epsilon1
        dSigma = sigma2 - sigma1

        self.youngsModulus = dSigma / dEpsilon

    def calcSize(self):
        self.size = len(self.strainList)