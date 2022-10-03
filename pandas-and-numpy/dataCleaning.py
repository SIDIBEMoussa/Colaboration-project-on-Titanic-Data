import pandas as pd
import requests
import os
#  creat the directory where to store the data
if not os.path.isdir("dataCleaning/"): os.mkdir("dataCleaning/")

# setting link where to retreave the data
link = "http://app-sellaci.eu-central-1.elasticbeanstalk.com/"
r = requests.get(link)
print(r)

# converting the data in json, for dataframe convertion and / or better manipulation
data = r.json()

# creating a flaten datafram with the raw datas
dfData = pd.json_normalize(data)
print(data)
print(len(data))

# first investigation to look for commun keys
commonKeys = []
uncommonKeys = []
for k in data[0].keys():
    if k in data[1].keys() : commonKeys.append(k)
    else: uncommonKeys.append(k)

commonData = []
uncommonData = []
for d in data:
    tmpDict = {}
    tmpDict2= {}
    for k, v in d.items():
        if k in commonKeys : tmpDict[k] = v
        else: tmpDict2[k] = v
    commonData.append(tmpDict)
    uncommonData.append(tmpDict2)
# creating two flatend dataframe for the common values, and unique ones
df= pd.json_normalize(commonData)
df2= pd.json_normalize(uncommonData)
print(df)
print(df2)


# function tryToClean
# function that will try to clean the big mess of data
# this function hint to extract table from this dataset
def tryToClean(dfData):

    # search for "sub table"
    potentialTable = []
    # search for potential id that could help to defind table 
    potentialIDList = []
    colToRename = {}

    for col in dfData.columns:
        if "id" in str.lower(col) : potentialIDList .append(col)

        # after looking the data, a "." seams to indicate a subtable
        if "." in col :
            splited = col.split(".") 
            # tableName = col [:col.find(".")]
            tableName = splited[-2]
            # colName = col[col.find(".")+1:]
            colName = splited[-1]
            colToRename[col] = colName
            if not tableName in potentialTable : potentialTable.append(tableName)

    # if no potential table have been found, we consider the data as cleaned
    if len(potentialTable) == 0 :
        return

    dfColList = {}
    dfFullColList = {}
    dfList = {}
    dfColRenameList= {}
    for table in potentialTable: 
        dfList[table] = []
        dfColList[table] = []
        dfFullColList[table] = []
        dfColRenameList[table] = {}

    for col in dfData.columns:
        splited = col.split(".")
        fullCol = col
        tmpCol = col 
        if len(splited) >1 : tmpCol= splited[-2]+"."+splited[-1]
        for table in potentialTable:
            if table in tmpCol and not tmpCol in dfColList[table]: 
                dfColList [table].append(splited[-1])
                dfFullColList [table].append(fullCol)
                dfColRenameList[fullCol]= splited[-1]

    # creating and writing our dataframe according to the previous findings
    for k, v in  dfFullColList.items():
        print(k +  str(v)) 
        dfList[k] = dfData[v]
        # dfData = dfData.drop(v, axis=1)
        dfList[k] = dfList[k].rename(columns = dfColRenameList[k])
    fullColToRemove = []
    for colList  in dfFullColList.values():
        for col in colList: 
            if not col in fullColToRemove: fullColToRemove.append(col)

    dfData = dfData.drop(fullColToRemove, axis=1)
    dfData.to_csv("dataCleaning/" + k + ".csv", sep=",", index=False)
    dfList[k].to_csv("dataCleaning/remainingData.csv", sep=",", index=False)

    return dfList
    
# trying to clean the recovered data
dfList = tryToClean(dfData)