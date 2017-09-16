import os
import Bio.Seq
import collections
from optparse import OptionParser

"""
enterGFFFile
inputs:  the gffFilePath and the geneID 

purpose:  the purpose of the function is to enter the gffFile and find the exon coordinates and strand direction for the specific geneID


output:  the returnlist output is a list that consists of the chromosome, geneID,  startPosition for the exon, the EndPos for the exon, and the strand direction



"""


def enterGFFFile(gffFilePath, geneID):
    returnlist = []
    with open(gffFilePath) as file:
        for line in file:
            line_delimiter = '\t'
            row = line.split(line_delimiter)
            if row.__len__() == 1:

                continue
            else:

                IDLine = row[8]
                IDLine_delimiter = ';'
                EightColumn_list = IDLine.split(IDLine_delimiter)
                IDname = EightColumn_list[0]

                if IDname.__contains__('exon_' + geneID):
                    bufferlist = []
                    chromosome = row[0]
                    bufferlist.append(chromosome)
                    bufferlist.append(IDname)
                    StartPos = row[3]
                    EndPos = row[4]
                    strandDirection = row[6]
                    bufferlist.append(StartPos)
                    bufferlist.append(EndPos)
                    bufferlist.append(strandDirection)
                    returnlist.append(bufferlist)

    return returnlist


"""
enterVCFFilePath
inputs: The inputs are the gffList, which is the list generated from the entergffFile function and the VCFFilePath

purpose: This function has two parts: in the first part it creates a chromosome list containing all the Nucleotides in the chromosome and then abbreviates that list 
        to contain only the nucleotides found in the exon 
        Secondly it takes the adjustedChromosomeList with all the nucleotides and SNPs and puts it in a organized list

output: The output of this function is a list containing a nucleotide sequence with all the references, a sequence with all the potential SNPs, and the strand direction for the exon

"""


def enterVCFFilePath(gffList, VCFfilePath, Freq_Boolean, cutOffFrequency):
    NucSeq = ""
    SNPNucSeq = ""
    ZygosityDict = {}
    counter = 0
    exonListLength = gffList.__len__()
    while counter < exonListLength:
        singleExonList = gffList[counter]

        singleExonChrom = singleExonList[0]
        singleExonStartPos = int(singleExonList[2])
        singleExonEndPos = int(singleExonList[3])
        singleExonStrandDirection = singleExonList[4]
        Chromosome_List = findChromosomeList(singleExonChrom, VCFfilePath)
        adjustedChromosomeList = ChromListRange(Chromosome_List, singleExonStartPos, singleExonEndPos)
        if adjustedChromosomeList == None:
            counter += 1
        if adjustedChromosomeList != None:

            adjustedChromosomeListLength = adjustedChromosomeList.__len__()
            counter1 = 0
            while counter1 < adjustedChromosomeListLength:
                singleChrom = adjustedChromosomeList[counter1]
                frequency = singleChrom[7]
                Zygosity = singleChrom[9][0:3]
                if VCFfilePath.__contains__(".gatk"):
                    frequency = singleChrom[9]
                Nucleotide = singleChrom[3]
                SNP = singleChrom[4]

                NucSeq += Nucleotide
                if SNP.__contains__('.'):
                    SNPNucSeq += Nucleotide

                    counter1 += 1
                else:
                    if Freq_Boolean == False:
                        if VCFfilePath.__contains__("bcftools"):
                            SNP_Freq = default_findFreq("bcftools", frequency)
                            DEFAULT = .4
                            if SNP_Freq < DEFAULT:
                                SNP = Nucleotide
                        if VCFfilePath.__contains__("gatk"):

                            SNP_Freq = default_findFreq("gatk", frequency)
                            DEFAULT = .4
                            if SNP_Freq < DEFAULT:
                                SNP = Nucleotide
                    if Freq_Boolean == True:
                        if VCFfilePath.__contains__("bcftools"):
                            optFreqList = optional_Freq("bcftools", frequency, Zygosity, cutOffFrequency, SNP, Nucleotide)
                            SNP = optFreqList[0]
                            Zygosity = optFreqList[1]

                        if VCFfilePath.__contains__("gatk"):
                            optFreqList = optional_Freq("bcftools", frequency, Zygosity, cutOffFrequency, SNP, Nucleotide)
                            SNP = optFreqList[0]
                            Zygosity = optFreqList[1]



                    SNPNucSeq += SNP
                    ZygosityDict[SNP +'_' + str(counter1+ 1)] = Zygosity



                    counter1 += 1
            counter += 1
    return [NucSeq, SNPNucSeq, singleExonStrandDirection,ZygosityDict]


