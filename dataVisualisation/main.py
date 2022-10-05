import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import requests
import folium
import json, os

def loadData(file):
    with open(file) as json_file:
        data = json.load(json_file)
        return data



def plotPieCaseRepartitionByContinent(df):
    continent = df.continent.dropna().unique().tolist()
    caseList = df.groupby(df.continent).total_cases.sum().values
    caseList = caseList / np.sum(caseList) * 100
    fig, ax1= plt.subplots()
    ax1.set_title("percentage repartition of total covid cases by continent")
    ax1.axis('equal')
    ax1.pie(caseList, labels=continent, autopct='%1.1f%%',
        shadow=True, startangle=90)
    fig.savefig("figures/piechartTotalCovidCases.png")
    plt.show()
    plt.close()



def plotCaseRepartitionByContinent(df):
    continent = df.continent.dropna().unique().tolist()
    caseList = df.groupby(df.continent).total_cases.sum().values
    plt.title('Continantal total case distribution')
    
    plt.xlabel("Continent")
    plt.ylabel("Total cases")
    plt.bar(continent , caseList, color = "purple")
    plt.show()
    plt.savefig("figures/continentalTotalCaseRepartition.png")
    plt.close()


def plotTotalCasesOverTimeForCountry(df, country):
    df = df.assign(realDate = pd.to_datetime(df.date, format = "%Y-%m-%d"))
    df = df[df.iso_code == country]
    x = df.groupby([df.realDate.dt.year, df.realDate.dt.month])
    for i, (k, g) in enumerate(x):
        plt.plot_date(g.realDate, g.total_cases)

    plt.title("Evolution of total cases over the time in " + country)
    plt.ylabel("Total number of cases in france")
    plt.xlabel("Time")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.show()
    plt.savefig("figures/curvOfCovidTotalCasesOvertime.png")
    plt.close()


def plotCoolMap(df, geoJson):
    jsonURL= 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{jsonURL}/world-countries.json'
    json =requests.get(country_shapes).json()
    jsonDf = pd.json_normalize(json["features"])

    # replaceing miss match in the countries
    df = df.replace("Tanzania", "United Republic of Tanzania")
    df = df.replace("United States", "United States of America")
    df = df.replace("Congo", "Democratic Republic of the Congo")
    df = df.replace("Bahamas", "The Bahamas")
    df = df.replace("Cote d'Ivoire", "Ivory Coast")
    df = df.replace("Serbia", "Republic of Serbia")

    dfName = df.location.unique().tolist()
    jsonName = jsonDf["properties.name"].unique().tolist()
    missMatch = []
    for c in dfName:
        if not c in jsonName: missMatch.append(c)

    df = df[~(df.location.isin(missMatch))]
# building the map
    m = folium.Map(location=[40, 0], zoom_start=3.0)
    folium.Choropleth(
    geo_data=country_shapes,
    name='choropleth',
    data=df,
    columns=['location', 'total_cases'],
    key_on='feature.properties.name',
    fill_color='YlOrRd',
    nan_fill_color='white',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='total cases'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save("figures/coolMap.html")


def main():
    if not os.path.isdir("figures/"): os.mkdir("figures/")
    if not os.path.isdir("data/"): os.mkdir("data/")
    if not os.path.isfile("data/covidData.csv"):
        print("getting data from the web")
        df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
        df.to_csv("data/covidData.csv", sep=",", index=False)
    else:
        df = pd.read_csv("covidData.csv")


    # 
    #  first ploting a bar plot to visualise the continental distribution of the total cases 
    plotCaseRepartitionByContinent(df)

    # plot the same data as a pie chart to see whitch continent  has been hiten the most
    plotPieCaseRepartitionByContinent(df)

    #  plot the evolution of cases over time for several country,
    # it help to  see how the countries treated the pendemic
    plotTotalCasesOverTimeForCountry(df, "FRA")
    plotTotalCasesOverTimeForCountry(df, "USA")
    # plot a map to see whitch country has the most  cases
    plotCoolMap(df, "custom.geo.json")



if __name__ == '__main__':
    main()