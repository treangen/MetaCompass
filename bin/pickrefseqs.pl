#!/usr/bin/perl

#############################################
#
# Program: Pick reference genomes using MetaPhyler.
#
# Author: Bo Liu
#
# Tue Aug  7 21:19:05 EDT 2012
#
#############################################

use strict;
use warnings;
use FindBin qw($Bin);


#----------------------------------------#
# read command line options
#----------------------------------------#
my $fastafile = "";
my $outdir = 0;
my $nthreads = 0;
my $prefix ="mc";
if (scalar @ARGV == 3) {
    ($fastafile, $outdir, $nthreads) = @ARGV;
} else {
    Usage();
}
#----------------------------------------#


my $cmd = "";

# run metaphyler
print STDERR "# Run MetaPhyler\n";
$cmd = "perl $Bin/../src/metaphyler/metaphyler.pl $fastafile $outdir $nthreads";
print STDERR "$cmd\n";
system($cmd);
print STDERR "\n";

# select reference genomes
print STDERR "# Pick reference genomes based on MetaPhyler output\n";
$cmd = "perl $Bin/pickrefids.pl $outdir/$prefix.blastn 1 > $outdir/$prefix.refseq.ids";
print STDERR "$cmd\n";
system($cmd);
print STDERR "\n";


print STDERR "# Extract reference genome sequences\n";
$cmd = "$Bin/extractSeq $Bin/../refseq/bacgeno.fna $outdir/$prefix.refseq.ids > $outdir/$prefix.refseq.fna";
print STDERR "$cmd\n";
system($cmd);
print STDERR "\n";


exit;


sub Usage {
    die("
Usage:
       perl pickrefseqs.pl <FASTA> <outdir> <# threads>

Options:
       <FASTA>        DNA reads in FASTA format.
       <outdir>       Output directory.
       <# threads>    Used to run BLAST.

Output:
       MetaPhyler output:
             mc.blast[n/x]
                   Raw blast output.
             mc.classification
                   Classification results.
             mc.<genus|family|order|class|phylum>.taxprof
                   Taxonomy profiles at each level.

       Reference genomes:
             mc.refseq.fna

Description:
       This program first runs MetaPhyler to estimate the taxonomic composition.
       Then extract corresponding genomes for comparative assembly.

");
}
