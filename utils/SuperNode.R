##Author: Natalie Stanley
##Contact: NatalieStanley1318@gmail.com
##Prepared February 6, 2018
##Tested on R version 3.4.3

##Code Objective: 
#This code is for creating a super node representation of your data
#For a network with N nodes, this will agglomerate local regions of the network to create a new network of S nodes

##Inputs:
#Network: An igraph graph object. Note that this must be undirected and unweighted
#S: the number of super nodes

##Ouput:
# $SNAssn: This is an N-length vector of node to community assignments
# $SNNet: This is the S node super node network. This is returned as an igraph object

##Dependencies: 
#Please make sure you have igraph installed in R


SuperNode=function(Network,S){

library('igraph')

#Find seeds
Seeds=SeedsFromCore(Network,S)

#Grow out seeds
RelSN=GrowOut(Network,Seeds)

#Create the new network
BtwGraph=EdgeBtwGraph_Fastest(Network,RelSN,Seeds)

Out=vector(mode='list',length=2)
names(Out)=c('SNAssn','SNNet')
Out[[1]]=RelSN
Out[[2]]=BtwGraph
Out
}

####################
###Helping functions###
#####################

SeedsFromCore<-function(Graph,NumSN){
	#This function uses the K core to then iteratively pick high degree vertex and delete and create k core. 
	V(Graph)$Names=c(1:vcount(Graph))
	degVec=degree(Graph)
	#where we will store the high degree nodes 
	ToStore=c()
	for(i in 1:NumSN){
		MaxDeg=which(degVec==max(degVec))[1]
		ToStore=c(ToStore,V(Graph)$Names[MaxDeg])
		Graph=delete_vertices(Graph,v=MaxDeg)
		Graph=Get2Core(Graph)
		degVec=degree(Graph)

	}
	ToStore
}

##
Get2Core<-function(Graph){
	#This function uses the 2 core in order to choose the most interesting seeds. 
	MinDeg=1
	ToDelete=c()
	degVec=degree(Graph)
	while(MinDeg<2){
		ToDelete=which(degVec<2)
		Graph=delete_vertices(Graph,v=ToDelete)
		degVec=degree(Graph)
		MinDeg=min(degVec)
	}
	
	Graph

}

##
GrowOut<-function(graph,seeds){
#this function assigns the rest of the node to super nodes

ord=1
#create a vector to store supernode assignments
SNAssn=rep(0,vcount(graph))

#initializing some things
SNAssn[seeds]=seeds
UnAssignVec=which(SNAssn==0)
NumUnAssign=length(which(SNAssn==0))
TotalSN=length(seeds)+NumUnAssign
Change=1
SNDiff=1
MaxSN=5000

#keep going until everyone is unassigned or until we go at least 6 neighborhood orders out
while(NumUnAssign>0& SNDiff>0 & ord<6){
#Create a matrix to store the seed node assignments
SeedNodeMat=matrix(0,nrow=length(seeds),ncol=vcount(graph))

#in every iteration grow out see
Neigh=ego(graph,order=ord,nodes=seeds)

for(i in 1:length(Neigh)){
	SeedNodeMat[i,Neigh[[i]]]=1
}

 
Prop=length(which(colSums(SeedNodeMat)>1))/length(which(colSums(SeedNodeMat)>0))

#to each column of seed node mat
ToAssign=intersect(UnAssignVec,which(colSums(SeedNodeMat)>0))

#TempAssn=unlist(apply(SeedNodeMat,2,function(x) which(x==1)[sample(1:length(x[x==1]),1)]))
TempAssn=unlist(apply(SeedNodeMat,2,function(x) ChooseSeedSet(x,seeds)))

###record distribution of how many possible seeds nodes have to go to at each iteration###

SNAssn[ToAssign]=TempAssn[ToAssign]


##########updates#########
UnAssignVec=which(SNAssn==0)
OldNumUnAssn=NumUnAssign
NumUnAssign=length(which(SNAssn==0))
OldTotalSN=TotalSN
TotalSN=length(seeds)+NumUnAssign
SNDiff=abs(TotalSN-OldTotalSN)
Change=abs(NumUnAssign-OldNumUnAssn)
ord=ord+1
} ##while

#updating singletons at end
UAInd=which(SNAssn==0)
SNAssn[UAInd]=UAInd
SNAssn
}

