import csv
import io
import os
import shutil
import subprocess
from os.path import dirname, abspath

import xlrd

print xlrd.__VERSION__

"""
STEP 1 of readcountmod
This part of the code creates the readcountfolder and creates readcount files from inputted bam , fasta, and region files and puts them in the readcounter folder

"""


# Checks to see if the directory exists
def doesdirectoryexist(path):
    if os.path.isdir(path):
        return True
    else:
        return False


# Checks to see if the path to file exists
def doespathexist(path):
    if os.path.exists(path):
        return True
    else:
        return False


# Checks to see if the fasta file exists
def isfilefasta(fasta):
    if fasta.endswith(".fasta"):
        return True
    else:
        print("The file does not end with .fasta")
        return False


# Checks to see if all the folders in the bam folder are either bam or bam.bai
def isfolderbamFolder(bamfolder):
    x = True
    for f in os.walk(bamfolder):
        y = f[1]
        y.extend(f[2])
        iterator = 0
        while iterator < y.__len__():
            if y[iterator].__contains__(".bam") | y[iterator].__contains__("bai") | y[iterator].__contains__(
                    ".DS_Store"):
                iterator += 1
                continue
            else:
                iterator += 1
    return x


def findfasta_in_RunFolder(RunFolder):
    files = os.listdir(RunFolder)
    iterator = 0
    while iterator < files.__len__():
        singleFile = files[iterator]
        if singleFile.__contains__(".fasta"):
            if singleFile.__contains__(".fai"):
                iterator += 1
                continue
            else:
                fastaFilePath = RunFolder + '/' + files[iterator]
                break

        else:
            iterator += 1
            continue
    return fastaFilePath


def findBed_in_RunFolder(RunFolder):
    files = os.listdir(RunFolder)
    iterator = 0
    while iterator < files.__len__():
        singleFile = files[iterator]
        if singleFile.__contains__(".bed"):
            bedFilePath = RunFolder + '/' + files[iterator]
            break
        else:
            iterator += 1
            continue
    return bedFilePath


"""
Turns run folder into a bam folder
"""


def BigRunFolder_to_BigBamFolder(BigRunFolder):
    BigRunFolder_basename = os.path.basename(BigRunFolder)
    BigRunFolder_directory = dirname(abspath(BigRunFolder))
    newDirectoryPath = BigRunFolder_directory.__add__("/" + BigRunFolder_basename + "BamFiles")
    if os.path.exists(newDirectoryPath):
        shutil.rmtree(newDirectoryPath)
    os.makedirs(newDirectoryPath)
    RunFolders = os.listdir(BigRunFolder)
    iterator = 0
    while iterator < RunFolders.__len__():
        singleRunFolder = RunFolders[iterator]
        singleRunFolderPath = BigRunFolder + '/' + singleRunFolder
        if singleRunFolder.__contains__(".DS_Store"):
            iterator += 1
            continue
        bamFolderPath = runfolder_to_bamfolder(singleRunFolderPath)

        iterator += 1
    return newDirectoryPath


def runfolder_to_bamfolder(runfolder):
    runfolder_basename = os.path.basename(runfolder)
    runfolder_directory = dirname(dirname(abspath(runfolder)))
    bigrunfolder_directory = dirname(abspath(runfolder))
    newFolder_basename = os.path.basename(bigrunfolder_directory).__add__("BamFiles/")
    newDirectoryPath = runfolder_directory.__add__("/" + newFolder_basename + runfolder_basename + "BamFolder")
    if os.path.exists(newDirectoryPath):
        shutil.rmtree(newDirectoryPath)
    os.makedirs(newDirectoryPath)
    for files in os.walk(runfolder):
        fileName = files[1]
        fileName.extend(files[2])
        iterator = 0
        while iterator < fileName.__len__():
            singleFile = fileName[iterator]
            if singleFile.__contains__(".bam") | fileName[iterator].__contains__("bai"):
                singleFilePath = runfolder + "/" + singleFile
                shutil.copy(singleFilePath, newDirectoryPath)
                iterator += 1
            else:
                iterator += 1
                continue
    BamFolderPath = newDirectoryPath
    return BamFolderPath




"""
Converting bams to readcounts
"""


