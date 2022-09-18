import json
import pandas as pd
import numpy as np
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
"Laurent Garnier"
"Mioun"
]

def getDataFromJson(pathToFile):
    jsonData = {}
    with open(pathToFile) as json_file: jsonData= json.load(json_file)
    return jsonData


def getArtistData(df, artistList, artistData):
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
    jsonData = getDataFromJson("mpd.slice.0-999.json")
    # creating a dataframe for the playlist
    playList_df = pd.json_normalize(jsonData["playlists"])
    #  reducing the data frame to the column needed
    playList_df = playList_df[["name", "tracks"]]
    #  creating a dictionnary to store our searched value
    artistData = {}
    for artist in artistList: artistData[artist] = {"name":artist, "nbPlaylist":0, "nbTracks":0, "listeningTime":0}
    dfChunck = np.array_split(playList_df, 100)
    for tmpDf in dfChunck:
        artistData = getArtistData(tmpDf, artistList, artistData)

    resultDf= pd.DataFrame.from_dict(artistData).transpose()
    resultDf["listeningTime"]=resultDf["listeningTime"].apply(lambda x: round(x, 2))
    # print(resultDf)
    resultDf.to_csv("artist_stats.csv", sep=",", index=False)
    mostFindInPlaylist = resultDf["nbPlaylist"].max()
    haveMostTracks= resultDf["nbTracks"].max()
    mostListeningTime = resultDf["listeningTime"].max()
    print("the artist that appears the most in the playlist is : " + str(resultDf[resultDf["nbPlaylist"] == mostFindInPlaylist]["name"][0]) + " with " + str(mostFindInPlaylist) + " playlist")
    print("the artist that have the most tracks in the playlist is : " + str(resultDf[resultDf["nbTracks"] == haveMostTracks]["name"][0]) + " with " + str(haveMostTracks) + " tracks")
    print("the artist that have the most listening time (in minutes) in the playlist is : " + str(resultDf[resultDf["listeningTime"] == mostListeningTime]["name"][0]) + " with " + str(round(mostListeningTime,2)) + " minutes")

if __name__ == '__main__':
    main()