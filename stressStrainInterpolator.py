# Stress-Strain-Interpolator V1.1
#
# Author: Christian Krumwiede
# Date: 29.10.21
#

import csv
import matplotlib.pyplot as pyplot
import numpy as np
import scipy.optimize as optimize

# ---------- PARAMETER ---------- #
DEFAULTCONFIGFILEPATH = 'data\\config.csv'

COLOR_DATA = 'black'
COLOR_BREAKPOINT = 'tab:red'
COLOR_INTERPOLATION = 'tab:blue'

EXPORTFILENAME = 'Interpolation.csv'
EXPORTSTEPWIDTH = 0.01  # %


# ---------- KLASSEN ---------- #
class DataSet:
    """
    DataSet Klasse um die einzelnen Datensätze als Objekt abzubilden.
    """

    def __init__(self, name, width, thickness, length, fOffset, isValid, color, fileName):
        self.name = name
        self.width = width
        self.thickness = thickness
        self.length = length
        self.fOffset = fOffset
        self.isValid = isValid
        self.color = color
        self.fileName = fileName
        self.strainVector = None
        self.stressVector = None
        self.maxStress = 0
        self.maxStrain = 0
        self.youngsModulus = 0
        self.size = 0

    def calcMax(self):
        self.maxStress = self.stressVector.max()
        idx = int(np.where(self.stressVector == self.maxStress)[0])
        self.maxStrain = self.strainVector[idx]

    def calcYoungsModulus(self):
        epsilon1 = 0.05
        epsilon2 = 0.25

        list1 = [abs(x - epsilon1) for x in self.strainVector]
        i1 = list1.index(min(list1))
        epsilon1 = self.strainVector[i1]
        sigma1 = self.stressVector[i1]

        list2 = [abs(x - epsilon2) for x in self.strainVector]
        i2 = list2.index(min(list2))
        epsilon2 = self.strainVector[i2]
        sigma2 = self.stressVector[i2]

        dEpsilon = epsilon2 - epsilon1
        dSigma = sigma2 - sigma1

        self.youngsModulus = 100 * dSigma / dEpsilon

    def calcSize(self):
        self.size = len(self.strainVector)


# ---------- FUNKTIONEN ---------- #
def importData(configFilePath, onlyValid):
    """
    importData:
    Importieren der in der config-Datei spezifizierten Datensätze als Liste an Datensätzen (DataSet-Objekten)

    :param configFilePath: Dateipfad zur config-Datei
    :param onlyValid: True = Aussortieren der nicht gültigen Datensätze
    :return: Liste mit den DataSet-Objekten
    """
    dataSetList = []

    with open(configFilePath, 'r', newline='') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=';')

        # Skip first two rows
        for i in range(2):
            csvReader.__next__()

        for line in csvReader:
            name = line[0]
            width = float(line[1].replace(',', '.'))
            thickness = float(line[2].replace(',', '.'))
            lenght = float(line[3].replace(',', '.'))
            fOffset = float(line[4].replace(',', '.'))

            isValid = True
            if 'nein' in line[5].lower():
                isValid = False

            color = line[6]
            fileName = line[7]

            newDataSet = DataSet(name, width, thickness, lenght, fOffset, isValid, color, fileName)

            dataSetList.append(newDataSet)

    # Aussortieren der nicht gültigen Datensätze (wenn gewünscht)
    if onlyValid:
        for dSet in list(dataSetList):
            if not dSet.isValid:
                dataSetList.remove(dSet)

    # Abtrennen des directory-Teils vom conifigFilePath
    directoryPath = configFilePath[0:configFilePath.rfind('\\')+1]

    # Einlesen der Datensätze
    for dSet in dataSetList:
        filePath = directoryPath + dSet.fileName

        with open(filePath, 'r') as dSetFile:
            dispo0 = 0
            strainList = []
            stressList = []

            # Skip first three rows
            for i in range(3):
                dSetFile.readline()

            for line in dSetFile:
                lineValues = line.split()
                force = float(lineValues[1].replace(',', '.'))
                dispo = float(lineValues[2].replace(',', '.'))

                if dispo0 == 0:
                    dispo0 = dispo

                strain = ((dispo - dispo0) / (1000 * dSet.length)) * 100  # stress (epsilon) in %
                stress = (force - dSet.fOffset) / (dSet.width * dSet.thickness)  # Strain (sigma) in MPa

                strainList.append(strain)
                stressList.append(stress)

            dSet.strainVector = np.array(strainList)
            dSet.stressVector = np.array(stressList)

    # Berechnen der Datensatz Attribute
    for dSet in dataSetList:
        dSet.calcMax()
        dSet.calcYoungsModulus()
        dSet.calcSize()

    return dataSetList