def default_findFreq(filetype, frequency):
    if filetype == "bcftools":
        splitFreq = frequency.split(';')
        DP4 = splitFreq[splitFreq.__len__() - 2]
        DP4vals = DP4[4: DP4.__len__()].split(',')
        int_DP4vals = list_of_strings_to_floats(DP4vals)
        Val_Sum = float(sum(int_DP4vals))

        Val3 = int_DP4vals[2]
        Val4 = int_DP4vals[3]

        Freq_Alt = (Val3 + Val4) / Val_Sum
        return Freq_Alt
    if filetype == "gatk":
        splitFreq = frequency.split(':')
        AD = splitFreq[1]
        AD_split = AD.split(',')
        AD_secondVal = float(AD_split[1])
        DP = float(splitFreq[2])
        Freq_Alt = AD_secondVal / DP
        return Freq_Alt


def optional_Freq(filetype , frequency, Zygosity , cutOffFreq , SNPNuc, RefNuc):
    if filetype == "bcftools":
        splitFreq = frequency.split(';')
        DP4 = splitFreq[splitFreq.__len__() - 2 ]
        DP4vals = DP4[4 : DP4.__len__()].split(',')
        int_DP4vals = list_of_strings_to_floats(DP4vals)
        Val_Sum = float(sum(int_DP4vals))
        Val1 = int_DP4vals[0]
        Val2 = int_DP4vals[1]
        Val3 = int_DP4vals[2]
        Val4 = int_DP4vals[3]

        Freq_Alt = (Val3 + Val4) / Val_Sum
        Freq_Ref = (Val1 + Val2) / Val_Sum

        if Zygosity.__contains__('0/1')  and Freq_Alt < cutOffFreq:
            Zygosity = '0/0'
            return [RefNuc, Zygosity]


        if Zygosity.__contains__( '1/1')  and Freq_Ref > cutOffFreq:
            Zygosity = '0/1'
            return [SNPNuc,Zygosity]

        return [SNPNuc, Zygosity]

    if filetype == "gatk":
        splitFreq = frequency.split(':')
        AD = splitFreq[1]
        AD_split = AD.split(',')
        AD_firstVal = float(AD_split[0])
        AD_secondVal = float(AD_split[1])
        DP = float(splitFreq[2])
        Freq_Alt = AD_secondVal / DP
        Freq_Ref = AD_firstVal/DP
        if Zygosity == '0/1' and Freq_Alt < cutOffFreq:
            Zygosity = '0/0'
            return [RefNuc, Zygosity]

        if Zygosity == '1/1' and Freq_Ref > cutOffFreq:
            Zygosity = '0/1'
            return [SNPNuc, Zygosity]

        return  [ SNPNuc, Zygosity]

def list_of_strings_to_floats (list_of_strings):
    counter = 0
    list_of_ints = []
    while list_of_strings.__len__() >  counter:
        value =  float(list_of_strings[counter])
        list_of_ints.append(value)
        counter += 1
    return list_of_ints



"""
This is a helper function for enterVCFfilePath 

input: the chromosome specific to the geneID and the vcfFilePath

purpose:  creates a list of lists from the vcfFilePath and removes all the data that does not contain the specific chromosome "

output: returns a list with only the specified chromosome information"
"""


def findChromosomeList(chromosome, vcfFilePath):
    chromosomeList = []
    with open(vcfFilePath) as file:
        for line in file:
            line_delimiter = '\t'
            row = line.split(line_delimiter)
            if row.__contains__('#') | row.__len__() <= 1: continue

            vcfChrom = row[0]

            if vcfChrom != chromosome: continue
            if vcfChrom == chromosome:
                chromosomeList.append(row)
    return chromosomeList


"""
This is a helper function for enterVCFFilePath

input: the chromosomeList generated from findChromosomeList , the exonStartPos and exonEndPos extracted from the gffList 

purpose:  to now further simplify and shorten the chromosome list by finding the range of the list and comparing the range of the chromosome positions with the exon start/end positions

output:  retuns an adjustedChromosomeList with only the positions that are part of the exon"

"""


def ChromListRange(chromosomeList, exonStartPos, exonEndPos):
    FirstRow = chromosomeList[0]
    LastRow = chromosomeList[chromosomeList.__len__() - 1]
    ChromListFirstPos = int(FirstRow[1])
    ChromListLastPos = int(LastRow[1])
    ajdustedChromList = isinRange(exonStartPos, exonEndPos, ChromListFirstPos, ChromListLastPos, chromosomeList)
    return ajdustedChromList


"""
This is a helper function for ChromListRange

input: the exonStart and end Positions, the ChromosomeList start and end positions, and the chromosomelist generated from findChromosomeList

purpose: the purpose is to compare the ranges of the exon position and the ranges for the chromosomelist positions, and determines where the range for the abbreviated chromosome list is "

output:  returns the newChromList with only the positions that are part of the exons.  All the other positions not part of the exon are discarded
"""


