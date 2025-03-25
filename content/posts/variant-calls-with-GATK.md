---
title: Variant calls with GATK
date: 2016-05-29
tags:
  - software
  - Julia
summary: Setting up a variant calling pipeline
draft: false
---

I had to replace a [CLC Bio](http://www.clcbio.com/) variant calling pipeline
with an open-source equivalent. These notes are mainly an update of another blog
post [Variant calling with
GATK](https://approachedinthelimit.wordpress.com/2015/10/09/variant-calling-with-gatk/).

# Tools Setup

1. Build and install (to ~/.local) [bwa](https://github.com/lh3/bwa)
1. Build and install [samtools](http://www.htslib.org/download/)
1. Download and extract [GATK](https://www.broadinstitute.org/gatk/) under non-comercial license
1. Download and extract [Picard Tools](http://broadinstitute.github.io/picard/)
1. Picard requires Java 1.8 so update to OpenJDK-1.8.72
1. Set environment variable to reference Picard

        :::shell
        export PICARD=~/Downloads/picard-tools-2.1.0/picard.jar

# Pipeline

1. Index the reference

        :::shell
        bwa index PAO1_reference.fasta

1. Sort the reference

        :::shell
        samtools faidx PAO1_reference.fasta

1. Create sequence dictionary

        :::shell
        java -jar $PICARD CreateSequenceDictionary \
         REFERENCE=PAO1_reference.fasta \
         OUTPUT=PAO1_reference.dict

1. Align reads using bwa

        :::shell
        bwa mem PAO1_reference.fasta \
         genomes/AZPAE12150_S4_L001_R1_001.fastq.gz \
         genomes/AZPAE12150_S4_L001_R2_001.fastq.gz > \
         pipeline_products/AZPAE12150_S4_L001.aln.sam

1. Sort SAM file, add fake ReadGroup IDs (otherwise will fail at GATK RealignerTargetCreator below) and convert to bam

        :::shell
        java -jar $PICARD AddOrReplaceReadGroups \
         I=pipeline_products/AZPAE12150_S4_L001.aln.sam \
         O=pipeline_products/AZPAE12150_S4_L001.sorted.bam \
         RGLB=kos1 \
         RGPL=illumina \
         RGPU=unit1 \
         RGSM=AZPAE12150 \
         SORT_ORDER=coordinate

1. Mark duplicates

        :::shell
        java -jar $PICARD MarkDuplicates \
         I=pipeline_products/AZPAE12150_S4_L001.sorted.bam\
         O=pipeline_products/AZPAE12150_S4_L001.dedup.bam \
         METRICS_FILE=pipeline_products/metrics.txt

1. Build bam index

        :::shell
        java -jar $PICARD BuildBamIndex INPUT=pipeline_products/AZPAE12150_S4_L001.dedup.bam

1. Create realignment targets

        :::shell
        java -jar ~/Downloads/GATK/GenomeAnalysisTK.jar -T RealignerTargetCreator \
        -R ../PAO1_reference.fasta -I AZPAE12150_S4_L001.dedup.bam \
        -o AZPAE12150_S4_L001.targetintervals.list

1. Indel realignment

        :::shell
        java -jar ~/Downloads/GATK/GenomeAnalysisTK.jar -T IndelRealigner \
         -R ../PAO1_reference.fasta -I AZPAE12150_S4_L001.dedup.bam \
         -targetIntervals AZPAE12150_S4_L001.targetintervals.list \
         -o AZPAE12150_S4_L001.realigned.bam

1. Call variants (takes ~10 minutes to run on a pair of 150M fastq.gz file )

        :::shell
        java -jar ~/Downloads/GATK/GenomeAnalysisTK.jar -T HaplotypeCaller \
         -R ../PAO1_reference.fasta -I AZPAE12150_S4_L001.realigned.bam \
         -ploidy 1 -stand_call_conf 30 -stand_emit_conf 10 \
         -o AZPAE12150_S4_L001.raw.vcf

1. Filter out SNPs (optional)

        :::shell
        java -jar ~/Downloads/GATK/GenomeAnalysisTK.jar -T SelectVariants \
         -R ../PAO1_reference.fasta -V AZPAE12150_S4_L001.raw.vcf -selectType SNP \
         -o AZPAE12150_S4_L001.snps.vcf

1. Convert to a tab separated file for easy dataframe loading

        :::shell
        java -jar ~/Downloads/GATK/GenomeAnalysisTK.jar -T VariantsToTable \
         -R ../PAO1_reference.fasta -V AZPAE12150_S4_L001.snps.vcf \
         -F POS -F REF -F ALT -F QUAL -o AZPAE12150_S4_L001.snps.tsv

# Wrapping in a script

I also put together a [Julia
script](https://gist.github.com/caryan/1a5624d8539c83d01cef2663b3bc2e7d) that
automates the whole pipeline.

# Performance

I don't have the experience to grade the quality of the SNP calling. Anecdotally
I seemed to run into a [reported
issue](http://gatkforums.broadinstitute.org/dsde/discussion/5422/why-is-haplotypecaller-not-calling-obvious-snps-by-default-but-requires-allownonuniquekmersinref)
where it seemed to miss SNPs at the beginning of a gene with lots of repeats.

In comparison to the CLC pipeline, some SNP set union/differences showed there
were about 27k they both called;  CLC called a few hundred that GATK did not and
GATK called a couple thousand that CLC did not.  Anecdotally, the extra calls
from GATK seemed to come from low depth of coverage region however some
primitive attempts to filter those using `SelectVariants` did not seem to
improve the overlap.
