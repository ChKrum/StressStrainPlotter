# Stress-Strain-PLotter V1.1
#
# Author: Christian Krumwiede
# Date: 29.10.21
#

import csv
import matplotlib.pyplot as pyplot
import numpy as np

# ---------- PARAMETER ---------- #
DEFAULTCONFIGFILEPATH = 'data\\config.csv'
OUTPUTFILENAME = 'StressStrainData.csv'
COLORMAP = 'turbo'  # Verfügbare Colormaps siehe https://matplotlib.org/stable/tutorials/colors/colormaps.html


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


def exportData(dataSetList, outFilePath):
    """
    exportData:
    Esportieren der Spannungs-Dehnungsdatensätze in eine gemeinesame csv-Datei

    :param dataSetList: Liste der Datensatz-Objekte
    :param filepath: Export-Dateipfad
    :param filename: Export-Dateiname
    """
    dataSetLengths = []

    # Längster Datensatz bestimmt Länge der Datei
    for dSet in dataSetList:
        dataSetLengths.append(dSet.size)

    nRows = max(dataSetLengths)

    with open(outFilePath, 'w', newline='') as outputFile:
        csvWriter = csv.writer(outputFile, delimiter=';')

        csvRow = []

        # Schreiben der Kopfzeilen
        for dSet in dataSetList:
            csvRow.append(dSet.name)
            csvRow.append(dSet.fileName)

        csvWriter.writerow(csvRow)
        csvRow.clear()

        for dSet in dataSetList:
            csvRow.append('Dehnung')
            csvRow.append('Spannung')

        csvWriter.writerow(csvRow)

        # Schreiben der Datensätze (ggf. Auffüllen mit Nullen, bis zum Ende der Datei)
        for i in range(nRows):
            csvRow.clear()

            for dSet in dataSetList:
                if i > dSet.size - 1:
                    csvRow.append(0)
                    csvRow.append(0)
                else:
                    strain = str(dSet.strainVector[i]).replace('.', ',')
                    stress = str(dSet.stressVector[i]).replace('.', ',')
                    csvRow.append(strain)
                    csvRow.append(stress)

            csvWriter.writerow(csvRow)


# ---------- MAIN ---------- #
if __name__ == '__main__':

    # Init Variablen
    configFilePath = DEFAULTCONFIGFILEPATH
    plotOnlyValid = False
    writeOutput = False
    customColor = False

# ----- Start-Up Prompt ----- #
    print('Stress-Strain-Plotter V1.0')
    print('')
    print('Dieses Programm plotted alle Dateien die in "data\config.csv" spezifiziert sind in ein Diagramm.')
    print('')

    input0 = input('Pfad zur Konfiguratiosdatei (ENTER = "data\config.csv"): ')
    if not input0 == '': configFilePath = input0

    input0 = input('Nur die gültigen Messdateien verarbeiten? (j/n): ')
    if input0 == 'j': plotOnlyValid = True

    outFilePath = configFilePath[0:configFilePath.rfind('\\') + 1] + OUTPUTFILENAME
    input0 = input('Ausgabe in "' + outFilePath + '" schreiben? (j/n): ')
    if input0 == 'j': writeOutput = True

    input0 = input('Benutzerdefinierte Farben verwenden? (j/n): ')
    if input0 == 'j': customColor = True

    print('')

# ----- Einlesen der in der Config-Datei spezifizierten Datensätze ----- #
    dataSetList = importData(configFilePath, plotOnlyValid)

# ----- Ggf. Daten in csv Schreiben ----- #
    if writeOutput:
        exportData(dataSetList, outFilePath)

# ----- Berechnen der statistischen Angaben ----- #
    maxStressList = []
    maxStrainList = []
    yModulusList = []

    for dSet in dataSetList:
        maxStressList.append(dSet.maxStress)
        maxStrainList.append(dSet.maxStrain)
        yModulusList.append(dSet.youngsModulus)

    # Umwandeln in Vektoren
    maxStressVector = np.array(maxStressList)
    maxStrainVector = np.array(maxStrainList)
    yModulusVector = np.array(yModulusList)

    # Berechnen der max. Spannng und der dazugehörigen Dehnung
    maxStress = maxStressVector.max()
    idx = int(np.where(maxStressVector == maxStress)[0])
    strainOfMaxStress = maxStrainVector[idx]

    # Berechnen der max. Dehnung
    maxStrain = maxStrainVector.max()

    # Berechnen der Mittelwerte und Standartabweichungen
    meanMaxStress = np.mean(maxStressList)
    meanMaxStrain = np.mean(maxStrainList)
    meanYModulus = np.mean(yModulusList)
    stdevMaxStress = np.std(maxStressList)
    stdevMaxStrain = np.std(maxStrainList)
    stdevYModulus = np.std(yModulusList)

# ----- Print ----- #
    print('Parameterausgabe:')

    for dSet in dataSetList:
        print(dSet.name, end=': ')
        print('MaxSpannung =', '%5.2f' % dSet.maxStress, end=' MPa ;  ')
        print('Dehnung(MaxSpannung) =', '%5.2f' % dSet.maxStrain, end=' % ;  ')
        print('E-Modul =', '%5.2f' % dSet.youngsModulus, 'MPa')

    print()
    print('Max(MaxSpannung) =', '%5.2f' % maxStress, end=' MPa ;  ')
    print('Dehnung(Max(MaxSpannung)) =', '%5.2f' % strainOfMaxStress, end=' % ;  ')
    print('Max(Dehnung(MaxSpannung)) =', '%5.2f' % maxStrain, '%')
    print('Mittel(MaxSpannung) =', '%5.2f' % meanMaxStress, end=' MPa ;  ')
    print('Mittel(Dehnung(MaxSpannung)) =', '%5.2f' % meanMaxStrain, end=' % ;  ')
    print('Mittel(E-Modul) =', '%5.2f' % meanYModulus, 'MPa')
    print('St.Abw.(MaxSpannung) =', '%5.2f' % stdevMaxStress, end=' MPa ;  ')
    print('St.Abw.(Dehnung(MaxSpannung)) =', '%5.2f' % stdevMaxStrain, end=' % ;  ')
    print('St.Abw.(E-Modul) =', '%5.2f' % stdevYModulus, 'MPa')

# ----- Plot ----- #
    cmap = pyplot.get_cmap(COLORMAP)
    colorSet = iter(cmap(np.linspace(0, 0.9, len(dataSetList))))

    for dSet in dataSetList:
        if customColor:
            pyplot.plot(dSet.strainVector, dSet.stressVector, label=dSet.name, color=dSet.color)
        else:
            pyplot.plot(dSet.strainVector, dSet.stressVector, label=dSet.name, color=next(colorSet))

    pyplot.title('Spannungs-Dehnungs-Diagramm')
    pyplot.xlabel('Dehnung [%]')
    pyplot.ylabel('Spannung [MPa]')
    pyplot.grid(True)
    pyplot.legend()
    pyplot.show()

# ----- End-Prompt ----- #
    print('')
    input('Programm fertig. Zum Beenden Enter drücken.')
