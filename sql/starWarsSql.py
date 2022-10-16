import pandas as pd
import numpy as np
import requests
import glob
import re, os
import sqlite3

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
        # if s in urlMap.keys() : return urlMap[s]
        if s in urlMap.keys() : return s.split("/")[5]

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
            # if url in urlMap.keys() : l.append(urlMap[url]["data"][urlMap[url]["colIdentifier"]].values[0])
            if url in urlMap.keys() : l.append(url.split("/")[5])
        return l




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

    # looping over the different dataframe in order to
    #  write and clean them,
    # and fill our urlMap
    for name, df in data.items():

        # filling my urlMap
        for url in df.url.tolist():
            urlMap[url] = {"data": df[df.url == url], "colIdentifier":df.columns.tolist()[0]}
        df.url = df.url.apply(lambda x: x.split("/")[5] if len(x) > 0 else np.nan )

# Cleaning data by  replacing URLs by they table primary key, 
        columns = df.columns
        for col in columns:
            if col != "url" : df[col] = df.apply(lambda x: cleanUrl(x[col], urlMap), axis=1)
        
            # df[col] = df[col].replace("unknown", np.nan)
            df.rename({"url" :"id"},axis=1, inplace=True)
            df.replace(to_replace=[None, 'none', 'n/a', 'unknown'], value=np.nan, inplace=True)

        
    #  modification of our different dataframe to fit in sql table
    people = data["people"]
    films = data["films"]
    planets= data["planets"]
    species= data["species"]
    starships= data["starships"]
    vehicles= data["vehicles"]

    # people treatment
    # people['height'] = people['height'].apply(lambda x: int(x) if x.isdigit() else 0)
    # people['mass'] = people['mass'].apply(lambda x: int(x) if x.isdigit() else 0)
    
    starships_pilot= people.explode('starships')[['id','starships']].dropna()
    starships_pilot.columns = ['character_id', 'starship_id']

    vehicles_drivers = people.explode('vehicles')[['id', 'vehicles']].dropna()
    vehicles_drivers.columns = ['character_id', 'vehicle_id']

    characters_films = people.explode('films')[['id', 'films']]
    characters_films.columns = ['character_id', 'film_id']

    people = people.drop(columns=['homeworld', 'species', 'starships', 'vehicles', 'films', 'created', 'edited'])

    #  for films
    planets_films = films.explode('planets')[['id', 'planets']]
    planets_films .columns = ['film_id', 'planet_id']
    vehicles_films = films.explode('vehicles')[['id','vehicles']]
    vehicles_films .columns = ['film_id', 'vehicle_id']
    starships_films = films.explode('starships')[['id','starships']]
    starships_films .columns = ['film_id', 'starship_id']

    films_producers = pd.DataFrame(films.producer.str.split(',').tolist(), index=films.id).stack()
    films_producers = films_producers.reset_index()[[0, 'id']] 
    films_producers.columns = ['producer', 'film_id']

    films = films.drop(columns=['species', 'planets', 'vehicles', 'starships', 'producer', 'characters', 'created', 'edited'])

    # for vehicles
    vehicles = vehicles.drop(columns=['films', 'pilots', 'created', 'edited'])
    #  for starships
    starships= starships.drop(columns=['films', 'pilots', 'created', 'edited'])
    # for species
    species= species.drop(columns=['films', 'people', 'created', 'edited'])
    # for planets
    planets = planets.drop(columns=['films', 'residents', 'created', 'edited'])

    
    #  go to sql now

    conn = sqlite3.connect('starwars_Database.db')
    c = conn.cursor()

    c.execute(f"CREATE TABLE IF NOT EXISTS people ({', '.join(people.columns)} , PRIMARY KEY (id))")
    conn.commit()
    people.to_sql('people', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS films ({', '.join(films.columns)}, PRIMARY KEY (id))")
    conn.commit()
    films.to_sql('films', conn, if_exists='replace', index = False)
    
    c.execute(f"CREATE TABLE IF NOT EXISTS starships ({', '.join(starships.columns)} , PRIMARY KEY (id))")
    conn.commit()
    starships.to_sql('starships', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS vehicles ({', '.join(vehicles.columns)} , PRIMARY KEY (id))")
    conn.commit()
    vehicles.to_sql('vehicles', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS species ({', '.join(species.columns)} , PRIMARY KEY (id))")
    conn.commit()
    species.to_sql('species', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS planets ({', '.join(planets.columns)} , PRIMARY KEY (id))")
    conn.commit()

    planets.to_sql('planets', conn, if_exists='replace', index = False)
    c.execute(f"CREATE TABLE IF NOT EXISTS planets_films ({', '.join(planets_films.columns)})")
    conn.commit()
    planets_films.to_sql('planets_films', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS vehicles_films ({', '.join(vehicles_films.columns)})")
    conn.commit()
    vehicles_films.to_sql('vehicles_films', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS starships_films ({', '.join(starships_films.columns)})")
    conn.commit()
    starships_films.to_sql('starships_films', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS films_producers ({', '.join(films_producers.columns)})")
    conn.commit()
    films_producers.to_sql('films_producers', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS characters_films ({', '.join(characters_films.columns)})")
    conn.commit()
    characters_films.to_sql('characters_films', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS starships_pilot({', '.join(starships_pilot.columns)})")
    conn.commit()
    starships_pilot.to_sql('starships_pilot', conn, if_exists='replace', index = False)

    c.execute(f"CREATE TABLE IF NOT EXISTS vehicles_drivers ({', '.join(vehicles_drivers.columns)})")
    conn.commit()
    vehicles_drivers.to_sql('vehicles_drivers', conn, if_exists='replace', index = False)






if __name__ == '__main__':
    main()