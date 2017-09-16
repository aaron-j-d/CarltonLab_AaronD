{\rtf1\ansi\ansicpg1252\cocoartf1404\cocoasubrtf130
{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\froman\fcharset0 Times-Roman;}
{\colortbl;\red255\green255\blue255;}
\margl1440\margr1440\vieww28600\viewh16500\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 AAPos.py readme\
\
Purpose\
 Python script that takes in multiple user inputs and prints out amino acid and their variants based on positions specified by user.  Returns a dictionary with information regarding the specified amino acid: zygosity and potential variation 
\f1\fs64 \

\f0\fs24 \
Prerequisites \
	- .vcf file path \
	- .gff file path\
\
Inputs \
	- .gff file path \
	-.vcf file path ( compatible with vcf made through bcftools and  genome analysis toolkit (gatk)\
	- User specified list of geneIDs from .gff file and positions \
		The format of the list should be geneID then a colon and comma separated positions.  		The geneID and positions should be separated by a semicolon from other geneIDs and 		positions.\
	- cutoff frequency for allele variation\
		-v <vcf file path>  -a <gatk  vcf file path>  -g <gff file path> -p <geneID and pos> \
		-f <cutoff frequency>\
	Example Input:\
		\
		-v \'93\'85/12330_pass_falciparum.q20.primary.sort.rg.bcftools.m.vcf\'94 -g \'93\'85/PlasmoDB-25_Pfalciparum3D7.gff\'94  -p \'93PF3DZ_0417200 : 16,51,59,108,164 ; PF3DZ_0810800: 436, 437,540,581, 613\'94 -f .4\
\pard\pardeftab720\li540\fi-540\partightenfactor0

\f1\fs56 \cf0 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \
\
Output\
	It is a dictionary with the key being the geneID_position.  The item is a list stating the zygosity, the reference and SNP codon, and the reference amino acid and the variant amino acid \
\
\pard\pardeftab720\li720\partightenfactor0
\cf0 ex. (\'91PF3D7_0417200_108', ['Heterozygous', 'AGC/AAC', 'S/N'])\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 \
\
How it works:  \
\
\pard\pardeftab720\li540\fi-540\partightenfactor0
\cf0 Step 1:  Extracting information from a 
\i .gff 
\i0  file: exon start, end position, strand direction \
Step 2 : Using information from 
\i .gff 
\i0 file, enter the 
\i .vcf
\i0  file 
\i  
\i0 to create a two sequences: a reference sequence and a variant sequence  \
Step 3: The sequences are transcribed, the specified codon is isolated and translated\
Step 4: the information is stored and returned in a dictionary \
\pard\pardeftab720\li720\partightenfactor0
\cf0 \
\
\
\

\f1\fs52 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \
\
\
	\
\
\
\
	}