def BigBamFolder_to_BigReadCountFolder(bigbamFolder):
    BigbamFolder_BaseName = os.path.basename(bigbamFolder)
    BigbamFolder_directory = dirname(abspath(bigbamFolder))
    new_BBF_basename = BigbamFolder_BaseName.replace("BamFiles", "toReadCount")
    newDirectoryPath = BigbamFolder_directory.__add__("/" + new_BBF_basename)
    if os.path.exists(newDirectoryPath):
        shutil.rmtree(newDirectoryPath)
    os.makedirs(newDirectoryPath)
    BamFolder = os.listdir(bigbamFolder)
    iterator = 0
    while iterator < BamFolder.__len__():
        singleBamFolder = BamFolder[iterator]
        singleBamFolderPath = bigbamFolder + "/" + singleBamFolder
        BigRunFolderDirectory = bigbamFolder.replace("BamFiles", "")
        RunName = singleBamFolder.replace("BamFolder", "")
        RunFolderDirectory = BigRunFolderDirectory + '/' + RunName
        fasta = findfasta_in_RunFolder(RunFolderDirectory)
        region = findBed_in_RunFolder(RunFolderDirectory)

        if singleBamFolder.__contains__(".DS_Store"):
            iterator += 1
            continue
        readcountfolderpath = bamReadCounter(singleBamFolderPath, fasta, region)
        iterator += 1
    return newDirectoryPath


# Loops through the bam folder and calls the bamreadcount function for each bam file
def bamReadCounter(bamfolder, fasta, region):
    parentDirectory = dirname(abspath(bamfolder))

    readcountfolderpath = parentDirectory.replace("BamFiles", "toReadCount").__add__(
        "/" + os.path.basename(bamfolder) + "toReadCount")
    if os.path.exists(readcountfolderpath):
        shutil.rmtree(readcountfolderpath)
    readcountFolder = os.makedirs(readcountfolderpath)
    if isfilefasta(fasta) != True & isfolderbamFolder(bamfolder) != True:
        print ("The file(s) you inputted are invalid")
        return IOError
    files = os.listdir(bamfolder)
    iterator = 0
    while iterator < files.__len__():
        singleBam = files[iterator]
        singleBamFilePath = bamfolder + "/" + singleBam
        if singleBam.__contains__("bai"):
            iterator += 1
            continue
        if singleBam.__contains__(".bam"):
            readcountfile = bamreadcount(singleBamFilePath, fasta, region)
            iterator += 1
            continue
        else:
            iterator += 1
            continue
    return readcountfolderpath


# Call the bam-readcount command for one bam file
def bamreadcount(bam, fasta, region):
    bamname = os.path.basename(bam)
    readcountname = bamname.replace(".bam", ".readcount")
    parentdirectory = dirname(dirname(abspath(bam)))

    readCountFolderPath = parentdirectory.replace("BamFiles", "toReadCount").__add__(
        "/" + os.path.basename(dirname(bam)) + "toReadCount/")
    newFileName = readCountFolderPath + readcountname
    with io.FileIO(newFileName, "w") as file:
        command = 'bam-readcount -l {0} -f {1} {2} '.format(region, fasta, bam)
        subprocess.call(command, stdout=file, shell=True)
        file.close()
    return file


"""
Step 2 : In the newly made readcountfolder replace all of the readcount file colons with tabs
"""


# Checks to see if the files in the inputted readcount folder are all .readcount
def isFolderReadCount(readcountfolder):
    x = True
    for f in os.walk(readcountfolder):
        y = f[1]
        y.extend(f[2])
        iterator = 0
        while iterator < y.__len__():
            if y[iterator].__contains__(".readcount") | y[iterator].__contains__(
                    ".DS_Store"):
                iterator += 1
                continue
            else:
                x = False
    return x


def BigReadCountFolder_to_BigReplaceColonFolder(BigReadCountFolder):
    BigReadCountFolder_basename = os.path.basename(BigReadCountFolder)
    BigReadCountFolder_directory = dirname(abspath(BigReadCountFolder))
    newDirectoryPath = BigReadCountFolder_directory.__add__("/" + BigReadCountFolder_basename + "TABBED")
    if os.path.exists(newDirectoryPath):
        shutil.rmtree(newDirectoryPath)
    os.makedirs(newDirectoryPath)
    ReadcountFolders = os.listdir(BigReadCountFolder)
    iterator = 0
    while iterator < ReadcountFolders.__len__():
        singleReadCountFolder = ReadcountFolders[iterator]
        singleReadCountFolderPath = BigReadCountFolder + "/" + singleReadCountFolder
        if singleReadCountFolder.__contains__(".DS_Store"):
            iterator += 1
            continue
        colonfolderpath = ReplaceColonFolder(singleReadCountFolderPath)
        iterator += 1
    return newDirectoryPath


