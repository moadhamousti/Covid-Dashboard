# sreamlit
import streamlit as st
# pandas
import pandas as pd
# config.toml
import toml
# altair
import altair as alt
# datetime 
from datetime import date,datetime
# pydeck
import pydeck as pdk
import requests
from requests.exceptions import ConnectionError


# Page icon and Title 

st.set_page_config(page_title="Covid-19 Data Dashboard", page_icon="🦠" , layout="wide", initial_sidebar_state="expanded")

# Linked CSS File 

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Logo Of the Web App 

st.sidebar.image("./components/img/logo.png", width=280)

# Config.toml For Styling 

@st.cache_data
def load_config():
    with open(".streamlit/config.toml") as f:
        config = toml.loads(f.read())
    return config

config = load_config()

# Sections in My Web Application 

header = st.container()
dataset = st.container()
placeholder = st.container()
chart = st.container()


# Loading the CSV DataFrames 

# ====== 1 - General Covid Data ======== #

@st.cache_data
def load_data():
    covid = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')

    # Fill NANs with 0s :
    covid = covid.fillna(0)
    return covid

# ====== 2 - Countries Names And ISO Code ======== #

def list_of_countries():
        df = pd.read_csv("./components/csv/countries.csv")
        return df["Name"].tolist()

df = load_data()

# st.sidebar.header('Dashboard `COVID-19`')

# Set default countries for dropdown menu
default_countries = ['United States', 'China', 'United Kingdom', 'Morocco']

# Header Section 

with header:
    st.title('`COVID-19` Data Worldwide :')
    st.info('In this project i look into Providing the data of each country and for each Continent about `COVID-19` disease Since the start in the year 2020 , Starting With an OverView of this Phenomenon ,You can se all the data of any country Updated Constantely. Then being Specific Like talking about Deaths caused by `Covid-19` And a Specific Country (MOROCCO).' )
    st.text('COVID-19 Data for each Country With the Population and Total Cases and Deaths... Also Recovered Cases and Active Cases and finally Total Tests.And You can select the Country from the Selectbox in the Sidebar:')
    with st.sidebar:
        st.subheader('`COVID-19` Data Worldwide :')
        selected_country = st.sidebar.selectbox('Select Country or Continant :', load_data()['location'].unique() ,key='country_selectbox-1')

        columns = ['iso_code','location','continent','date','total_cases','new_cases','total_deaths','new_deaths','total_cases_per_million','new_cases_per_million']

        filtered_data = load_data()[load_data()['location'] == selected_country]

    st.write('## `COVID-19` Data for : ', '<span style="color:#e64c2c">'+ selected_country + '</span>', unsafe_allow_html=True)
    st.write(filtered_data[columns])
    

    # Adding external URL JSONs :

    def remote_css(url):
        st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)


    def covid_data_menu():
        col1, col2 = st.columns([6, 6])
        # Time Update Disabled Menu
        with col1:
            st.text_input(label="Last Updated", value=str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")), disabled=True)
        # Countries JSON File 
        with col2:
            try:
                url = "https://disease.sh/v3/covid-19/countries"
                response = requests.get(url)
                countries = [i.get("country") for i in response.json()]
                option = st.selectbox('Please select country?', (countries), help="Please select country")


            except ConnectionError:
                st.error("There is a connection error we failed to fetch all the countries 😥")
        try:
            response = requests.get("https://disease.sh/v3/covid-19/countries/" + option)
            data = response.json()

            # Columns 

            col1, col2 = st.columns([6, 6])
            # column 1 Contains Country (Flag, ISO code) & JSON Data on another TABLE :
            with col1:
                st.subheader("Country Info :")
                country_data = data.pop("countryInfo")
                longitude, latitude = country_data["long"], country_data["lat"]
                country_data.update({"country": data["country"]})
                country_data.pop("lat")
                country_data.pop("long")
                remote_css("")
                st.markdown(f"""
                <table class="table table-borderless">
                        <tr>
                        <td>Country</td>
                        <td>{country_data["country"]}</td>
                        </tr>
                        <tr>
                        <td>Flag</td>
                        <td><img src="{country_data["flag"]}" style="width:20%;height:40%"></td>
                        </tr>
                        <tr>
                        <td>ISO Code</td>
                        <td>{country_data["iso3"]}</td>
                        </tr>
                </table></br>
                """, unsafe_allow_html=True)

                st.subheader("`Covid-19` Statistics :")
                data.pop("country")
                data['updated'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                df = pd.DataFrame.from_dict(data, orient="index", dtype=str, columns=['Value'])
                st.table(df)

            # Column 2 Contains Country Map And Vaccination Data 

            # ======== 2 - Country Map =========

            with col2:
                st.subheader("Selected Country Map :")
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=pdk.ViewState(
                        latitude=latitude,
                        longitude=longitude,
                        zoom=4.7,
                        pitch=50,
                    )
                ))

                # ======== 2 - Vaccination Data JSON =========

                st.subheader("`Covid-19`  Vaccination Data :")
                current_date = datetime.today().date()
                first_day_of_month = current_date.replace(day=1)
                number_of_days = (date.today() - first_day_of_month).days

                url = "https://disease.sh/v3/covid-19/vaccine/coverage/countries?lastdays=" + str(number_of_days)
                response = requests.get(url)
                vaccination_data = {}
                for i in response.json():
                    if i.get("country") == option:
                        vaccination_data = i.get("timeline")

                if len(vaccination_data) != 0:
                    vaccination_data = {str(key): str(value) for key, value in vaccination_data.items()}
                    st.write(vaccination_data)
                else:
                    st.write("Vaccination data for %s no available" % option)


            
        except ConnectionError as e:
            st.error("There is a connection error please retry later 😥")



    def main():
        st.title("`COVID-19` Live Update Data Worldwide :")
        st.info('In this Section You can Follow Any Update on `COVID-19` For any Country , All the details From , `General Informations` : like The flag and the ISO code to `Statistics`: like Cases , Deaths, And Tests , and finally `Vaccination` : of Total Vaccinated People Worldwide by date.')
        covid_data_menu()


    if __name__ == '__main__':
        main()



