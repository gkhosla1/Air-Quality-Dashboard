# This file will create a streamlit dashboard to explore the data that was prepared in the other notebooks

#import packages
import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
import datetime as dt
pd.options.mode.chained_assignment = None

# set page layout to wide, so multiple columns can be used
st.set_page_config(layout='wide')

# add title and subtitles (almost all text will be created using markdown since it has much 
#   better formatting options than streamlit's default text functions)
st.markdown('<h1 style="text-align:center">Air Quality Data for World Cities</h1>',
           unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center">Created By Griffin Khosla</h2>',
           unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center">MA346-SN2</h2>',
           unsafe_allow_html=True)

######
# INTRO SECTION
######
# create columns for first section (intro stuff)
info_spc1, info1, info_spc2, info2, info_spc3 = st.columns([1, 5, 1, 5, 1])

info1.markdown("<h2 style='text-align:center'>General Info</h2><p style='text-align:center'>This dashboard explores 2019 air quality data for world cities. It is built from a dataset compiled by me as part of the final project. The air quality data was scraped from IQ Air's website, since is was not downloadable. Population data was downloaded from the UN website. These data sources returned 4,680 cities and 1,860 cities, respectively, but this dashboard only displays data for the 710 cities that were in both datasets.</p>", unsafe_allow_html=True)

info2.markdown("<h2 style='text-align:center'>Data Description</h2><p style='text-align:center'>The air quality measure used in this dashboard is PM2.5 concentration (measured in micrograms per cubic meter). There are two kinds of inhalable particulate matter: PM2.5 and PM10. PM10 particulates have a diameter of 10 microns or less, and PM2.5 particulates have diameters of 2.5 microns or less. Both are mostly produced by emissions from fuel and wood combustion, but PM10 particulates are also made up of dust from contruction sites and landfills, wildfires, pollen, and more. Even though PM10 particulates are larger, health professionals consider PM2.5 particulates to be more hazardous to human health.</p>", unsafe_allow_html=True)

# Read in dataset
df = pd.read_csv('final_data.csv')

#####
# MAP SECTION
#####
# create columns on page, map in center column
map_spc1, map1, map_spc2 = st.columns([1, 2, 1])

# title text
map1.markdown("<h2 style='text-align:center'>Map of Air Quality and Population for World Cities</h2><p style='text-align:center'>The height of a cylinder corresponds to the population of the city, and the color corresponds to air quality (bins based on IQ Air's classifications). The map can become slow/unresponsive, so refresh the page if it is not working. Click + Drag to move around the map, Ctrl + Click + Drag to rotate view, Scroll to zoom. Hover over a cylinder to see details on the city.</p>",
              unsafe_allow_html=True)

# add color legend image below map
map1.image("aq_legend.JPG",
          width=900)

# data manipulation for mapping
# create dataframe with only necessary columns for mapping
df_map = df[['city',
             'country',
             'avg_2019',
             'lat',
             'lon',
             'pop_2020']]

# create color bins (returns RGB values to be used later)
def colors(pm_level):
    if pm_level < 10: # WHO target, blue
        return 50, 125, 255
    elif pm_level < 12: # Good, green
        return 150, 255, 150
    elif pm_level < 35.4: # Moderate, yellow
        return 255, 230, 125
    elif pm_level < 55.4: # Unhealthy for sensitive groups, orange
        return 255, 190, 90
    elif pm_level < 150.4: # Unhealthy, red
        return 255, 130, 120
    elif pm_level < 250.4: # Very unhealthy, purple
        return 160, 100, 255
    else: # Hazardous, brown
        return 120, 80, 50

df_map['r'], df_map['g'], df_map['b'] = zip(*df_map['avg_2019'].map(colors))

# convert population number to string with thousands separator
def pop_conv(pop):
    pop_str = f'{pop:,}'
    return pop_str

df_map['pop_str'] = df_map.pop_2020.apply(pop_conv)