# Iterates through the readcount folder and calls the ReplaceColonFile function
def ReplaceColonFolder(readcountfolder):
    if isFolderReadCount(readcountfolder) == False:
        print ("Folder contains non readcount  files ")
        return IOError
    else:
        parentDirectory = dirname(abspath(readcountfolder))
        readcountfolderTABBEDpath = parentDirectory.__add__("TABBED/" + os.path.basename(readcountfolder) + "TABBED")
        if os.path.exists(readcountfolderTABBEDpath):
            shutil.rmtree(readcountfolderTABBEDpath)
        readcountFolderTABBED = os.makedirs(readcountfolderTABBEDpath)
        files = os.listdir(readcountfolder)
        iterator = 0
        while iterator < files.__len__():
            singleReadCount = files[iterator]
            singleReadCountFilePath = readcountfolder + "/" + singleReadCount
            if singleReadCount.__contains__(".DS_Store"):
                iterator += 1
                continue
            else:
                readcountTABBEDfile = ReplaceColonFile(singleReadCountFilePath)
                iterator += 1
                continue
    return readcountfolderTABBEDpath


# Removes the colons in one file and replaces them with tabs to make the read count file a
# Tab delimited file so that it is easier to manipulate and edit
def ReplaceColonFile(readcount):
    readcountname = os.path.basename(readcount)
    readcountTabbedname = readcountname.replace(".readcount", "TABBED.txt")
    parentparentDirectory = dirname(dirname(abspath(readcount)))
    parentDirectoryBaseName = os.path.basename(dirname(abspath(readcount))).__add__("TABBED")
    readcountTABBEDFolderPath = parentparentDirectory.__add__("TABBED/")
    newFileName = readcountTABBEDFolderPath.__add__(parentDirectoryBaseName + "/") + readcountTabbedname
    with io.FileIO(newFileName, "w") as file:
        shutil.copyfile(readcount, newFileName)
        f1 = open(newFileName)
        for lines in f1:
            file.write(lines.replace(":", "\t"))
    file.close()

    return newFileName


"""
Step 3

This step removes many of the unnecessary columns of the readcount folder
"""


# Checks to see the if the folder is all .txt files
def isFoldertxt(readcountfolder):
    x = True
    for f in os.walk(readcountfolder):
        y = f[1]
        y.extend(f[2])
        iterator = 0
        while iterator < y.__len__():
            if y[iterator].__contains__(".txt") | y[iterator].__contains__(
                    ".DS_Store"):
                iterator += 1
                continue
            else:
                x = False
    return x


def BigTabbedFolder_to_BigCutColumnFolder(BigTabbedFolder):
    BigTabbedFolder_basename = os.path.basename(BigTabbedFolder).replace("TABBED", "CUT")
    BigTabbedFolder_directory = dirname(abspath(BigTabbedFolder))
    newDirectoryName = BigTabbedFolder_directory + "/" + BigTabbedFolder_basename
    if os.path.exists(newDirectoryName):
        shutil.rmtree(newDirectoryName)
    os.makedirs(newDirectoryName)
    TabbedFolders = os.listdir(BigTabbedFolder)
    iterator = 0
    while iterator < TabbedFolders.__len__():
        singleTabbedFolder = TabbedFolders[iterator]
        singleTabbedFolderDirectory = BigTabbedFolder.__add__("/" + singleTabbedFolder)
        if singleTabbedFolder.__contains__(".DS_Store"):
            iterator += 1
            continue
        cutColumnFolderPath = CutColumnFolder(singleTabbedFolderDirectory)
        iterator += 1
    return newDirectoryName


