# Installing the required packages and dependencies
install.packages("BiocManager")
install.packages("forcats")
install.packages("stringr")
BiocManager::install("GEOquery")
BiocManager::install("limma")
BiocManager::install("pheatmap")

# Install GEOquery
if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

#BiocManager::install("GEOquery")

# Loading the required packages and dependencies
library("BiocManager")
library("forcats")
library("stringr")
library("GEOquery")
library("limma")
library("pheatmap")
library("dplyr")

library(dyplr)
library(GEOquery)
library(pheatmap)

get_file_name <- function(filename) {
  gse <- getGEO(filename=filename, destdir= "GDS Data Analysis")    # change my_id to the required dataset
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

  jpeg(filename= "static/visuals/pheatmap.jpeg", units = "px", width = 4000, height = 2451, res = 300)
  pheatmap(corMatrix,annotation_col=sampleInfo)
  dev.off()
}
