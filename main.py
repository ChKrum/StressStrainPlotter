# Stress-Strain- PLotter V1.0
#
# Author: Christian Krumwiede
# Date: 23.08.21
#

import csv
import matplotlib.pyplot as pyplot
import numpy as np
import statistics as stat
import dataSet

if __name__ == '__main__':

    # ----- Init variables ----- #
    directoryPath = 'data\\'
    plotOnlyValid = False
    writeOutput = False
    customColor = False
    colorMap = 'turbo' # Available Colormaps see https://matplotlib.org/stable/tutorials/colors/colormaps.html

    dataSetList = []

    # ----- Start-up prompt ----- #
    print('Stress-Strain-Plotter V1.0')
    print('')
    print('Dieses Programm plotted alle Dateien die in "data/config.csv" spezifiziert sind in ein Diagramm.')
    print('')

    input0 = input('Nur die gültigen Messdateien plotten? (j/n): ')
    if input0 == 'j': plotOnlyValid = True

    input0 = input('Ausgabe in "data/0_StressStrainData.csv" schreiben? (j/n): ')
    if input0 == 'j': writeOutput = True

    input0 = input('Benutzerdefinierte Farben verwenden? (j/n): ')
    if input0 == 'j': customColor = True

    print('')
    print('Parameterausgabe:')

    # ----- Read-in config values ----- #
    configFilePath = directoryPath + 'config.csv'
    with open(configFilePath, 'r', newline='') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=';')

        # Skip first two rows
        for i in range(2):
            csvReader.__next__()

        for line in csvReader:
            number = int(line[0])
            width = float(line[1].replace(',', '.'))
            thickness = float(line[2].replace(',', '.'))
            lenght = float(line[3].replace(',', '.'))
            fOffset = float(line[4].replace(',', '.'))

            isValid = True
            if line[5] == 'nein':
                isValid = False

            color = line[6]
            fileName = line[7]

            newDataSet = dataSet.DataSet(number, width, thickness, lenght, fOffset, isValid, color, fileName)

            dataSetList.append(newDataSet)

    # ----- Remove non-valid data sets (if wanted) ----- #
    if plotOnlyValid:
        for dSet in dataSetList:
            if dSet.isValid == False: dataSetList.pop(dataSetList.index(dSet))

    # ----- Read-in data sets ----- #
    for dSet in dataSetList:
        filePath = directoryPath + dSet.fileName

        with open(filePath, 'r') as dSetFile:
            dispo0 = 0

            # Skip first three rows
            for i in range(3):
                dSetFile.readline()

            for line in dSetFile:
                lineValues = line.split()
                force = float(lineValues[1].replace(',', '.'))
                dispo = float(lineValues[2].replace(',', '.'))

                if dispo0 == 0:
                    dispo0 = dispo

                strain = ((dispo-dispo0)/(1000*dSet.length))*100
                stress = (force-dSet.fOffset)/(dSet.width*dSet.thickness)

                dSet.appendDataPoint(stress, strain)

    # ----- Calc all max/ length values ----- #
    for dSet in dataSetList:
        dSet.calcMax()
        dSet.calcYoungsModulus()
        dSet.calcSize()

    # ----- Write data to csv File ----- #
    if writeOutput:
        dataSetLengths = []

        for dSet in dataSetList:
            dataSetLengths.append(dSet.size)

        maxSize = max(dataSetLengths)

        outputFilePath = directoryPath + "0_StressStrainData.csv"

        with open(outputFilePath, 'w', newline='') as outputFile:
            csvWriter = csv.writer(outputFile, delimiter=';')

            csvRow = []

            for dSet in dataSetList:
                csvRow.append(dSet.number)
                csvRow.append(dSet.fileName)

            csvWriter.writerow(csvRow)
            csvRow.clear()

            for dSet in dataSetList:
                csvRow.append('Strain')
                csvRow.append('Stress')

            csvWriter.writerow(csvRow)

            for i in range(maxSize):
                csvRow.clear()

                for dSet in dataSetList:
                    if i > dSet.size-1:
                        csvRow.append(0)
                        csvRow.append(0)
                    else:
                        strain = str(dSet.strainList[i]).replace('.', ',')
                        stress = str(dSet.stressList[i]).replace('.', ',')
                        csvRow.append(strain)
                        csvRow.append(stress)

                csvWriter.writerow(csvRow)

    # ----- Plot data sets ----- #
    maxStressList = []
    maxStrainList = []
    yModulusList = []

    cmap = pyplot.get_cmap(colorMap)
    colorSet = iter(cmap(np.linspace(0, 0.9, len(dataSetList))))

    for dSet in dataSetList:
        if customColor:
            pyplot.plot(dSet.strainList, dSet.stressList, label=dSet.number, color=dSet.color)
        else:
            pyplot.plot(dSet.strainList, dSet.stressList, label=dSet.number, color=next(colorSet))

        maxStressList.append(dSet.maxStress)
        maxStrainList.append(dSet.maxStrain)
        yModulusList.append(dSet.youngsModulus)

        print('%02d' % dSet.number, end=': ')
        print('MaxStress =', '%5.2f' % dSet.maxStress, end='MPa ;  ')
        print('Strain(MaxStress) =', '%5.2f' % dSet.maxStrain, end='% ;  ')
        print('Y-Modulus =', '%5.2f' % dSet.youngsModulus, 'MPa')

    # Calc max, mean, standard deviation of the max value
    idx = maxStressList.index(max(maxStressList))
    maxMaxStress = maxStressList[idx]
    strainOfMaxMaxStress = maxStrainList[idx]
    maxMaxStrain = max(maxStrainList)
    meanMaxStress = stat.mean(maxStressList)
    meanMaxStrain = stat.mean(maxStrainList)
    meanYModulus = stat.mean(yModulusList)
    stdevMaxStress = stat.stdev(maxStressList)
    stdevMaxStrain = stat.stdev(maxStrainList)
    stdevYModulus = stat.stdev(yModulusList)

    print()
    print('MaxMaxStress =', '%5.2f' % maxMaxStress, end='MPa ;  ')
    print('Strain(MaxMaxStress) =', '%5.2f' % strainOfMaxMaxStress, end='% ;  ')
    print('MaxMaxStrain =', '%5.2f' % maxMaxStrain, '%')
    print('MeanMaxStress =', '%5.2f' % meanMaxStress, end='MPa ;  ')
    print('MeanMaxStrain =', '%5.2f' % meanMaxStrain, end='% ;  ')
    print('MeanYModule =', '%5.2f' % meanYModulus, 'MPa')
    print('StDevMaxStress =', '%5.2f' % stdevMaxStress, end='MPa ;  ')
    print('StDevMaxStrain =', '%5.2f' % stdevMaxStrain, end='% ;  ')
    print('StDevYModule =', '%5.2f' % stdevYModulus, 'MPa')


    pyplot.title('Stress strain plot')
    pyplot.xlabel('Strain [%]')
    pyplot.ylabel('Stress [MPa]')
    pyplot.grid(True)
    pyplot.legend()
    pyplot.show()

    # ----- End prompt ----- #
    print('')
    input('Programm fertig. Zum Beenden Enter drücken')