# Iterates through the tabbed ReadCountfolder and removes
# Many of the unnecessary columns in the readcount file
def CutColumnFolder(RCTfolder):
    if isFoldertxt(RCTfolder) == False:
        print ("Folder contains non txt  files ")
        return IOError
    else:
        parentDirectory = dirname(abspath(RCTfolder)).replace("TABBED", "CUT")
        cutcolumnpath = parentDirectory.__add__("/" + os.path.basename(RCTfolder).replace("TABBED", "CUT") + "/")
        if os.path.exists(cutcolumnpath):
            shutil.rmtree(cutcolumnpath)
        cutcolumnfolder = os.makedirs(cutcolumnpath)
        files = os.listdir(RCTfolder)
        iterator = 0
        while iterator < files.__len__():
            singletabbed = files[iterator]
            singletabbedPath = RCTfolder + "/" + singletabbed
            if singletabbed.__contains__(".DS_Store"):
                iterator += 1
                continue
            else:
                cutcolumnFile = CutColumnFile(singletabbedPath)
                iterator += 1
                continue

    return cutcolumnpath


# Removes columns for one specific .txtfile
def CutColumnFile(txtFile):
    txtFilename = os.path.basename(txtFile)
    cutcolumnname = txtFilename.replace(".txt", "cut.txt")
    parentparentDirectory = dirname(dirname(abspath(txtFile))).replace("TABBED", "CUT/")
    parentDirectory = os.path.basename(dirname((abspath(txtFile))))
    cutcolumnfolderpath = parentparentDirectory.__add__(parentDirectory.replace("TABBED", "CUT") + "/")
    newFileName = cutcolumnfolderpath + cutcolumnname
    with io.FileIO(newFileName, "w") as file:
        command = """ awk '{print $1"\t"$2"\t"$3"\t"$4"\t"$6"\t"$7"\t"$19"\t"$20"\t"$21"\t"$33"\t"$34"\t"$35"\t"$47"\t"$48"\t"$49"\t"$61"\t"$62"\t"$63}'""" + "  " + txtFile
        subprocess.call(command, stdout=file, shell=True)
    file.close()

    return newFileName


"""
Step 4
This final step removes a few more of the columns of the previous read count folder and adds a header
"""


def BigCutColumnFolder_toBigParsedFolder(BigColumnCutFolder):
    BigColumnCutFolder_basename = os.path.basename(BigColumnCutFolder).replace("CUT", "_Parsed")
    BigColumnCutFolder_directory = dirname(abspath(BigColumnCutFolder))
    newDirectoryName = BigColumnCutFolder_directory + '/' + BigColumnCutFolder_basename
    if os.path.exists(newDirectoryName):
        shutil.rmtree(newDirectoryName)
    os.makedirs(newDirectoryName)
    ColumnCutFolders = os.listdir(BigColumnCutFolder)
    iterator = 0
    while iterator < ColumnCutFolders.__len__():
        singleColumnCutFolder = ColumnCutFolders[iterator]
        singleColumnCutFolderDirectory = BigColumnCutFolder.__add__("/" + singleColumnCutFolder)
        if singleColumnCutFolder.__contains__("DS_Store"):
            iterator += 1
            continue
        ParsedFolderPath = FinalFolder(singleColumnCutFolderDirectory)
        iterator += 1
    return newDirectoryName


# Iterates through the eddited reacount files and calls the FinalFile method

def FinalFolder(CutFolder):
    parentDirectory = dirname(abspath(CutFolder)).replace("CUT", "_Parsed")
    basename = os.path.basename(CutFolder)
    x = os.path.basename(basename).replace("CUT", "")
    FinalFolderpath = parentDirectory.__add__("/" + x + "_Parsed/")
    if os.path.exists(FinalFolderpath):
        shutil.rmtree(FinalFolderpath)
    finalfolder = os.makedirs(FinalFolderpath)
    files = os.listdir(CutFolder)
    iterator = 0
    while iterator < files.__len__():
        singlecutfile = files[iterator]
        singcutfilePath = CutFolder + "/" + singlecutfile
        if singlecutfile.__contains__(".DS_Store"):
            iterator += 1
            continue
        else:
            singlecutfile = FinalFile(singcutfilePath)
            iterator += 1
            continue
    return FinalFolderpath


