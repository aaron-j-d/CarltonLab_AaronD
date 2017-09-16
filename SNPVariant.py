import csv
import io
import os
import subprocess
import shutil
from os.path import dirname, abspath


def convert_xlsx_to_csv(excelFile):
    parentDirectory = dirname(abspath(excelFile))
    excelFileBaseName = os.path.basename(excelFile)
    newBaseName = excelFileBaseName.replace('.xlsx', '.csv')
    newFilePath = os.path.join(parentDirectory, newBaseName)
    with io.FileIO(newFilePath, 'w') as file:
        command = "xlsx2csv {0}".format(excelFile)
        subprocess.call(command, stdout=file, shell=True)
        file.close()
    return newFilePath

def findColumn(excelcsvFile, columnTypeString):
    with open(excelcsvFile, 'rU') as excelFile:
        excel_reader = csv.reader(excelFile, delimiter=',')
        excelHeader = next(excel_reader)
        columnNum = 0
        XColumn = 0
        while columnNum < excelHeader.__len__():
            headerTitle = excelHeader[columnNum]
            if headerTitle != columnTypeString:
                columnNum += 1
                continue
            else:
                XColumn = columnNum
                break
        return XColumn


def matcher(CSVList, Column, Type):
    counter = 0

    rowNum = 0
    while rowNum < CSVList.__len__():
        singleRow = CSVList[rowNum]
        singleCategory_inRow = singleRow[Column]
        if singleCategory_inRow == Type:
            counter += 1
        rowNum += 1
    return counter


def findStartingPoint(CSVList, Column, Type):
    rowNum = 0
    while rowNum < CSVList.__len__():
        singleRow = CSVList[rowNum]
        singleCategory_inRow = singleRow[Column]
        if singleCategory_inRow == Type:
            return rowNum
        rowNum += 1
    return rowNum


def findEndingPoint(CSVList, Column, Type):
    startingPoint = findStartingPoint(CSVList, Column, Type)
    while startingPoint < CSVList.__len__():
        singleRow = CSVList[startingPoint]
        singleCategory_inRow = singleRow[Column]
        if singleCategory_inRow == Type:
            startingPoint += 1
            continue
        else:
            endingpoint = startingPoint
            return endingpoint


"""
Step 3:  Extract the proper information from the 6 column excel and match it with the fasta
"""


def findBaseinFasta(fastaFile, Chrom, Position):
    with open(fastaFile, 'rU') as fasta:
        lines = fasta.readlines()
        iterator = 0
        while iterator < lines.__len__():
            singleLine = lines[iterator]
            nextLine = lines[iterator + 1]
            if singleLine.__contains__(Chrom):
                print nextLine.__len__()
                Base = nextLine[Position]
                break
            iterator += 1
    fasta.close()
    return Base

def NucinFasta(fastaFile, Chrom,):
    x = False
    with open(fastaFile, 'rU') as fasta:
        lines = fasta.readlines()
        iterator = 0
        while iterator < lines.__len__():
            singleLine = lines[iterator]
            if singleLine.__contains__(Chrom):
                x = True
            iterator += 1
    return x

def FindNucSeqinFasta(fastaFile, Chrom):
    with open(fastaFile, 'rU') as fasta:
        lines = fasta.readlines()
        iterator = 0
        while iterator < lines.__len__():
            singleLine = lines[iterator]
            if singleLine.__contains__(Chrom):
                nextLine = lines[iterator + 1]
                nucSeq = nextLine
                break
            iterator += 1

    return nucSeq

def createNewSeq(oldSeq, PositionIndex, ReferenceBaseIndex, VariantIndex, singleChromList):
    ChromLength = 0
    while ChromLength < singleChromList.__len__():
        singleChromRow = singleChromList[ChromLength]
        Position = int(singleChromRow[PositionIndex]) - 1
        ReferenceBase = singleChromRow[ReferenceBaseIndex]
        Variant = singleChromRow[VariantIndex]
        print oldSeq[Position]
        if oldSeq[Position] == ReferenceBase:
            newSeq = oldSeq[:Position - 1] + Variant + oldSeq[Position + 1:]


            if newSeq == oldSeq:
                print 'Same'
            else:
                print "Different"


            ChromLength += 1

    return newSeq


