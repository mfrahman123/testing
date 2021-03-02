# Installing the required packages and dependencies, uncomment if not using AWS
#install.packages("BiocManager")
#install.packages("forcats")
#install.packages("stringr")
#BiocManager::install("GEOquery")
#BiocManager::install("limma")
#BiocManager::install("pheatmap")
#BiocManager::install("plsgenomics")

# Install GEOquery
#if (!requireNamespace("BiocManager", quietly = TRUE))
# install.packages("BiocManager")

#BiocManager::install("GEOquery")

# Loading the required packages and dependencies
library("BiocManager")
library("forcats")
library("stringr")
library("limma")

#library(dpylr)
library(GEOquery)
library(pheatmap)
library(plsgenomics)


get_file_name <- function(filename) {

  gse <- getGEO(filename=filename, destdir=".")    # change my_id to the required dataset
  #gse <- getGEO(filename='GDS859.soft.gz', destdir=".")
  # check how many platforms used
  length(gse)

  # if more than one dataset is present, can analyse the other dataset by changing the number inside the [[...]]
  # e.g. gds <- gds[[2]]

  # Turning GDS object into an expression set object (using base 2 logarithms) and examining it
  eset <- GDS2eSet(gse, do.log2=TRUE)


  sampleNames(eset)
  featureData(eset)

  # Check the normalisation and the scales used
  ## exprs get the expression levels as a data frame and get the distribution
  summary(exprs(eset))



  # Inspect the clinical variables
  sampleInfo <- pData(eset)
  # Visualisation of Data and Exploratory Analyses
  # Sample clustering and Principal Components Analysis

  # Heatmap
  corMatrix <- cor(exprs(eset),use="c")

  # Print the rownames of the sample information and check it matches the correlation matrix
  rownames(sampleInfo)
  colnames(corMatrix)

  # Ensure rownames match the columns
  rownames(sampleInfo) <- colnames(corMatrix)

  jpeg(filename= 'static/visuals/pheatmap.jpeg', units = "px", width = 4000, height = 2451, res = 300)
  pheatmap(corMatrix,annotation_col=sampleInfo)
  dev.off()
}

error_fix <- function() {
  dev.off()
}

# for RA results
relative_activity <- function() {

  connec <- read.csv(file = 'connec_data.csv',header = FALSE)
  connec2 <- read.csv(file = 'connec_data.csv')
  connec <- data.matrix(connec, rownames.force = NA)
  connec <- as.matrix(connec)
  ge <- read.csv(file = 'ge_data.csv', header = FALSE)
  ge2 <- read.csv(file = 'ge_data.csv')
  ge <- data.matrix(ge, rownames.force = NA)
  ge <- as.matrix(ge)

  new <- TFA.estimate(CONNECdata = connec, GEdata = ge,ncomp=3,nruncv=0)
  TFAc <- new$TFA
  colnames(TFAc) <- colnames(ge2)
  rownames(TFAc) <- colnames(connec2)
  TFAc[is.nan(TFAc)] = 0
  TFAc <- TFAc[,-1]
  TFAc <- TFAc[-1,]
  TFAc
  #TFAc <- TFAc[ order(rowMeans(TFAc), decreasing = T), ] #doesn't work with datatables
  # Add a new column for the average relative activity
  TFAc <- cbind(TFAc, rowMeans(TFAc))
  # Rename column as average
  colnames(TFAc)[ncol(TFAc)] <- "AVERAGE"
  write.csv(TFAc, "relative.csv")

}

clear_env <- function() {
    rm(list = ls()) # clear the R environment

}