# Create map
map1.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude=23.6388434607044,
         longitude=92.1323951592008,
         zoom=2,
         pitch=60,
     ),
     layers=[
         pdk.Layer(
            'ColumnLayer',
            data=df_map,
            auto_highlight=True,
            get_position=['lon', 'lat'],
            radius=20000,
            get_elevation='pop_2020',
            elevation_scale=0.05,
            get_fill_color=['r', 'g', 'b', 150],
            pickable=True,
            extruded=True,
         )
     ],
    tooltip={
        'html':'<b>City</b>: {city}<br><b>Country</b>: {country}<br><b>PM2.5 Concentration</b>: {avg_2019}<br><b>2020 Population</b>: {pop_str}'
    }
))

#####
# CHARTING SECTION
#####
# set up columns
brk1, brk_empty, brk2, brk3 = st.columns([8, 1, 7, 2])

# title text for continent chart
brk1.markdown("<h2 style='text-align:center'>Breakdown by Continent</h2>", unsafe_allow_html=True)

# data manipulation for conitinent chart
# new dataframe, create population string column for tooltips
df_plots = df[['city',
                'country',
                'continent',
                'jan',
                'feb',
                'mar',
                'apr',
                'may',
                'jun',
                'jul',
                'aug',
                'sep',
                'oct',
                'nov',
                'dec',
                'avg_2017',
                'avg_2018',
                'avg_2019',
                'pop_2020']]
df_plots['pop_str'] = df_plots.pop_2020.apply(pop_conv)

# dropdown for user selection of continent
cont_options = list(df_plots.continent.unique())
cont_options.insert(0, 'All')
cont = brk1.selectbox('Choose a Continent',
                   cont_options)

# filter df for selected continent
if cont=='All':
    df_plots_cont = df_plots
else:
    df_plots_cont = df_plots[df_plots['continent']==cont]

# interactive scatterplot
selection = alt.selection_point(fields=['continent'], bind='legend')
brk1.altair_chart(
    alt.Chart(df_plots_cont).mark_circle(size=60).encode(
            x=alt.X('pop_2020', axis=alt.Axis(title='2020 Population')),
            y=alt.Y('avg_2019', axis=alt.Axis(title='PM2.5 Concentration')),
            tooltip=['city', 'country', 'avg_2019', 'pop_str'],
            color=alt.Color('continent', scale=alt.Scale(scheme='category10')),
            opacity=alt.condition(selection, alt.value(0.6), alt.value(0.08)))
        .add_params(selection)
        .interactive(),
    use_container_width = True
)

# chart use instructions
brk1.markdown("<p style='text-align:center'>Each point on the scatterplot represents a city. Hover over a point to see details about the city. Select a continent in the legend to highlight its cities. Use the dropdown menu to focus on data for a specific continent.</p>",
             unsafe_allow_html=True)

# coutnry breakdown title
brk2.markdown("<h2 style='text-align:center'>Breakdown by Country</h2>", unsafe_allow_html=True)

# dataframe for country plotting (only countries from selected continent included)
df_plots_country = df_plots_cont.sort_values(by=['country'])

# possible country selections
country_opts = list(df_plots_country.country.unique())

# if all continents selected, set default country shown to australia (because it looks cooler than Afghanistan's plot)
if cont=="All":
    def_index = 5
else:
    def_index = 0

# dropdown selector    
country = brk2.selectbox('Choose a Country',
                      country_opts,
                      def_index)

# filter df for that country's data
df_plots_country = df_plots_country[df_plots_country['country']==country]

# spacing
brk3.header(' ')
brk3.header(' ')
brk3.text(' ')

# user selection for aggregation and chart type
agg = brk3.checkbox('Aggregate', value=False)
ann = brk3.checkbox('Annual', value=False)

