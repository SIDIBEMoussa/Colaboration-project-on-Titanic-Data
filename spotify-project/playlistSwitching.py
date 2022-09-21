import json, time
import pandas as pd
import numpy as np
import glob


def getDataFromJson(pathToFile):
    jsonData = {}
    with open(pathToFile) as json_file: jsonData= json.load(json_file)
    return jsonData


def getSongFirstPlaylist(df, track_uri):
    for index, row in df.iterrows():
                tracks = pd.DataFrame.from_dict(row["tracks"]).track_uri.tolist()
                if track_uri in tracks : return row["pid"]

        
def switchPlaylist(df, p1, t1, p2, t2, path, visitedPlaylist):

    p1Name = str(df[df.pid == p1].name.squeeze())
    
    p1Tracks= pd.DataFrame.from_dict(df[df.pid == p1].tracks.squeeze())[["pos", "track_uri", "track_name"]]
    p2Tracks= pd.DataFrame.from_dict(df[df.pid == p2].tracks.squeeze())[["pos","track_uri", "track_name"]]
    t1infos= p1Tracks[p1Tracks["track_uri"] == t1].head(1)
    # print(t1infos)
    t2infos= p2Tracks[p2Tracks["track_uri"] == t2].head(1)
    p1Candidat = p1Tracks[p1Tracks.pos.values > t1infos.pos.values]
    p2Candidat = p2Tracks[p2Tracks["pos"].values < t2infos.pos.values]
    t1Name = str(t1infos.track_name.values[0])
    
    path += p1Name + ":" + t1Name + "-> \n"
    if p1Candidat.track_uri.isin(p2Candidat.track_uri.tolist()).any() or p1 == p2:
        p2Name = str(df[df.pid == p2].name.squeeze())
        t2Name = str(t2infos.track_name.values[0])
        commonTracks = ""
        for tracks in p1Candidat.track_uri.tolist():
            if track in p2Tracks.track_uri .tolist():
                commonTracks = track
                break
        path += p1Name + ":" + commonTracks + "->" + p2Name + ":" + t2Name
        return path

    else:
        for index, row in df.iterrows():
            if not row["pid"] in visitedPlaylist:
                curentTracks = pd.DataFrame.from_dict(row["tracks"])[["pos","track_uri"]]
                if row["pid"] != p1 and p1Candidat.track_uri.isin(curentTracks .track_uri.tolist()).any() and p2Candidat.track_uri.isin(curentTracks .track_uri.tolist()).any() : 
                    newP1 = row["pid"]
                    visitedPlaylist.append(newP1)
                    # print(newP1)
                    newT1 = ""
                    lCur = curentTracks.track_uri.tolist()
                    lP1= p1Candidat.track_uri.tolist()
                    lP2= p2Candidat.track_uri.tolist()
                    for track in lCur:
                        if track in lP1 and track in lP2:
                            newT1= track
                            break
                    return switchPlaylist(df, newp1, newT1, p2, t2, path, visitedPlaylist)

                elif row["pid"] != p1 and p1Candidat.track_uri.isin(curentTracks .track_uri.tolist()).any()  and not p2Candidat.track_uri.isin(curentTracks .track_uri.tolist()).any() :
                    newP1 = row["pid"]
                    visitedPlaylist.append(newP1)
                    # print(newP1)
                    newT1 ="" 
                    for track in curentTracks .track_uri.tolist():
                        if track in p1Candidat.track_uri.tolist(): 
                            newT1 = track
                            break

                    return switchPlaylist(df, newP1, newT1, p2, t2, path, visitedPlaylist)

    print("should be finish, I hope it worked")
    print("path : ", path)

def main():
    jsonData = getDataFromJson("mpd.slice.0-999.json")
    # creating a dataframe for the playlist
    playList_df = pd.json_normalize(jsonData["playlists"])
    #  reducing the data frame to the column needed
    playList_df = playList_df[["name", "pid", "tracks"]]

    t1 = time.time()
    p1 =getSongFirstPlaylist(playList_df, "spotify:track:2Xcvt8NRLw0xbB3ClfW8MI")
    p2 =getSongFirstPlaylist(playList_df, "spotify:track:1WFOcz2CnLr2OP4o8HfK46")
    finalPath = switchPlaylist(playList_df, p1, "spotify:track:2Xcvt8NRLw0xbB3ClfW8MI", p2, "spotify:track:1WFOcz2CnLr2OP4o8HfK46", "", [])
    t2= time.time()
    print("execution time : ", str((t2-t1)/60))
    print(finalPath)



if __name__ == '__main__':
    main()