# Filter the data based on selected country
def filter_data(country):
    return df[(df['location'] == country) & (df['date'] >= '2020-01-03')].set_index('date')

# Sidebar for selecting a country
with st.sidebar:
        st.subheader('`COVID-19` Total Deaths Worldwide :')
        selected_countries = st.multiselect(
            'Select Countries or Continants :',
            df.groupby('location').count().reset_index()['location'].tolist(),
            default=default_countries
        )


with dataset:
    # Main app
    st.title('`COVID-19` line chart Graph of **Total Deaths** for All Countries & Continants :')
    st.info('`COVID-19` Data Of Total Cases for each Country and Continants ,To compare between Countries Or Continants :')
    st.text('You Can Select Countries Or Continants in the SideBar :')

    # Display a comparative graph for multiple countries
    st.subheader('`COVID-19` Total Cases Worldwide **(Compare Graph)**:')

    if selected_countries:
        chart_data = pd.DataFrame()
        for country in selected_countries:
            chart_data[country] = filter_data(country)['total_cases']
        st.line_chart(chart_data)

    # Function to create the chart based on user selection
    def create_chart(df, selection):
        if selection == "total_cases":
            chart_title ='COVID-19 Total Cases In Morocco'
            y_axis_title = "Total Cases"
            y_field = "total_cases:Q"
        elif selection == "new_cases":
            chart_title = 'COVID-19 New Cases In Morocco'
            y_axis_title = "New Cases"
            y_field = "new_cases:Q"
        else:
            chart_title ='COVID-19 Total Deaths In Morocco'
            y_axis_title = "Total Deaths"
            y_field = "total_deaths:Q"
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y(y_field, title=y_axis_title)
        ).properties(
            width=700,
            height=400,
            title=chart_title
        )
        return chart

    # Streamlit app
    with st.sidebar:
        # Sidebar for user selection
        st.subheader('`COVID-19` Morocco Data :')
        options = ["total_cases", "new_cases", "total_deaths"]
        options = [option.replace('_', ' ').capitalize() for option in options]
        selection = st.selectbox('Select an Option :', options)

    my_country = 'MOROCCO'

    st.write('## `COVID-19` Data for : ', '<span style="color:#e64c2c">'+ my_country + '</span>', unsafe_allow_html=True)
    st.info('The `COVID-19` Of (MOROCCO) Contains Total Cases , Total Deaths and finally New Cases:')
    st.text('You Can Choose Any Option From The Menu in the Sidebar To be Displayed.')
with st.container():
    # Filter data for Morocco
    df = df[df['location'] == 'Morocco']

    # Create the chart based on user selection
    chart = create_chart(df, selection)

    # Display the chart
    st.altair_chart(chart)


st.title('General Tips To Protect Yourself From `Covid-19` :')
with st.expander('Covid 19 Prevention Tips'):
                    st.subheader("Here’s what you can do to protect yourself:")
                    st.markdown(f"""<p>At International Medical Corps, we’re always preparing for the unexpected—whether it’s
                    an earthquake, a hurricane or an outbreak of infectious disease. As the COVID-19 outbreak grows,
                    it’s important to know that there are many actions we can take to protect ourselves, our loved ones and
                    our communities.</p>""", unsafe_allow_html=True)

                    st.subheader("Here’s some tips you can apply:")
                    st.markdown(f""" <ul> <li>Wash your hands frequently with soap and water for at least 20 seconds.</li>
                    <li>If soap and water are not available, use an alcohol-based hand sanitizer with at least 60%
                    alcohol.</li> <li>Avoid close contact with people who are sick.</li> <li>Especially if you’re in a
                    high-risk group, consider limiting your exposure to others, using social distancing—for example,
                    avoid large gatherings, crowds of people and frequent trips to the store.</li>
                    </li>Visit your state and local public-health websites for additional guidance specific to your area.</li>
                    <li>Those at higher risk for serious illness should take additional precautions.</li>
                    </ul> """, unsafe_allow_html=True)

                    st.markdown(
                        f"""</br> Reference for Tips : <a href="https://internationalmedicalcorps.org/emergency-response/covid-19/coronavirus-prevention-tips/">IMC</a>""",
                        unsafe_allow_html=True)


st.markdown(
    """
    <link href='style.css' rel='stylesheet'>
    """,
    unsafe_allow_html=True
)




    
with st.sidebar:
    st.markdown('**Made By Moad Hamousti** 👋')







