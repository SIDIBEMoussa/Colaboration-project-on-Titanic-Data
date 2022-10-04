import pandas as pd
import numpy as np
import requests
import glob
import re, os


#  global variable to use in all code
session = requests.Session()


# function getFullPageContent
# this function yield the json content of each pages for an api table
def getFullPageContent(url):
    pageData= session.get(url).json()
    yield pageData["results"]
    while pageData["next"] != None:
        pageData = session.get(pageData["next"]).json()
        yield pageData["results"]

# function getFullDataFromAPI
# this function get all the data from the api and convert each
# table into a dataframe
def getFullDataFromAPI(baseUrl):
    basePage = session.get(baseUrl).json()
    data = {}

    for k, v in basePage.items():
        data[k] = []
        for pageData in getFullPageContent(v): data[k].append(pd.json_normalize(pageData))

        data[k] = pd.concat(data[k])
    
    return data

# function getFullDataLocaly
# just a function to load the csv if you outputed it
def getFullDataLocaly(sourceFolder):
    data = {}
    fileList = glob.glob(sourceFolder + "*.csv")
    for file in fileList:
        data[file[7:file.rfind(".")]] = pd.read_csv(file)

    return data



# function cleanUrl
# this function turn all the url by it's value in other dataframe
def cleanUrl(s, urlMap, debug= False):
    if debug:
        print(s)
        print(type(s))
    if isinstance(s, list): s= str(s)
    if not isinstance(s, str ): return s
    if not "http" in s : return s
    nbBracket = s.count("[")
    if nbBracket == 0:
        if s in urlMap.keys() : return urlMap[s]

    elif nbBracket == 1 :
        l = []
        s = s[1:s.rfind("]")-1]
        s = s.replace("'", "").replace(" ", "").replace("[", "").replace("]", "")
        items = s.split(",")
        for url in items:
            
            url = url.replace(",", "")
            if url[-1] != "/" :
                s= s.replace(url, url+"/")
                url+= "/"
            # print(url)
            if url in urlMap.keys() : l.append(urlMap[url]["data"][urlMap[url]["colIdentifier"]].values[0])
            # if url in urlMap.keys() : 
                # s= s.replace(url, urlMap[url]["data"][urlMap[url]["colIdentifier"]].values[0])
        return l


#  function getDFDescription
# as is name indicate it, this methode print some basic and classic
#  information about the dataframe
def getDFDescription(name, df):
    print("Description of the dataframe : ", name)
    print("the dataframe looks like : \n "+ str(df.head(5)))
    print("nb records : "+ str(len(df)))
    print("nb columns : "+ str(len(df.columns)))
    print("The columns are : \n"+ str(df.columns))
    print("more infos : \n"+str(df.info()))
    print("for a bit of number : \n" + str(df.count()))
    try : 
        print("Some visualisation know : ")
        df.hist()
    except: print("unfortunatly, nothing to visualise")
    print("some statistics : ")
    print(df.describe())
# function to return the amount of unic value in a list
def getUniqueValueCount(l):
    return len(set(l))


def main():
    # creat a folder to write the csv if you want
    if not os.path.isdir("swData/"): os.mkdir("swData/")

    # get the url for the api
    urlAPI = "https://swapi.dev/api/"

    # get the api data and store it into a dictionnary
    data = getFullDataFromAPI(urlAPI)
    # data = getFullDataLocaly("swData/")
    # this dictionnary is used to clean the url in the dataframe
    urlMap = {}
    vecTorizedCleanURLFunction = np.vectorize(cleanUrl)

    # looping over the different dataframe in order to
    #  write and clean them,
    # and fill our urlMap
    for name, df in data.items():

        # filling my urlMap
        for url in df.url.tolist():
            urlMap[url] = {"data": df[df.url == url], "colIdentifier":df.columns.tolist()[0]}
        # df.drop('url', axis=1, inplace=True)


# Cleaning data by  replacing URLs by they table primary key, 
        columns = df.columns
        for col in columns:
            if col != "url" : df[col] = df.apply(lambda x: cleanUrl(x[col], urlMap), axis=1)
            df[col] = df[col].replace("unknown", np.nan)
            # df[col] = df[col].drop_duplicates()
            # df[col] = df[col].dropna()

        
# print some info about the dataframe and then write it
        getDFDescription(name, df)
        df.to_csv("swData/"+ name + ".csv", sep=",", index=False)

        # some manipulation on the different dataframes
    data["people"].mass = data["people"].mass.replace(",", ".")
    # print(data["people"].mass.replace(",", "."))
    data["people"].height= data["people"].height.replace(",", ".")
    data["people"][["height"]]=data["people"][["height"]].astype('float')
    # data["people"][["mass"]]=data["people"][["mass"]].astype('float')
        # finding the character that are taller than the avrage
    hightMean = data["people"].height.dropna().mean()
    print("taille moyenne des gens : " + str(hightMean))
    tallerPeople = data["people"].where(data["people"].height > hightMean)[["name", "height"]].dropna()
    smallerPeople = data["people"].where(data["people"].height < hightMean)[["name", "height"]].dropna()
    print("character smaller than the avrage : ")
    print(smallerPeople.value_counts())
    tallerGuy = tallerPeople[tallerPeople['height'] == tallerPeople['height'].max()]
    smallerGuy = smallerPeople[smallerPeople['height'] == smallerPeople['height'].min()]
    tallerGuyName=tallerGuy["name"].values[0]
    tallerGuyHeight=tallerGuy["height"].values[0]
    smallerGuyName=smallerGuy["name"].values[0]
    smallerGuyHeight=tallerGuy["height"].values[0]
    print("the tallest character is "  + tallerGuyName + " with a height of " + str(tallerGuyHeight) + " cm")
    print("the smallest character is "  + smallerGuyName + " with a height of " + str(smallerGuyHeight) + " cm")
    print("top 10 tallest character : ") 
    print(tallerPeople.sort_values(by=["height"], ascending=False).head(10))
    print("top 5 smallest character among th tallest ")
    print(tallerPeople.sort_values(by=["height"], ascending=False).tail(5))
    print("top 3 smallest character")
    print(smallerPeople.sort_values(by=["height"], ascending=True).head(3))
    nbCharactersInFilms = []
    for index, row in data["films"].iterrows():
        nbCharactersInFilms.append(getUniqueValueCount(row["characters"]))
    data["films"] = data["films"].assign(nbUniqueCharacters=nbCharactersInFilms)
    print(data["films"]["nbUniqueCharacters"])
    films2= data["films"].explode("characters")
    films2 = films2.merge(data["people"][["name"]], how='left',left_on='characters',right_on='name')
    # print(len(films2.characters[0]))
    print(films2['name'].value_counts())


    
if __name__ == '__main__':
    main()