def MatchinFasta(fastaFile, excelFile):
    user_input_Directory =raw_input("In what directory do you want the Files to go")
    if os.path.exists(user_input_Directory) == False:
        os.makedirs(user_input_Directory)
    ChromList = listChrom(fastaFile)
    iterator = 0
    while iterator < ChromList.__len__():
        singleChrom = ChromList[iterator]
        FastaFileDirectory = user_input_Directory + '/' + singleChrom +'.fasta'
        with io.FileIO(FastaFileDirectory, 'w') as file:
            file.close()
        iterator += 1

    excelCSVFile = convert_xlsx_to_csv(excelFile)
    RunColumnIndex = findColumn(excelCSVFile, "Run Name")
    ChromColumnIndex = findColumn(excelCSVFile, "Chrom")
    PositionColumnIndex = findColumn(excelCSVFile, "Position")
    RefColumnIndex = findColumn(excelCSVFile, "Ref")
    VariantColumnIndex = findColumn(excelCSVFile, "Variant")
    SampleIDColumnIndex = findColumn(excelCSVFile, "SampleID")
    with open(excelCSVFile, 'rU') as csvX:
        csv_reader = csv.reader(csvX, delimiter=',')
        csvRows = list(csv_reader)
        csvRows.pop(0)
        rowNum = 0

        while rowNum < csvRows.__len__():

            CSVRow = csvRows[rowNum]

            Run = CSVRow[RunColumnIndex]
            RunCount = matcher(csvRows, RunColumnIndex, Run)
            StartingRow = findStartingPoint(csvRows, RunColumnIndex, Run)
            EndingRow = StartingRow + RunCount

            modCSVList_SingleRun = csvRows[StartingRow:EndingRow]

            modCSVrowNum = 0
            while modCSVrowNum < modCSVList_SingleRun.__len__():
                singlemodCSVRow = modCSVList_SingleRun[modCSVrowNum]
                SampleID = singlemodCSVRow[SampleIDColumnIndex]
                SampleIDCount = matcher(modCSVList_SingleRun, SampleIDColumnIndex, SampleID)
                StartingRow1 = findStartingPoint(modCSVList_SingleRun, SampleIDColumnIndex, SampleID)
                EndingRow1 = StartingRow1 + SampleIDCount

                modCSVList_SingleBarcode = modCSVList_SingleRun[StartingRow1:EndingRow1]

                modCSVrowNum1 = 0
                while modCSVrowNum1 < modCSVList_SingleBarcode.__len__():
                    singlemodCSVRow1 = modCSVList_SingleBarcode[modCSVrowNum1]
                    Chromosome = singlemodCSVRow1[ChromColumnIndex]

                    ChromCount = matcher(modCSVList_SingleBarcode, ChromColumnIndex, Chromosome)
                    StartingRow2 = findStartingPoint(modCSVList_SingleBarcode, ChromColumnIndex, Chromosome)
                    EndingRow2 = StartingRow2 + ChromCount

                    modCSVList_SingleChrom = modCSVList_SingleBarcode[StartingRow2:EndingRow2]
                    singeChromRow = modCSVList_SingleChrom[0]
                    Chromosome = singeChromRow[ChromColumnIndex]
                    oldSeq = FindNucSeqinFasta(fastaFile, Chromosome)
                    newSeq = createNewSeq(oldSeq, PositionColumnIndex, RefColumnIndex, VariantColumnIndex,
                                          modCSVList_SingleChrom)
                    createNewFile(newSeq, SampleID, Run, Chromosome, user_input_Directory)
                    modCSVrowNum1 = EndingRow2

                modCSVrowNum = EndingRow1

            rowNum = EndingRow

    return user_input_Directory





