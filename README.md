# CarltonLab_AaronD
## Purpose of  AAPos.py
   Python script that takes in multiple user inputs and prints out amino acid and their variants based on positions specified by user.  Returns a dictionary with information regarding the specified amino acid: zygosity and potential variation 
## Prerequisites and file types
	 .vcf file path 
	 .gff file path
## Inputs
   1. .gff file path 
  2. .vcf file path ( compatible with vcf made through bcftools and  genome analysis toolkit (gatk)
	3.  User specified list of geneIDs from .gff file and positions 
	  - The format of the list should be geneID then a colon and comma separated positions.  		The geneID and positions should be separated      by a semicolon from other geneIDs and positions.
	4. cutoff frequency for allele variation
      - If no cutoff frequency is specified, it will set a default value of .4 
	
  
   > -v vcf file path  -a gatk  vcf file path  -g gff file path -p geneID and pos -f cutoff frequency
	
  Example Input:
		
	> -v “…/12330_pass_falciparum.q20.primary.sort.rg.bcftools.m.vcf” -g “…/PlasmoDB-25_Pfalciparum3D7.gff”  -p “PF3DZ_0417200 :        16,51,59,108,164 ; PF3DZ_0810800: 436, 437,540,581, 613” -f .4
  
  ## Outputs
  It is a dictionary with the key being the geneID_position.  The item is a list stating the zygosity, the reference and SNP codon, and the reference amino acid and the variant amino acid 
  
 > ex. (‘PF3D7_0417200_108', ['Heterozygous', 'AGC/AAC', 'S/N'])
 
 ## How it works
 Step 1:  Extracting information from a .gff  file: exon start, end position, strand direction 
 
Step 2 : Using information from .gff file, enter the .vcf file  to create a two sequences: a reference sequence and a variant sequence

Step 3: The sequences are transcribed, the specified codon is isolated and translated

Step 4: the information is stored and returned in a dictionary 
