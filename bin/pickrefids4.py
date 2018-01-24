#!/usr/bin/env python

#############################################
#
# Program: Pick reference genomes based on
#          metaphyler output
#
# Author: Victoria Cepeda, Mathieu Almeida, Bo Liu,
#
# Thu Sep 28 07:55:00 EDT 2017
#
#############################################

import sys
import os
import operator


pathbin="/".join(os.path.realpath(__file__).split('/')[:-2])

#============================
#calculate median of list
#============================
def median2(L):
   median = 0
   sortedlist = sorted(L)
   lengthofthelist = len(sortedlist)
   centerofthelist = lengthofthelist / 2
   if len(sortedlist) % 2 == 0:
        temp = 0.0
        medianparties = []
        medianparties = sortedlist[centerofthelist -1 : centerofthelist +1 ]
        for value in medianparties:
            temp += value
            median = temp / 2
        return median
   else:
        return sortedlist[centerofthelist]
        
        
def median(L):
   if sum(L)>0:
         
         srt = sorted(L)
         n = len(L)
         mid = n//2
         
         if n % 2:
            return float(srt[mid])
         else:
            med = (srt[mid] + srt[mid-1]) / 2.0 
            return float(med)
   
   else:
      return 0.0        

#============================
#calculte average of list
#============================
def average(L):
    return( sum(L)/ float(len(L)))
 
#good
#mejor filtrar antes este archivo
#da marker[nc...]=largo, en otras palabras
#========================================
#initalize marker coverage arrays
#========================================
def init_marker_data(marker2coverage):
   marker2length={}
   mlength=0
   with open(pathbin + "/src/metaphyler/markers/markers.length", "rt") as markerfile:
   #with open("/Users/victoria/metacompass/new/bin/new_pick/markers.length", "rt") as markerfile:
      id=""
      for line in markerfile:
         items = line.split("\t")
         #print ("%s" % items)
         marker=items[0]
         #print ("%s" % id)
         mlength=int(items[1])
         #print ("%d" % mlength)
         #ref = "_".join(marker.split('_')[0:2])
         #print ("%s" % ref)
         if marker in marker2coverage:
            if marker in marker2length:
               marker2length[marker] += mlength
            else:
               marker2length[marker] = mlength
   #print ("%s" % marker2length)
   return marker2length

#?
#===========================================================
#extract blast information from the read to marker alignment
#===========================================================
def extract_marker_data(blast_filename):
   marker2coverage={}
   markertotalcount={}
   with open(blast_filename, "rt") as blastfile:
      for line in blastfile:
         items = line.split("\t")
         marker = items[1]
         #ref = "_".join(marker.split('_')[0:2])
         alglength = int(items[3])
         if marker in marker2coverage:
            marker2coverage[marker]+=alglength
         else:
            marker2coverage[marker]=alglength
         if marker in markertotalcount:
            markertotalcount[marker] += 1
         else:
            markertotalcount[marker] = 1
#print ("%s  %s" % (marker2coverage,markertotalcount))
   return marker2coverage,markertotalcount

#nope...
#============================================================
#generate reference genome list data
#marker2coverage
#markertotalcount
#covthreshold ???
#============================================================
def create_refid_file(marker2coverage, marker2lenght, markertotalcount, covthreshold,refid_filename,markercoverage_filename):
   total_ref_cov={}
   total_marker_cov={}
   list_ref_median_cov={}
   list_ref_avg_cov={}
   outfile = open(markercoverage_filename,'w')
   #calculate coverage per gene
   for marker in marker2coverage:#is ref not marker
      coverage= float(marker2coverage[marker]/marker2lenght[marker])  
      if coverage >= covthreshold:
         total_marker_cov[marker] = coverage       
   #prev_ref=list(total_marker_cov.keys())[0]
   #prev_ref="_".join(prev_ref.split('_')[0:2])
   prev_ref="NA"
   id_list=[]
   for marker, cov in sorted(total_marker_cov.items(), key=operator.itemgetter(1), reverse=True):
       #outfile.write( 'dict = ' + repr(dict) + '\n' )
       ref = "_".join(marker.split('_')[0:2])
       #if median_cov >= covthreshold:
       print ( "%s\t%.5f" % (marker, cov), file= outfile)  
       id_list.append(ref)
   outfile.close()
   outfile = open(refid_filename,'w')
   myset=set(id_list)
   for id in myset:
      print ("%s" % (id), file =outfile)
#list_species.append(species)
# %s/bin/pickrefseqs.pl {input} {output.out} {threads} {params.mincov} {params.readlen}  1>> {log} 2>&1"%(config["mcdir"])



#===========================
#MAIN
#===========================
def main():
#----------------------------------------#
# read command line options
#----------------------------------------#
   query = ""
   blast = "blastn"
   outdir=""
   prefix = "mc"
   nump = 0
   query  = sys.argv[1]
   outdir = sys.argv[2]
   nump   = sys.argv[3]
   covthreshold = float(sys.argv[4])
#----------------------------------------#
   ref = pathbin +"/src/markers/markers.refseq.dna"
   param = "-word_size 28"
# run blast
   cmd = "%s %s -num_threads %s -evalue 1e-10 -perc_identity 97 -outfmt 6 -max_target_seqs 100 -query %s -db %s > %s/%s.%s.all"%(blast,param,nump,query,ref,outdir,prefix,blast)
   print ("%s" % (cmd))
   os.system(cmd)
# filter blast
   cmd = "%s/bin/best-hits.py %s/%s.%s.all %s/%s.%s"%(pathbin,outdir,prefix,blast,outdir,prefix,blast)
   print ("%s" % (cmd))
   os.system(cmd)
    
#if (scalar @ARGV == 3) {
#{input} {output.out} {threads} {params.mincov} {params.readlen}

   blast_filename = outdir+"/"+prefix+"."+blast+".all"#sys.argv[1]
   refid_filename = outdir+"/"+prefix+".refseq.ids"#sys.argv[1]
   markercoverage_filename = outdir+"/"+prefix+ ".markercoverage.txt"#sys.argv[1]
   
   #coverage per marker gene or based on the all marker genes in a genome

   marker2coverage, markertotalcount = extract_marker_data(blast_filename)
   marker2length = init_marker_data(marker2coverage)
   create_refid_file(marker2coverage, marker2length, markertotalcount, covthreshold,refid_filename, markercoverage_filename)
   

   print ("# Extract reference genome sequences")
   cmd = "%s/bin/extractSeq %s/refseq/bacgeno.fna %s/%s.refseq.ids > %s/%s.refseq.fna"%(pathbin,pathbin,outdir,prefix,outdir,prefix)
   print ("%s" % (cmd))
   os.system(cmd)
          

if __name__ == '__main__':
    main()
 