def createNewFile(newSeq, SampleID, Run, Chromosome, Directory):
    fastaDirectory = Directory + '/' + Chromosome + '.fasta'
    with open(fastaDirectory, 'a+') as fasta:
        fasta.write('>' + SampleID +'_' + Run + "_"+ Chromosome + '\n')
        fasta.write(newSeq)

        
    fasta.close()






def listChrom(fastaFile):
    ChromList =[]
    with open(fastaFile,'rU') as fasta:
        lines = fasta.readlines()
        iterator = 0

        while iterator < lines.__len__():
            singleLine = lines[iterator]
            if singleLine.__contains__('>'):
                ChromList.append(singleLine[1:singleLine.__len__()-1])

            iterator += 1
    return ChromList

def listColumn(excelFile, ColumnType):
    csvFile = convert_xlsx_to_csv(excelFile)
    ColumnList = []
    with open(csvFile,'rU') as csv_f:
        reader = csv.reader(csv_f, delimiter=',')
        csvList = list(reader)
        csvList.pop(0)
        ColumnIndex = findColumn(csvFile,ColumnType)
        iterator = 0
        while iterator < csvList.__len__():
            singleRow = csvList[iterator]
            singleType= singleRow[ColumnIndex]
            if ColumnList.__contains__(singleType):
                ColumnList.remove(singleType)


            ColumnList.append(singleType)
            iterator += 1
    return ColumnList





def completeList(csvFile, Directory,fastafile):

    ChromList = listColumn(csvFile, "Chrom")
    SampleIDList = listColumn(csvFile,"SampleID")
    RunList = listColumn(csvFile, 'Run Name')
    ChromListCounter = 0
    while ChromListCounter < ChromList.__len__():
        singleChrom = ChromList[ChromListCounter]
        basename = singleChrom + '.fasta'
        ChromFasta = Directory + '/' + basename
        Sequence = FindNucSeqinFasta(fastafile,singleChrom)
        with open(ChromFasta,'a') as CF:
            RunCounter = 0
            while RunCounter < RunList.__len__():
                singleRun = RunList[RunCounter]
                IDCounter = 0
                while IDCounter < SampleIDList.__len__():
                    singleId = SampleIDList[IDCounter]
                    comboname = '>'+ singleId + '_' +singleRun + '_' + singleChrom
                    nucSeq = NucinFasta(ChromFasta,comboname)
                    if nucSeq == True:
                        print 'True'
                        IDCounter += 1

                    if nucSeq == False:
                        print 'False'
                        print comboname
                        CF.write(comboname + '\n')
                        CF.write(Sequence)
                        IDCounter +=1
                RunCounter+= 1
        ChromListCounter += 1













def countSeqInFasta(fastaFile):
    with open(fastaFile, 'rU') as fasta:
        lines = fasta.readlines()
        iterator = 0
        counter = 0
        while iterator < lines.__len__():
            singleLine = lines[iterator]
            if singleLine.__contains__('>'):
                counter += 1
                iterator += 1
            iterator += 1
    return counter

    





def Pipeline():
    user_input_fasta =raw_input("Input fasta file:")
    user_input_xcel =raw_input("Input raw variant xcel file")

    x = MatchinFasta(user_input_fasta,user_input_xcel)
    completeList(user_input_xcel,x,user_input_fasta)

    ChromList = listChrom(user_input_fasta)
    y = 0
    while y < ChromList.__len__():
        FastaDirectory = x + '/'+ChromList[y] +'.fasta'
        a = countSeqInFasta(FastaDirectory)
        print a
        print   ChromList[y]
        y += 1
    print listColumn(user_input_xcel,"Sample ID")




if __name__ == '__main__':

    Pipeline()