# show plot based on checkbox selections
if (agg==False and ann==False): # all cities, monthly
    # keep only necessary columns, clean and manipulate data for charting
    keep_cols = list(df_plots_country.columns[0:15]) + ['pop_2020', 'pop_str']
    df_plot1 = df_plots_country[keep_cols].sort_values(by=['pop_2020'], ascending=False)
    leg_cities = list(df_plot1['city'][:5])
    df_plot1 = df_plot1.melt(id_vars=['city', 'country', 'continent', 'pop_str'],
                   var_name='month',
                   value_name='pm25')
    df_plot1['month'] = df_plot1['month'].map({'jan':dt.datetime(2019, 1, 1),
                                                 'feb':dt.datetime(2019, 2, 1),
                                                 'mar':dt.datetime(2019, 3, 1),
                                                 'apr':dt.datetime(2019, 4, 1),
                                                 'may':dt.datetime(2019, 5, 1),
                                                 'jun':dt.datetime(2019, 6, 1),
                                                 'jul':dt.datetime(2019, 7, 1),
                                                 'aug':dt.datetime(2019, 8, 1),
                                                 'sep':dt.datetime(2019, 9, 1),
                                                 'oct':dt.datetime(2019, 10, 1),
                                                 'nov':dt.datetime(2019, 11, 1),
                                                 'dec':dt.datetime(2019, 12, 1)})
    df_plot1 = df_plot1.dropna()
    sel_plot1 = alt.selection_point(fields=['city'], bind='legend')
    # draw chart
    brk2.altair_chart(
        alt.Chart(df_plot1).mark_line(point=True).encode(
                x = alt.X('month(month)', axis=alt.Axis(title='Month (2019)')),
                y = alt.Y('pm25', axis=alt.Axis(title='PM2.5 Concentration')),
                color = alt.Color('city', 
                                  scale=alt.Scale(scheme='category10'),
                                  legend=alt.Legend(title='Cities (Up to 5 Most Populous)', values=leg_cities)),
                opacity=alt.condition(sel_plot1, alt.value(0.6), alt.value(0.08)),
                tooltip=[alt.Tooltip('city', title='City'),
                         alt.Tooltip('pop_str', title='Population'),
                         alt.Tooltip('pm25', title='PM2.5 Concentration')])
            .add_params(sel_plot1)
            .interactive(),
        use_container_width=True
    )
elif (agg==True and ann==False): # country mean, monthly
    # keep only necessary columns, clean and manipulate data for charting
    keep_cols = list(df_plots_country.columns[0:15])
    df_plot2 = df_plots_country[keep_cols]
    df_plot2 = df_plot2.groupby('country')[['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']].agg('mean').reset_index()
    df_plot2 = df_plot2.melt(id_vars=['country'],
                   var_name='month',
                   value_name='pm25')
    df_plot2['month'] = df_plot2['month'].map({'jan':dt.datetime(2019, 1, 1),
                                     'feb':dt.datetime(2019, 2, 1),
                                     'mar':dt.datetime(2019, 3, 1),
                                     'apr':dt.datetime(2019, 4, 1),
                                     'may':dt.datetime(2019, 5, 1),
                                     'jun':dt.datetime(2019, 6, 1),
                                     'jul':dt.datetime(2019, 7, 1),
                                     'aug':dt.datetime(2019, 8, 1),
                                     'sep':dt.datetime(2019, 9, 1),
                                     'oct':dt.datetime(2019, 10, 1),
                                     'nov':dt.datetime(2019, 11, 1),
                                     'dec':dt.datetime(2019, 12, 1)})
    # draw chart
    brk2.altair_chart(
        alt.Chart(df_plot2).mark_line(point=True).encode(
                x = alt.X('month(month)', axis=alt.Axis(title='Month (2019)')),
                y = alt.Y('pm25', axis=alt.Axis(title='Mean PM2.5 Concentration')),
                tooltip=[alt.Tooltip('pm25', title='Mean PM2.5 Concentration')])
            .interactive(),
        use_container_width=True
    )
