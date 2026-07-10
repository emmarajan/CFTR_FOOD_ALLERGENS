library(alakazam)
library(tigger)
library(shazam)
library(igraph)
library(dplyr)
library(plyr)
library(ggpubr)
library(cowplot)
library(reshape2)
library(ggplot2)
library(purrr)
rootDir <- "/srv/GT/analysis/p3482/FN.p3482/"
setwd(rootDir)
sampleNames <- grep("FN",basename(list.dirs(path = ".", recursive = F)), value = T)
prepareDataForAirrSeqReport <- function(sampleName) {
  actualName <- gsub("FN.p3482.","",sampleName)
  setwd(file.path("/srv/GT/analysis/p3482/FN.p3482/", sampleName))
  
  
  ### ALAKAZAM PART
  
  # Load and subset data
  db <- data.frame(readChangeoDb(file.path(actualName, sprintf("%s_germ-pass.tsv", actualName))))
  # Calculate and plot rank-abundance curve
  estimAbund <- estimateAbundance(db, group="prcons")
  
  
  # Generate Hill diversity curve
  hillDiversity <- alphaDiversity(db, group="prcons")
  diversityDF <- data.frame(hillDiversity@diversity)
  diversityDF_Q1 <- select(filter(diversityDF,q==1),c("prcons","d"))
  diversityDF_Q1$sample <- as.factor(actualName)
  diversityDF_Q1$group <-   as.factor(gsub("-","",gsub('[0-9]+', '', actualName)))
  
  # Calculate CDR3 amino acid properties
  p <- aminoAcidProperties(db,
                           seq="junction", nt=T, trim=T,
                           label="CDR3")
  aminoAcidInfo <- melt(select(p,grep("CDR3",colnames(p),value = T)))
  aminoAcidInfo$sample <-  as.factor(actualName)
  aminoAcidInfo$group <-   as.factor(gsub("-","",gsub('[0-9]+', '', actualName)))
  meanAminoAcidInfo <- aggregate(value~variable+group+sample, aminoAcidInfo, mean)
  
  aminoAcidInfoIGG <- melt(select(p,c("prcons", grep("CDR3",colnames(p),value = T))))
  aminoAcidInfoIGG <- aminoAcidInfoIGG[aminoAcidInfoIGG$prcons=="Human-IGHG",]
  aminoAcidInfoIGG$prcons <- gsub("Human-","",aminoAcidInfoIGG$prcons)
  
  # V family usage by isotype and clone
  v <- countGenes(db, 
                  gene="v_call_genotyped",
                  groups="prcons", clone="clone_id",
                  mode="family")
  isotypeComp <- data.frame(v)
  isotypeComp$sample <-  as.factor(actualName)
  isotypeComp$group <-  as.factor(gsub("-","",gsub('[0-9]+', '', actualName)))
  
  # Calculate total mutation frequency
  TMF <- observedMutations(db, regionDefinition=NULL, frequency=T, combine = T, nproc=4)
  z <- collapseClones(TMF)
  TMF <- TMF[grep(",",TMF$v_call_genotyped, invert = T),]
  TMF$geneFamily <- sapply(TMF$v_call_genotyped, function(z) unlist(strsplit(z, "-"))[1])
  TMF <- TMF[,c("prcons","mu_freq","geneFamily")]
  TMF$sample <- as.factor(actualName)
  TMF$group <- as.factor(gsub("-","",gsub('[0-9]+', '', actualName)))
  TMF$prcons <- gsub("Human-","",TMF$prcons)
  # Calculate clonal consensus and selection by clone
  
  b <- calcBaseline(z, regionDefinition=IMGT_V)
  # Combine selection scores for isotypes
  densitiesForPlot <- groupBaseline(b, groupBy="prcons")
  selection_plot <- plot(densitiesForPlot, "prcons", sigmaLimits=c(-1, 1), silent=T)
  selectionDF <- selection_plot$data
  selectionDF$sample <-  as.factor(actualName)
  selectionDF$group <-   as.factor(gsub("-","",gsub('[0-9]+', '', actualName)))
  return(list(estimAbund=estimAbund,diversityDF_Q1=diversityDF_Q1,
              aminoAcidInfo=meanAminoAcidInfo,aminoAcidInfoIGG=aminoAcidInfoIGG,
              isotypeComp=isotypeComp,mutationFrequency=TMF, 
              selectionDF=selectionDF, db=db))
}

listOfObjectsForReport <- lapply(sampleNames,prepareDataForAirrSeqReport)
saveRDS(listOfObjectsForReport,file.path(rootDir, "RobjectForSummaryReport.Rdata"))