def isinRange(exonStartPos, exonEndPos, ChromListStartPos, ChromListEndPos, ChromosomeList):
    newChromList = []
    inRange = False
    if (exonStartPos < ChromListStartPos and exonEndPos < ChromListEndPos) or (
                    exonStartPos > ChromListEndPos and exonEndPos > ChromListEndPos):
        returnList = [inRange, 0, 0]
        return None
    if exonStartPos > ChromListStartPos and exonEndPos < ChromListEndPos:
        inRange = True
        returnList = [inRange, exonStartPos, exonEndPos]
        ChromListStart_to_exonStartPos = exonStartPos - ChromListStartPos
        ExonEnd_to_ChromListEnd = ChromListEndPos - exonEndPos
        Exon_to_Exon = exonEndPos - exonStartPos
        newChromList = ChromosomeList[
                       ChromListStart_to_exonStartPos:ChromosomeList.__len__() - ExonEnd_to_ChromListEnd]

        return newChromList

    if (exonStartPos < ChromListStartPos and exonEndPos < ChromListEndPos) or (
                    exonStartPos == ChromListStartPos and exonEndPos <= ChromListEndPos):
        inRange = True
        returnList = [inRange, ChromListStartPos, exonEndPos]
        ExonEnd_to_ChromListEnd = ChromListEndPos - exonEndPos
        newChromList = ChromosomeList[0: ChromosomeList.__len__() - ExonEnd_to_ChromListEnd]
        return newChromList

    if exonStartPos >= ChromListStartPos and exonEndPos == ChromListEndPos:
        inRange = True
        returnList = [inRange, exonStartPos, ChromListEndPos]
        ChromListStart_to_exonStartPos = exonStartPos - ChromListStartPos
        newChromList = ChromosomeList[ChromListStart_to_exonStartPos: ChromosomeList.__len__() - 1]

        return newChromList


"""
input:  The seqList which is generated by the enterVCFFIlePath function which contains the ReferenceSeq , the SNPSequence, and the StrandDirection, the codon position specified by the user, 

        and the geneID specified by the user

purpose:  The purpose of the function is to Transcribe the sequence, then find the specific codon associated with the codon positon, translate the codon, and compare the codon generated from the SNPSequence to the codon generated  ReferenceSequence

output:  the output is a dictionary stating whether the AA is homozygous or heterozygous , the codon for the reference and snp seuqnces, and the AA associated with that codon" 
"""


def analyze_Sequences(SeqList, CodonPos, geneID):
    CodonAnalysisDict = {}
    RefNucSeq = SeqList[0]
    SNPNucSeq = SeqList[1]
    zygosityDict = SeqList[2]

    if RefNucSeq == '' or SNPNucSeq == '':
        print " No Seq found"
        return
    StrandDirection = SeqList[2]
    Transcribed_RefNucSeq = TranscribeSeq(RefNucSeq)
    Transcribed_SNPNucSeq = TranscribeSeq(SNPNucSeq)
    RefCodon = Isolate_Codon(Transcribed_RefNucSeq, StrandDirection, CodonPos)
    SNPCodon = Isolate_Codon(Transcribed_SNPNucSeq, StrandDirection, CodonPos)
    RefAA = TranslateCodon(RefCodon)
    SNPAA = TranslateCodon(SNPCodon)
    if RefCodon == SNPCodon:
        CodonAnalysisDict[geneID + '_' + str(CodonPos)] = ['Homozygous', RefCodon, RefAA]
    if RefCodon != SNPCodon:
        CodonAnalysisDict[geneID + '_' + str(CodonPos)] = ['Heterozygous', RefCodon + '/' + SNPCodon,
                                                           RefAA + '/' + SNPAA]
    return CodonAnalysisDict


"""
This is a helper function for the analyze_Sequence function

input:  The nucleotide sequence

Purpose:  to transcribe the nucleotide sequence

output:  The transcribed nucleotide sequence" 
"""


def TranscribeSeq(Sequence):
    TranscribedSeq = Bio.Seq.transcribe(Sequence)
    return TranscribedSeq


"""
This is a helper funtion for the analyze_Sequence function

input: the transcribedSequence, the stranddirection, and the specified codon position 

purpose:  to find the specific codon that corresponds with the codon position.  If the strand direction is '-', the reverse compliment is found and then the specific codon is found"

output: The singular codon associated wit the codon position
"""