# Takes in one of the inputted eddited readcount files and adds a header
def FinalFile(CutFile):
    CutFilename = os.path.basename(CutFile)
    finalFileName = CutFilename.replace("TABBEDcut.txt", "_Parsed.txt")

    parentparentDirectory = dirname(dirname((abspath(CutFile)))).replace("CUT", "_Parsed")
    parentDirectory = dirname(abspath(CutFile)).replace("CUT", "_Parsed")

    finalfolderpath = parentparentDirectory + '/' + os.path.basename(parentDirectory)

    newFileName = finalfolderpath + '/' + finalFileName

    with io.FileIO(newFileName, 'w') as file:
        file.write("Gene\tPos\tRB\tDepth\tCount\tA-C\tA-Q\tC-C\tC-Q\tG-C\tG-Q\tT-C\tT-Q\n")

        command = """ awk '{print $1"\t"$2"\t"$3"\t"$4"\t"$5"\t"$8"\t"$9"\t"$11"\t"$12"\t"$14"\t"$15"\t"$17"\t"$18}'""" + "  " + CutFile
        subprocess.call(command, stdout=file, shell=True)
    file.close()

    return newFileName


"""

Part b Readcount  with processed results





"""


def is_folder_parsedreadcount(folder):
    x = True
    for file in os.walk(folder):
        y = file[1]
        y.extend(file[2])
        iterator = 0
        while iterator < y.__len__():
            if y[iterator].__contains__(".txt") | y[iterator].__contains__(
                    ".DS_Store"):
                iterator += 1
                continue
            else:
                print("The folder contains not .txt files")
                x = False
    return x


def is_file_excel(excel):
    if excel.endswith(".xlsx") | excel.endswith(".xls"):
        return True
    else:
        print("The file does not end with .xlsx")
        return False


def excel_to_csv(excelFile):
    if is_file_excel(excelFile) == False:
        print("Invalid file")
        return IOError
    else:
        with open(excelFile, "rb") as infile, open(excelFile.replace(".xls", ".csv"), 'wb') as outfile:
            in_txt = csv.reader(infile, delimiter='\t')
            out_csv = csv.writer(outfile)
            out_csv.writerows(in_txt)
    return excelFile.replace('.xls', '.csv')


def Bigtxtfolder_to_bigcsvfolder(bigtxtfolder):
    BigTxtFolder_basename = os.path.basename(bigtxtfolder)
    BigTxtFolder_directory = dirname(abspath(bigtxtfolder))
    newBasename = BigTxtFolder_basename.replace("_Parsed", "toCSV")
    newDirectoryName = BigTxtFolder_directory + '/' + newBasename
    if os.path.exists(newDirectoryName):
        shutil.rmtree((newDirectoryName))
    os.makedirs(newDirectoryName)
    TxtFolders = os.listdir(bigtxtfolder)
    iterator = 0
    while iterator < TxtFolders.__len__():
        singleTxtFolder = TxtFolders[iterator]
        singleTxtFolderDirectory = bigtxtfolder + '/' + singleTxtFolder
        if singleTxtFolder.__contains__("DS_Store"):
            iterator += 1
            continue
        csvfolderpath = txtfolder_to_csvfolder(singleTxtFolderDirectory)
        iterator += 1
    return newDirectoryName


def txtfolder_to_csvfolder(txtfolder):
    txtfolder_parentDirectory = dirname(abspath(txtfolder)).replace("_Parsed", "toCSV")
    csvFolderName = os.path.basename(txtfolder).replace("_Parsed", "toCSV")
    csvFolderpath = os.path.join(txtfolder_parentDirectory, csvFolderName)
    if os.path.exists(csvFolderpath) == True:
        shutil.rmtree(csvFolderpath)
    os.makedirs(csvFolderpath)
    files_in_txtfolder = os.listdir(txtfolder)
    iterator = 0
    print files_in_txtfolder.__len__()
    while iterator < files_in_txtfolder.__len__():
        singleFile = files_in_txtfolder[iterator]
        singleFilePath = os.path.join(txtfolder, singleFile)
        if singleFilePath.__contains__(".DS_Store"):
            iterator += 1
            continue
        if singleFilePath.__contains__(".txt"):
            csvfile = txtfile_to_csv(singleFilePath)
            shutil.move(csvfile, csvFolderpath)
            iterator += 1
            continue
    return csvFolderpath