# Polynom 8ter-Ordnung mit a0=0
def polynomial8_0(x, a1, a2, a3, a4, a5, a6, a7, a8):
    return a8 * x ** 8 + a7 * x ** 7 + a6 * x ** 6 + a5 * x ** 5 + a4 * x ** 4 + a3 * x ** 3 + a2 * x ** 2 + a1 * x


# ---------- MAIN ---------- #
if __name__ == '__main__':

    # Init Variablen
    configFilePath = DEFAULTCONFIGFILEPATH
    plotOnlyValid = False
    writeOutput = False

# ----- Start-Up Prompt ----- #
    print('Stress-Strain-Interpolator V1.0')
    print('')
    print('Dieses Programm plotted alle Dateien die in "data\config.csv" spezifiziert sind in ein Diagramm.')
    print('')

    input0 = input('Pfad zur Konfiguratiosdatei (ENTER = "data\config.csv"): ')
    if not input0 == '': configFilePath = input0

    input0 = input('Nur die gültigen Messdateien verarbeiten? (j/n): ')
    if input0 == 'j': plotOnlyValid = True

    #
    # input0 = input('Ausgabe in "' + outFilePath + '" schreiben? (j/n): ')
    #

    print('')

# ----- Einlesen der in der Config-Datei spezifizierten Datensätze ----- #
    dataSetList = importData(configFilePath, plotOnlyValid)

# ----- Auswählen des zu interpolierenden ----- #
    print('Eingelesene Datensätze (Nr.: Name; Datei): ')

    for idx, dSet in enumerate(dataSetList):
        print(idx, end=": ")
        print(dSet.name, end=" - ")
        print(dSet.fileName)

    input0 = input('Nummer des zu interpolierenden Datensatzes: ')
    if input0 == '':
        input0 = 0
    else:
        input0 = int(input0)

    dataSet = dataSetList[input0]
    dSetName = dataSetList[input0].name + '-' + dataSetList[input0].fileName

    print('"' + dSetName + '" eingelesen')
    print()

# ----- Interpolation ----- #
    # Beschränken der Interpolation auf Bereich bis Bruchstelle
    idx = int(np.where(dataSet.stressVector == dataSet.maxStress)[0])
    strainVectorReduced = dataSet.strainVector[0:idx+1]
    stressVectorReduced = dataSet.stressVector[0:idx+1]

    # Eigentliche Interpolation (bzw. Curve Fit)
    popt, _ = optimize.curve_fit(polynomial8_0, strainVectorReduced, stressVectorReduced)
    fitVectorReduced = polynomial8_0(strainVectorReduced, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], popt[6],
                                     popt[7])

    # Fehlerberechnung
    errorVector = stressVectorReduced - fitVectorReduced
    magnitudeErrorVector = np.sqrt(errorVector ** 2)
    magnitudeErrorVectorPercent = magnitudeErrorVector / stressVectorReduced
    rmsError = np.mean(magnitudeErrorVector)

# ----- Print ----- #
    print('Koeffizienten von "f(x) = a8*x^8 + a7*x^7 + a6*x^6 + a5*x^5 + a4*x^4 + a3*x^3 + a2*x^2 + a1^x + 0": ')
    for i, p in enumerate(popt):
        print('a' + str(i+1) + ' = ' + str(p))
    print('für Dehnung innerhalb [0:%f]%% ' % dataSet.maxStrain)
    print()

    print('Abweichung: ')
    print('Fehler_RMS:', rmsError, 'MPa')
    print('max(Fehler_Absolut):', magnitudeErrorVector.max(), 'MPa')
    print('max(Fehler_Relativ):', magnitudeErrorVectorPercent.max(), '%')
    print()

# ----- Plot ----- #
    pyplot.title('Spannungs-Dehnungs-Interpolation')
    pyplot.scatter(dataSet.strainVector, dataSet.stressVector, label=dSetName, color=COLOR_DATA, s=2)
    pyplot.plot(strainVectorReduced, fitVectorReduced, color=COLOR_INTERPOLATION, label='Interpolation')
    pyplot.plot(dataSet.maxStrain, dataSet.maxStress, 'x', ms="8", color=COLOR_BREAKPOINT, label='Bruchstelle')
    pyplot.xlabel('Dehnung [%]')
    pyplot.ylabel('Spannung [MPa]')
    pyplot.grid(True)
    pyplot.legend()
    pyplot.show()
