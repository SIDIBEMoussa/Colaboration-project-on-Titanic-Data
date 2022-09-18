import json, time
import pandas as pd
import numpy as np
import glob

artistList =[
    "Britney Spears",
    "Zaz",
"Oumou",
"Kendrick Lamar",
"Pink",
"Muse",
"The Killers",
"Eminem",
"Taylor Swift",
"Harry Styles",
"Lara Fabian",
"Andrea Bocelli",
"Laurent Garnier",
]

# def getFullData(path, colToGet):
    # dfList = []
    # for jsonData in getJSonList(path):
        # dfList.append(pd.json_normalize(jsonData)[["name","tracks"]])
        # if len(dfList) % 100 == 0: print(str(len(dfList)) + "/" + str(len(fileList)) + "have been treated, continuing to get the data from the file before concatenating them")
    # print("assembling the data")
    # df = pd.concat(dfList, ignore_index=True)
    # print(df)
    # return df
    
def getDataFromJson(pathToFile):
    jsonData = {}
    with open(pathToFile) as json_file: jsonData= json.load(json_file)
    return jsonData

def getJSonList(path):
    fileList= glob.glob(path+'*.json')
    erroredFile = []
    # nbFileTreated = 0
    print("getting the data")
    for file in fileList:
        # print(file)
        try :
            json_file= open(file)
            jsonData = json.load(json_file)["playlists"]
            json_file.close()
            # nbFileTreated+=1
            # if nbFileTreated %100 == 0 : print(str(nbFileTreated)+ "/" + str(len(fileList)+ " have been treated, continuing to process"))
            yield jsonData
        except:
            erroredFile.append(file)

    if len(erroredFile) >0 : print("try with field that encountered an error")
    for file in erroredFile:
        print(file)
        json_file= open(file)
        jsonData = json.load(json_file)["playlists"]
        json_file.close()
        yield jsonData

def getArtistData(df, artistList, artistData):
    # artistData = {}
    # for artist in artistList: artistData[artist] = {"name":artist, "nbPlaylist":0, "nbTracks":0, "listeningTime":0}
    # looping over my dataframe rows to get the data I want
    for index, row in df.iterrows():
        playListTracks = pd.DataFrame.from_dict(row["tracks"])
        for artist in artistList:
            if artist in playListTracks["artist_name"].tolist():
                artistTracks = playListTracks[playListTracks["artist_name"] == artist]
                artistData[artist]["nbPlaylist"] +=1
                artistData[artist]["nbTracks"] += len(artistTracks)
                artistData[artist]["listeningTime"] += artistTracks["duration_ms"].sum() / 60000

    return artistData



def main():
    artistData = {}
    for artist in artistList: artistData[artist] = {"name":artist, "nbPlaylist":0, "nbTracks":0, "listeningTime":0}
    # creating a dataframe for the playlist
    t1 = time.time()
    for jsonData in getJSonList("data/"):
        playList_df = pd.json_normalize(jsonData)[["name", "tracks"]]
        dfChunck = np.array_split(playList_df, 100)
        for tmpDf in dfChunck:
            artistData = getArtistData(tmpDf, artistList, artistData)
    t2 =time.time()
    

    resultDf= pd.DataFrame.from_dict(artistData).transpose()
    resultDf["listeningTime"]=resultDf["listeningTime"].apply(lambda x: round(x, 2))
    print(resultDf)
    resultDf.to_csv("artist_stats_fullDataSet.csv", sep=",", index=False)
    mostFindInPlaylist = resultDf["nbPlaylist"].max()
    haveMostTracks= resultDf["nbTracks"].max()
    mostListeningTime = resultDf["listeningTime"].max()
    print("the artist that appears the most in the playlist is : " + str(resultDf[resultDf["nbPlaylist"] == mostFindInPlaylist]["name"][0]) + " with " + str(mostFindInPlaylist) + " playlist")
    print("the artist that have the most tracks in the playlist is : " + str(resultDf[resultDf["nbTracks"] == haveMostTracks]["name"][0]) + " with " + str(haveMostTracks) + " tracks")
    print("the artist that have the most listening time (in minutes) in the playlist is : " + str(resultDf[resultDf["listeningTime"] == mostListeningTime]["name"][0]) + " with " + str(round(mostListeningTime,2)) + " minutes")
    print("execution time : " + str(round((t2-t1) / 60, 2)) + " minutes")

if __name__ == '__main__':
    main()