def txtfile_to_csv(txtfile):
    csvfile = txtfile.replace('.txt', '.csv')
    basename = os.path.basename(csvfile)
    in_text = csv.reader(open(txtfile, "rb"), delimiter='\t')
    out_csv = csv.writer(open(csvfile, 'wb'))

    out_csv.writerows(in_text)
    return csvfile


def findexcel_in_RunFolder(RunFolder):
    files = os.listdir(RunFolder)
    iterator = 0
    while iterator < files.__len__():
        singleFile = files[iterator]
        if singleFile.__contains__("xls"):
            if singleFile.__contains__("summary") | singleFile.__contains__("matrix") | singleFile.__contains__("cov"):
                iterator += 1
                continue
            else:
                excelFilePath = RunFolder + '/' + files[iterator]
                break

        else:
            iterator += 1
            continue
    return excelFilePath


"""
Matches txt based on header
"""


def findBarcodeColumn(excelCSVfile):
    with open(excelCSVfile, 'rU') as excelFile:
        excel_reader = csv.reader(excelFile, delimiter=',')
        excelHeader = next(excel_reader)
        columnNum = 0
        BarcodeColumn = 0
        while columnNum < excelHeader.__len__():
            headerTitle = excelHeader[columnNum]
            if headerTitle != "Barcode":
                columnNum += 1
                continue
            else:
                BarcodeColumn = columnNum
                break
        return BarcodeColumn


def findChromColumn(excelCSVfile):
    with open(excelCSVfile, 'rU') as excelFile:
        excel_reader = csv.reader(excelFile, delimiter=',')
        excelHeader = next(excel_reader)
        columnNum = 0
        ChromColumn = 0
        while columnNum < excelHeader.__len__():
            headerTitle = excelHeader[columnNum]
            if headerTitle != "Chrom":
                columnNum += 1
                continue
            else:
                ChromColumn = columnNum
                break
        return ChromColumn


def findPosColumn(excelCSVFile):
    with open(excelCSVFile, 'rU') as excelFile:
        excel_reader = csv.reader(excelFile, delimiter=',')
        excelHeader = next(excel_reader)
        columnNum = 0
        PositionColumn = 0
        while columnNum < excelHeader.__len__():
            headerTitle = excelHeader[columnNum]
            if headerTitle != "Position":
                columnNum += 1
                continue
            else:
                PositionColumn = columnNum
                break
        return PositionColumn


def FindLineBigFolder(Bigreadcountfolder):
    readcountfolder = os.listdir(Bigreadcountfolder)
    iterator = 0
    while iterator < readcountfolder.__len__():
        singleReadCountFolder = readcountfolder[iterator]
        readcountFolderPath = Bigreadcountfolder + '/' + singleReadCountFolder
        if singleReadCountFolder.__contains__("DS_Store"):
            iterator += 1
            continue
        FindAppendLine_in_Folder(readcountFolderPath)
        iterator += 1
        continue


def FindAppendLine_in_Folder(readcountFolder):
    RunBaseName = os.path.basename(readcountFolder).replace("BamFoldertoReadCount_Parsed", "")
    RC_ParentDirectory = dirname(abspath(readcountFolder))
    RunFolder = RC_ParentDirectory.replace("toReadCount_Parsed", "") + '/' + RunBaseName
    excelfile = findexcel_in_RunFolder(RunFolder)
    csv_excelfilePath = excel_to_csv(excelfile)
    if is_folder_parsedreadcount(readcountFolder) == False:
        print "Incorrect readcountfolder input"
        return IOError
    if is_file_excel(excelfile) == False:
        print"File inputted is not an excel"
        return IOError

    csv_readcountFolderPath = txtfolder_to_csvfolder(readcountFolder)

    readcountfiles = os.listdir(csv_readcountFolderPath)
    iterator = 0
    while iterator < readcountfiles.__len__():
        singleFile = readcountfiles[iterator]
        singleFilePath = csv_readcountFolderPath + "/" + singleFile
        if singleFile.__contains__(".DS_Store"):
            iterator += 1
            continue
        else:
            findLine(singleFilePath, csv_excelfilePath)
            iterator += 1
            continue
    return csv_excelfilePath


