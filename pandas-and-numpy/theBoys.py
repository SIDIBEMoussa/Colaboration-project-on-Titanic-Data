import glob
import pandas as pd

def loadData():
    fileList= glob.glob("the_boys/"+'*.csv')
    dataList = []
    for file in fileList:
        df = pd.read_csv(file)
        df= df.assign(season =  [file[file.rfind("\\")+1:file.rfind("e")]] * len(df))
        df= df.assign(episode=  [file[file.rfind("e")+1:file.rfind(".")]]* len(df))
        df= df.assign(screenTime= df.end-df.start)
        dataList.append(df)

    return pd.concat(dataList, ignore_index=True)


def main():
    df= loadData()
    print(df.head())
    print(df)
    print("the characters that appear the most in the series are : ")
    print(df.character.value_counts())
    print("nb character in the serie: " + str(len(df.character.unique())))
    print("nb season in the serie: " + str(len(df.season.unique())))
    dfS1= df[df.season == "s01"]
    dfS2= df[df.season == "s02"]
    dfS3= df[df.season == "s03"]
    print("nb episode in season 1 : " + str(len(dfS1.episode.unique())))
    print("nb episode in season 2 : " + str(len(dfS2.episode.unique())))
    print("nb episode in season 3 : " + str(len(dfS3.episode.unique())))
    print("character that appear the most in season 1 is : " + str(dfS1["character"].value_counts()))
    aggregation_functions = {'screenTime': 'sum', 'nconst': 'first', 'character' : 'first'}
    season1MaxScreenTime = dfS1.groupby(dfS1['nconst']).aggregate(aggregation_functions).sort_values('screenTime', ascending = False)
    season2MaxScreenTime = dfS2.groupby(dfS2['nconst']).aggregate(aggregation_functions).sort_values('screenTime', ascending = False)
    season3MaxScreenTime = dfS3.groupby(dfS3['nconst']).aggregate(aggregation_functions).sort_values('screenTime', ascending = False)
    # print(season1MaxScreenTime )
    print("character that appear the most in season 1 as screen time is : " + str(season1MaxScreenTime.character.values[0])+ " with " + str(round(season1MaxScreenTime.screenTime.values[0] /60000, 2))+ " minutes")
    
    print("character that appear the most in season 2 is : " + str(dfS2.character.value_counts()))
    print("character that appear the most in season 2 as screen time is : " + str(season2MaxScreenTime.character.values[0])+ " with " + str(round(season2MaxScreenTime.screenTime.values[0] /60000, 2))+ " minutes")
    print("character that appear the most in season 3 is : " + str(dfS3.character.value_counts()))
    print("character that appear the most in season 3 as screen time is : " + str(season3MaxScreenTime.character.values[0])+ " with " + str(round(season3MaxScreenTime.screenTime.values[0] /60000, 2))+ " minutes")
    print("top 10 character in season 1 are : \n" + str(season1MaxScreenTime[["character", "screenTime"]].head(10)))
    print("top 10 character in season 2 are : \n" + str(season2MaxScreenTime[["character", "screenTime"]].head(10)))
    print("top 10 character in season 3 are : \n" + str(season3MaxScreenTime[["character", "screenTime"]].head(10)))
    # print(dfS1.nconst.unique())
    print ("character that disappear in s2 are : \n" +str(dfS1.character.compare(dfS2.character)))
    died = []
    justDisappear = []
    for char1 in dfS1.character.unique().tolist():
        if char1 not in dfS2.character.unique().tolist(): died.append(char1)

    for char2 in dfS2.character.unique().tolist():
        if char2 not in dfS3.character.unique().tolist() and not char2 in died: died.append(char2)
        elif char2 not in dfS3.character.unique().tolist() and char2 in died: 
            died.remove(char2)
            justDisappear.append(char2)

    # print("The characters that seamed to die are : " + str(died))
    # print("The characters vanish in season 2 but appear again in season 3 are : " + str(justDisappear))





if __name__ == '__main__':
    main()