elif(agg==False and ann==True): # all cities, 2017-2019
    # keep only necessary columns, clean and manipulate data for charting
    keep_cols = list(df_plots_country.columns[0:3]) + list(df_plots_country.columns[15:19])
    df_plot3 = df_plots_country[keep_cols].sort_values(by=['pop_2020'], ascending=False)
    leg_cities = list(df_plot3['city'][:5])
    df_plot3 = df_plot3.melt(id_vars=['city', 'country', 'continent'],
                   var_name='year',
                   value_name='pm25')
    df_plot3['year'] = df_plot3['year'].map({'avg_2017':dt.datetime(2017, 1, 1),
                                            'avg_2018':dt.datetime(2018, 1, 1),
                                            'avg_2019':dt.datetime(2019, 1, 1)})
    df_plot3 = df_plot3.dropna()
    sel_plot3 = alt.selection_point(fields=['city'], bind='legend')
    # draw chart
    brk2.altair_chart(
        alt.Chart(df_plot3).mark_line(point=True).encode(
                    x = alt.X('year(year)', axis=alt.Axis(title='Year', tickCount=3)),
                    y = alt.Y('pm25', axis=alt.Axis(title='PM2.5 Concentration')),
                    color = alt.Color('city',
                                      scale=alt.Scale(scheme='category10'),
                                      legend=alt.Legend(title='Cities (Up to 5 Most Populous)', values=leg_cities)),
                    opacity=alt.condition(sel_plot3, alt.value(0.6), alt.value(0.08)),
                    tooltip=[alt.Tooltip('city', title='City'),
                             alt.Tooltip('pm25', title='PM2.5 Concentration')])
            .add_params(sel_plot3)
            .interactive(),
        use_container_width=True
    )
else: # country mean, 2017-2019
    # keep only necessary columns, clean and manipulate data for charting
    keep_cols = list(df_plots_country.columns[0:3]) + list(df_plots_country.columns[15:18])
    df_plot4 = df_plots_country[keep_cols]
    df_plot4 = df_plot4.groupby('country')[['avg_2017', 'avg_2018', 'avg_2019']].agg('mean').reset_index()
    df_plot4 = df_plot4.melt(id_vars=['country'],
                             var_name='year',
                             value_name='pm25')
    df_plot4['year'] = df_plot4['year'].map({'avg_2017':dt.datetime(2017, 1, 1),
                                            'avg_2018':dt.datetime(2018, 1, 1),
                                            'avg_2019':dt.datetime(2019, 1, 1)})
    df_plot4 = df_plot4.dropna()
    # draw chart
    brk2.altair_chart(
        alt.Chart(df_plot4).mark_line(point=True).encode(
                x = alt.X('year(year)', axis=alt.Axis(title='Year', tickCount=3)),
                y = alt.Y('pm25', axis=alt.Axis(title='Mean PM2.5 Concentration')),
                tooltip=[alt.Tooltip('pm25', title='Mean PM2.5 Concentration')])
            .interactive(),
        use_container_width=True
    )

# Chart use instructions
brk2.markdown("<p style='text-align:center'>Select a country using the dropdown filter (the countries listed in this filter depend on the continent selected in the previous section). Use the check boxes to change how the data is organized: checking the \"Aggregate\" box will show the average PM2.5 concentration for all cities in that country; checking the \"Annual\" box will switch from 2019 monthly values to 2017-2019 average values on the x axis. When the data is not aggregated, only the top 5 most populous cities in that country are shown in the legend. Select a city in the legend to highlight its line. Hover over points on the chart for more informaion.</p>",
             unsafe_allow_html=True)

#####
# RAW DATA SECTION
###

# title text
st.markdown('<h2 style="text-align:center">Data Tables</h2>', unsafe_allow_html=True)

# create columns
tbl1, tbl_spc1, tbl2, tbl_spc2, tbl3 = st.columns([7, 1, 7, 1, 7])