def findLine(readcountCSVfile, excelCSVfile):
    appendheader(excelCSVfile, readcountCSVfile)

    RC_barcode = os.path.basename(readcountCSVfile)[:13]
    BarcodeColumnNum = findBarcodeColumn(excelCSVfile)
    ChromColumnNum = findChromColumn(excelCSVfile)
    PositionColumnNum = findPosColumn(excelCSVfile)
    tracker = 0

    with open(excelCSVfile, 'rU') as excelFile:
        excel_reader = csv.reader(excelFile, delimiter=',')
        excel_writer = csv.writer(excelFile, delimiter=',')
        excelrows = list(excel_reader)
        excelrowNumber = 0
        while excelrows.__len__() > excelrowNumber:
            singleExcelRow = excelrows[excelrowNumber]
            excelrowNumber += 1

            Barcode = singleExcelRow[BarcodeColumnNum]
            if Barcode == RC_barcode:
                Chrom = singleExcelRow[ChromColumnNum]
                Position = singleExcelRow[PositionColumnNum].replace('.0', '')
                with open(readcountCSVfile, "r+") as readCountFile:

                    readCount_Reader = csv.reader(readCountFile, delimiter=',')
                    readCount_Writer = csv.writer(readCountFile, delimiter=',')
                    rows = list(readCount_Reader)
                    rowNumber = 0
                    while rows.__len__() > rowNumber:
                        singleRow = rows[rowNumber]
                        readcountChrom = singleRow[0]
                        readcountPosition = singleRow[1]
                        if readcountChrom != Chrom:
                            if rows.__len__() == rowNumber + 1:
                                print rowNumber
                        if readcountChrom != Chrom:
                            rowNumber += 1
                            continue

                        if readcountChrom == Chrom:
                            if readcountPosition != Position:
                                rowNumber += 1
                            else:
                                returnrowval = rowNumber
                                returnexcelrowval = excelrowNumber - 1
                                print Barcode, Chrom, Position, "The Readcount row val is :", returnrowval, "and the excel row val is :", returnexcelrowval

                                appendLine(excelCSVfile, returnexcelrowval, readcountCSVfile, returnrowval)
                                break
                readCountFile.close()
    excelFile.close()


def appendheader(excelcsvfile, readcountcsvfile):
    with open(excelcsvfile, 'rU') as excelfile:
        with open(readcountcsvfile, 'rU') as readcountfile:
            excelReader = csv.reader(excelfile, delimiter=',')
            readcountReader = csv.reader(readcountfile, delimiter=',')
            excelList = list(excelReader)
            readcountList = list(readcountReader)
            excelHeader = excelList[0]

            readcountReader = readcountList[0]
            newHeader = excelHeader + readcountReader
            if newHeader.__len__() > 62:
                return None
            excelList[0] = newHeader
    with open(excelcsvfile, 'wb') as excelfile:
        excelwriter = csv.writer(excelfile, delimiter=',')
        excelwriter.writerows(excelList)
    excelfile.close()
    excelfile.close()


def appendLine(excelcsvfile, excelrowindex, readcountcsvfile, readcountrowindex):
    with open(excelcsvfile, 'rU') as excelfile:
        with open(readcountcsvfile, 'rU') as readcountfile:
            excelReader = csv.reader(excelfile, delimiter=',')
            excelList = list(excelReader)
            excelRow = excelList[excelrowindex]
            readcountReader = csv.reader(readcountfile, delimiter=',')
            readcountList = list(readcountReader)
            readcountRow = readcountList[readcountrowindex]
            excelOverrideRow = excelRow + readcountRow
            excelList[excelrowindex] = excelOverrideRow

    with open(excelcsvfile, 'wb') as excelfile:
        excelwriter = csv.writer(excelfile, delimiter=',')
        excelwriter.writerows(excelList)
    excelfile.close()
    excelfile.close()


def PipeLine():

    user_input_BigRunFolder = raw_input("Input Run Folder")
    BigBamFolderpath = BigRunFolder_to_BigBamFolder(user_input_BigRunFolder)
    BRCFP = BigBamFolder_to_BigReadCountFolder(BigBamFolderpath)
    x = BigReadCountFolder_to_BigReplaceColonFolder(BRCFP)
    y = BigTabbedFolder_to_BigCutColumnFolder(x)
    z = BigCutColumnFolder_toBigParsedFolder(y)

    shutil.rmtree(x)
    shutil.rmtree(y)



    FindLineBigFolder(z)






if __name__ == '__main__':
    PipeLine()