def Isolate_Codon(Sequence, StrandDirection, CodonPos):
    split_string = lambda Str, n: [Str[i:i + n] for i in range(0, len(Str), n)]
    if StrandDirection == '+':
        CodonSeperatedSeq = split_string(Sequence, 3)
        SpecificCodon = CodonSeperatedSeq[CodonPos - 1]

    if StrandDirection == '-':
        ReverseComplimentSequence = Bio.Seq.reverse_complement(Sequence)
        CodonSeperatedSeq = split_string(ReverseComplimentSequence, 3)
        SpecificCodon = CodonSeperatedSeq[CodonPos - 1]
    return SpecificCodon


"""
This is a helper function for the analyze_Sequence function

input:  Specific codon from the isolate_codon function

purpose:  Translates the codon into an amino acid

output:  the amino acid associated with the codon
"""


def TranslateCodon(Codon):
    AA = Bio.Seq.translate(Codon)
    return AA


"""
input: the geneIDdictionary generated from the user input, the gffFilePath, the vcfFilePath

purpose:  Iterates through the dictionary and returns a dictionary containing the specific codon, amino acid, and whether that codon is homozygous or heterozygous"

output: returns  a dictionary from the values generated by the anyalze_sequences function 
"""


def iterate_throughGeneIDDict(geneIDDict, gffFilePath, vcfFilePath, frequencyBoolean, cutoffFreq):
    AnalysisDict = collections.OrderedDict()
    for geneID in geneIDDict:
        genePos = geneIDDict[geneID]
        genePos = genePos.split(',')

        gffList = enterGFFFile(gffFilePath, geneID)

        SeqList = enterVCFFilePath(gffList, vcfFilePath,frequencyBoolean, cutoffFreq)


        counter = 0
        while counter < genePos.__len__():
            AnalysisDict.update(analyze_Sequences(SeqList, (int(genePos[counter])), geneID))
            counter += 1
    return AnalysisDict


"""
input: User input for the geneID 

purpose:  create a dictionary from the geneID user input

output: returns a dictionary with the keys in the dictionary being the specific geneID and the keys in each items being the desired codon positions
"""


def userInput_to_dict(userInput):
    geneIDDict = {}
    userInput = userInput.replace(" ", "")
    splitUserInput = userInput.split(';')
    splitUserInput_length = splitUserInput.__len__()
    counter = 0
    while counter < splitUserInput_length:
        singleGene_Pos = splitUserInput[counter]
        splitSingleGeneColon = singleGene_Pos.split(':')

        splitSingleGene_Pos = splitSingleGeneColon[1].split(" ")
        geneIDDict[splitSingleGeneColon[0]] = splitSingleGene_Pos[0]
        counter += 1
    return geneIDDict




if __name__ == "__main__":

    parser = OptionParser('-v <vcf File Path> -a <gatk.vcf File Path.  -g <gff File Path> -p <gene ID> -f <cutoff allele frequency> ')

    parser.print_help()
    parser.add_option('-p', '--pos', type=str,
                      help="input gene ID and AA position, example input is: PF3D7_0417200 : 16, 51,59,108,164 ; PF3D7_0810800 : 436,437 ,540, 581, 613 ",
                      dest="geneID")
    parser.add_option('-v', '--vcf', type=str, help='input vcf file path', dest="vcfFilePath", )
    parser.add_option('-g', '--gff', type=str, help='input gff file path', dest="gffFilePath")
    parser.add_option('-a', '--gatk', type=str, help= 'input vcf-gatk file path', dest="gatkFilePath")
    parser.add_option('-f', '--freq', type =float, help= 'input a cutoff frequency for allele variants.  Default frequency set at 10%', dest="cutoffFreq")
    (options, args) = parser.parse_args()
    gffFilePath =options.gffFilePath
    vcfFilePath =options.vcfFilePath
    userinput =options.geneID
    gatkFilePath = options.gatkFilePath
    cutoffFreq = options.cutoffFreq
    geneIDDict = userInput_to_dict(userinput)
    if vcfFilePath == None:
        if cutoffFreq == None:
            freqBoolean = False
            cutoffFreq = .4
            x = iterate_throughGeneIDDict(geneIDDict, gffFilePath, vcfFilePath, freqBoolean, cutoffFreq)
            print x

        else:
            freqBoolean = True

            x = iterate_throughGeneIDDict(geneIDDict, gffFilePath, gatkFilePath, freqBoolean, cutoffFreq)
            print x


    if gatkFilePath == None:
        if cutoffFreq == None:
            freqBoolean = False
            cutoffFreq = .4
            x = iterate_throughGeneIDDict(geneIDDict, gffFilePath, vcfFilePath, freqBoolean, cutoffFreq)
            print x

        else:
            freqBoolean = True
            x = iterate_throughGeneIDDict(geneIDDict, gffFilePath, vcfFilePath, freqBoolean, cutoffFreq)
            print x