###### Helper code########

ChooseSeedSet=function(Col,seeds){
NumberOfOnes=length(which(Col>=1))
if(NumberOfOnes>0){
ToSample=sample(1:NumberOfOnes,1)
OneInds=which(Col>0)
Final=seeds[OneInds[ToSample]]	
}

else{Final=0}
Final
}

######
Ord1Correct=function(Neigh,UnAssignVec,seeds,graph,SeedNodeMat,SNAssn){

RelNeigh=sort(unique(unlist(Neigh)))

#to each column of seed node mat
ToAssign=intersect(UnAssignVec,which(colSums(SeedNodeMat)>0))

##assign unambiguous nodes##
NonAmbig=which(colSums(SeedNodeMat)==1)
IntNonAmbigToAssn=intersect(ToAssign,NonAmbig)
if(length(IntNonAmbigToAssn>0)){
TempMat=as.matrix(SeedNodeMat[,IntNonAmbigToAssn],nrow=length(seeds))
Assns=apply(TempMat,2,function(x) seeds[which(x==1)])
SNAssn[IntNonAmbigToAssn]=Assns
}

##first pass is columns going to more than 1 place##
Ambig=which(colSums(SeedNodeMat)>1)

#intersect with the to assign
AmbigAndToAssn=intersect(Ambig,ToAssign)

if(length(AmbigAndToAssn)>1){

##get adjacency matrix###
SpAdj=get.adjacency(graph)
SpAdj=get.adjacency(graph)[c(AmbigAndToAssn,sample(AmbigAndToAssn,500))]

#compute distance matrix
DistMat=hamming(SpAdj)
DistMat=as.matrix(DistMat[1:length(AmbigAndToAssn),-c(1:length(AmbigAndToAssn))])

#get the assignments for the ambiguous and to assn
AmbigAssn=apply(DistMat,1,function(x) seeds[order(x)][1])

##update supernode assignments of ambiguous nodes
SNAssn[AmbigAndToAssn]=AmbigAssn
}
else{
SNAssn[AmbigAndToAssn]=sample(1:length(seeds),1,replace=FALSE)
}
SNAssn
}

######

hamming <- function(X) {
    D <- (1 - X) %*% t(X)
    D + t(D)
}

EdgeBtwGraph_Fastest=function(graph,SNMembers,seeds){
	graph=simplify(graph)

	SeedTemp=TurnToUniqueLab(seeds)
	SeedTemp

	#create NxS matrix
	IndMat=matrix(0,nrow=vcount(graph),ncol=max(SeedTemp))

	for(i in 1:length(seeds)){
		In=which(SNMembers==seeds[i])
		IndMat[In,i]=1
	}

	#get sparse adjacency matrix
	sp=get.adjacency(graph)
	NewAdj=t(IndMat)%*%sp%*%IndMat
	diag(NewAdj)=0
	NewAdj=as.matrix(NewAdj)
	NewGraph=graph.adjacency(NewAdj,mode='undirected',weighted=TRUE)
	NewGraph
}

TurnToUniqueLab=function(Vec){
	#the purpose of this function is to turn 
	#a vector of very large values to something that is smaller
	#for ex: if we had [9521 931 1034] it would convert to [1 2 3]

	UVals=sort(unique(Vec))
	Count=1
	FinalVec=rep(0,length(Vec))
	for(i in UVals){
		CInd=which(Vec==i)
		FinalVec[CInd]=Count
		Count=Count+1
	}


	FinalVec
}