# create dataframe to use for these tables (more presentable column names and order)
df_tbl = pd.DataFrame({'City':df['city'],
                       'Country':df['country'],
                       'iso3':df['iso3'],
                       'Continent':df['continent'],
                       '2020 Population':df['pop_2020'],
                       'Avg PM2.5 2019':df['avg_2019'],
                       'PM2.5 Jan19':df['jan'],
                       'PM2.5 Feb19':df['feb'],
                       'PM2.5 Mar19':df['mar'],
                       'PM2.5 Apr19':df['apr'],
                       'PM2.5 May19':df['may'],
                       'PM2.5 Jun19':df['jun'],
                       'PM2.5 Jul19':df['jul'],
                       'PM2.5 Aug19':df['aug'],
                       'PM2.5 Sep19':df['sep'],
                       'PM2.5 Oct19':df['oct'],
                       'PM2.5 Nov19':df['nov'],
                       'PM2.5 Dec19':df['dec'],
                       'Avg PM2.5 2018':df['avg_2018'],
                       'Avg PM2.5 2017':df['avg_2017'],
                       'City Alt Name':df['city_alt'],
                       'Latitude':df['lat'],
                       'Longitude':df['lon']})

# first table: top 15 cities for pm2.5 concentration (most polluted)
tbl1.markdown('<h3 style="text-align:center">Highest PM2.5 Concentration</h3>', unsafe_allow_html=True)
df_tbl1 = df_tbl[['City',
                   'Country',
                   'Avg PM2.5 2019']].sort_values(by=['Avg PM2.5 2019'], ascending=False).reset_index(drop=True)
# restructure data for visual appeal
df_tbl1.index = [i + 1 for i in df_tbl1.index]
df_tbl1 = df_tbl1.astype({'Avg PM2.5 2019':'str'})
tbl1.table(df_tbl1[:15])

# second table: bottom 15 cities for pm2.5 concentration (cleanest air)
tbl2.markdown('<h3 style="text-align:center">Lowest PM2.5 Concentration</h3>', unsafe_allow_html=True)
df_tbl2 = df_tbl[['City',
                   'Country',
                   'Avg PM2.5 2019']].sort_values(by=['Avg PM2.5 2019']).reset_index(drop=True)
# restructure data for visual appeal
df_tbl2.index = [i + 1 for i in df_tbl2.index]
df_tbl2 = df_tbl2.astype({'Avg PM2.5 2019':'str'})
tbl2.table(df_tbl2[:15])

# third table: top 15 most populous cities
tbl3.markdown('<h3 style="text-align:center">Most Populous</h3>', unsafe_allow_html=True)
df_tbl3 = df_tbl[['City',
                 'Country',
                 '2020 Population',
                 'Avg PM2.5 2019']].sort_values(by=['2020 Population'], ascending=False).reset_index(drop=True)
# restructure data for visual appeal
df_tbl3['2020 Population'] = df_tbl3['2020 Population'].apply(pop_conv)
df_tbl3.index = [i + 1 for i in df_tbl3.index]
df_tbl3 = df_tbl3.astype({'Avg PM2.5 2019':'str'})
tbl3.table(df_tbl3[:15])

# full data table
# title
st.markdown('<h3 style="text-align:center">Full Data</h3>', unsafe_allow_html=True)

# data table
st.dataframe(df_tbl.sort_values(by=['City']).reset_index(drop=True))

#####
# FOOTNOTES
#####
st.markdown(
    'Air Quality data from <a href="https://www.iqair.com/world-most-polluted-cities?continent=&country=&state=&page=1&perPage=50&cities=" target="_blank">IQ Air</a>',
    unsafe_allow_html=True)
st.markdown(
    'Population data from <a href="https://population.un.org/wup/Download/" target="_blank">UN</a> (file named WUP2018-F12-Cities_Over_300K.xls)',
    unsafe_allow_html=True)
