# Streamlit library
import streamlit as st

# Data libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import dates
import numpy as np
import array
import altair as alt

st.set_page_config(
    page_title="Arima Yuuto UK Box Office", 
    layout="wide"
)

# Styling the page
st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        margin-top: 0;
        margin-bottom: 0;
    }
    .sidebar .sidebar-content {
        width: 100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Tables

## 1. Market Share Table (market_shares)
market_shares = pd.read_csv("datasets/market_shares.csv")
market_shares = market_shares.drop(columns=['index'])
market_shares["year"] = pd.to_datetime(market_shares["year"], format='%Y')
market_shares = market_shares.sort_values(by=['name', 'year']).reset_index()
market_shares = market_shares.drop(columns=['index'])
market_shares = market_shares.rename(columns={"name": "distributor"})
### Shares 2011-now (shares_2011_now)
shares_2011_now = market_shares.loc[market_shares['year'] > '2010-01-01']
### Total market shares 2011-now (market_shares_2011_now)
total_market_shares = market_shares.groupby([market_shares.year.dt.year]).agg({'marketShare': 'sum'}).reset_index()
market_shares_2011_now = total_market_shares.loc[total_market_shares['year'] > 2010]
### Five highest average shares of distributors (five_averages_shares)
five_averages_shares = shares_2011_now.groupby('distributor').mean('marketShare').sort_values('marketShare', ascending=False).reset_index().head(5)
five_averages_shares = five_averages_shares[['distributor','marketShare']]
### Name of five highest distributors (five_averages_distributors)
five_averages_distributors = five_averages_shares['distributor'].unique()
### Shares of five highest avg 2011-now (shares_of_five_biggest_avg)
shares_of_five_biggest_avg = shares_2011_now.loc[market_shares['distributor'].isin(five_averages_distributors)]
shares_of_five_biggest_avg = shares_of_five_biggest_avg[['year','distributor','marketShare']].reset_index()
shares_of_five_biggest_avg = shares_of_five_biggest_avg.drop(columns=['index'])
### Columns for distributor's pivot table (pivot_columns)
pivot_distributors_columns = np.array(five_averages_distributors)
pivot_columns = np.append (['year'], pivot_distributors_columns)
### Pivot table of five highest average (pivot_five_avg_biggest)
pivot_five_avg_biggest = shares_of_five_biggest_avg.pivot_table('marketShare', ['year'], 'distributor').reset_index()
pivot_five_avg_biggest = pivot_five_avg_biggest[pivot_columns]
pivot_five_avg_biggest = pivot_five_avg_biggest.fillna(0)

## 2. Films Table (films)
films = pd.read_csv("datasets/archive_export.csv")
films["date"] = pd.to_datetime(films["date"], format='%Y%m%d')
### Films of five distributors with highest average shares (films_five_highest_share)
films_five_highest_share = films.loc[films['distributor'].isin(five_averages_distributors)]
films_five_highest_share = films_five_highest_share.groupby([films_five_highest_share.date.dt.year, films_five_highest_share.distributor, films_five_highest_share.film]).agg(total_gross= ('total_gross' , 'sum')).reset_index()
films_five_highest_share = films_five_highest_share.rename(columns={"date": "year"})
films_five_highest_share = films_five_highest_share.loc[films_five_highest_share['year'] > 2010].reset_index().drop(columns=['index'])

film_first_year_launch = films.loc[films['distributor'].isin(five_averages_distributors)]
film_first_year_launch = film_first_year_launch.groupby([film_first_year_launch.date.dt.year, film_first_year_launch.distributor, film_first_year_launch.film]).agg(total_gross= ('total_gross' , 'sum')).reset_index()
film_first_year_launch = film_first_year_launch.rename(columns={"date": "year"})
film_first_year_launch = film_first_year_launch.groupby([film_first_year_launch.film, film_first_year_launch.distributor]).agg(first_launch_year= ('year' , 'min'))
film_first_year_launch = film_first_year_launch.sort_values(['first_launch_year','distributor','film'], ascending=True).reset_index()

film_showing_status = pd.merge(films_five_highest_share, film_first_year_launch, on='film', how='left').reset_index().drop(columns=['index'])
def add_column(row):
    if row['year'] ==  row['first_launch_year'] or (row['year'] - row['first_launch_year']) == 1:
        return 'First Showing'
    else:
        return 'Re-Showing'
film_showing_status['status'] = film_showing_status.apply(add_column, axis=1)

first_showing_film = film_showing_status.loc[(film_showing_status['year'] - film_showing_status['first_launch_year']) == 0].reset_index().drop(columns=['index'])
first_showing_film = first_showing_film[['year','film','distributor_x']]

count_first_showing_film = first_showing_film.groupby([first_showing_film.distributor_x, first_showing_film.year]).agg(first_showing_count = ('film' , 'count')).reset_index()

total_new_title = count_first_showing_film.groupby(count_first_showing_film.year).agg(total_new_title = ('first_showing_count' , 'sum')).reset_index()

pivot_count_first_showing_film = count_first_showing_film.pivot_table('first_showing_count', ['year'], 'distributor_x').reset_index()
pivot_count_first_showing_film = pivot_count_first_showing_film[pivot_columns]
pivot_count_first_showing_film = pivot_count_first_showing_film.fillna(0)

re_showing_film = film_showing_status.loc[film_showing_status['status'] == 'Re-Showing'].reset_index().drop(columns=['index'])
re_showing_film = re_showing_film[['year','film','distributor_x']]

count_films_of_five_2011_now = films_five_highest_share.groupby([films_five_highest_share.year, films_five_highest_share.distributor]).agg(film_count= ('film' , 'count')).reset_index()

pivot_count_films_of_five_2011_now = count_films_of_five_2011_now.pivot_table('film_count', ['year'], 'distributor').reset_index()
pivot_count_films_of_five_2011_now = pivot_count_films_of_five_2011_now[pivot_columns]

highest_gross_of_five_highest_share = films_five_highest_share.groupby([films_five_highest_share.year, films_five_highest_share.distributor]).agg(highest_gross= ('total_gross' , 'max')).reset_index()
highest_gross_2011_now = highest_gross_of_five_highest_share.loc[highest_gross_of_five_highest_share['year'] > 2010].reset_index()
highest_gross_2011_now = highest_gross_2011_now.drop(columns=['index'])
highest_gross_2011_now["year"] = pd.to_datetime(highest_gross_2011_now["year"], format='%Y')

pivot_highest_gross_2011_now = highest_gross_2011_now.pivot_table('highest_gross', ['year'], 'distributor').reset_index()
pivot_highest_gross_2011_now = pivot_highest_gross_2011_now[pivot_columns]

highest_distributor_gross = highest_gross_2011_now.groupby([highest_gross_2011_now.distributor]).agg(max_highest_gross= ('highest_gross' , 'max')).sort_values('max_highest_gross', ascending=False).reset_index()

five_highest_gross_distributors = highest_distributor_gross['distributor'].unique()

five_max_highest_gross = highest_distributor_gross['max_highest_gross'].unique()

highest_gross_film_title =  films_five_highest_share.loc[films_five_highest_share['total_gross'].isin(five_max_highest_gross)].reset_index().drop(columns=['index'])[['year','film','distributor','total_gross']]

highest_gross_value = highest_gross_2011_now['highest_gross'].unique()

films_list_2011_now = films_five_highest_share.loc[films_five_highest_share['total_gross'].isin(highest_gross_value)].reset_index().drop(columns=['index'])[['year','film','distributor','total_gross']]
films_list_2011_now["year"] = pd.to_datetime(films_list_2011_now["year"], format='%Y')

pivot_films_2011_now = films_list_2011_now.pivot_table('film', ['year'], 'distributor', aggfunc=lambda x: ' '.join(x)).reset_index()
pivot_films_2011_now = pivot_films_2011_now[pivot_columns]

accumulation_gross_of_five_highest_share = films_five_highest_share.groupby([films_five_highest_share.year, films_five_highest_share.distributor]).agg(accumulation_gross= ('total_gross' , 'sum')).reset_index()
accumulation_gross_2011_now = accumulation_gross_of_five_highest_share.loc[accumulation_gross_of_five_highest_share['year'] > 2010].reset_index()
accumulation_gross_2011_now = accumulation_gross_2011_now.drop(columns=['index'])
accumulation_gross_2011_now["year"] = pd.to_datetime(accumulation_gross_2011_now["year"], format='%Y')

pivot_accumulation_gross_2011_now = accumulation_gross_2011_now.pivot_table('accumulation_gross', ['year'], 'distributor').reset_index()
pivot_accumulation_gross_2011_now = pivot_accumulation_gross_2011_now[pivot_columns]

films_count_of_five_highest_share = films_five_highest_share.groupby([films_five_highest_share.year, films_five_highest_share.distributor]).agg(films_count= ('film' , 'count')).reset_index()
films_count_2011_now = films_count_of_five_highest_share.loc[films_count_of_five_highest_share['year'] > 2010].reset_index()
films_count_2011_now = films_count_2011_now.drop(columns=['index'])
films_count_2011_now["year"] = pd.to_datetime(films_count_2011_now["year"], format='%Y')

# Any Preparations
five_averages_distributors_modif = pivot_distributors_columns.astype(str)
def replace_space(x):
    return x.replace(' ', '_')
vreplace_comma = np.vectorize(replace_space)
five_averages_distributors_modif = vreplace_comma(five_averages_distributors_modif)

year_datever_shares = sorted(market_shares['year'].unique())
year_datever_shares = pd.to_datetime(year_datever_shares, format='%Y-%m-%d')

year_shares = sorted(market_shares.year.dt.year.unique())
year_shares = pd.to_datetime(year_shares, format='%Y')

# Sidebar Title
st.sidebar.title("Arima Yuuto - UK Box Office 2011-Now")

# Tampilkan tombol navigasi pada sidebar
nav_button_1 = st.sidebar.button("Overview")
nav_button_2 = st.sidebar.button("Tables")
nav_button_3 = st.sidebar.button("Distributors")
nav_button_4 = st.sidebar.button("Market Shares")
nav_button_5 = st.sidebar.button("Films")
nav_button_6 = st.sidebar.button("Gross Earns")
nav_button_7 = st.sidebar.button("Analysis Creation")
nav_button_8 = st.sidebar.button("Source")
nav_button_9 = st.sidebar.button("About")

# Set tombol navigasi pertama menjadi aktif pada awal dibuka
if not nav_button_1 and not nav_button_2 and not nav_button_3 and not nav_button_4 and not nav_button_5 and not nav_button_6 and not nav_button_7 and not nav_button_8 and not nav_button_9:
    nav_button_1 = True

# Tampilkan konten berdasarkan tombol navigasi yang aktif
if nav_button_1:

    st.title("Overview")
    st.markdown("<br>", unsafe_allow_html=True)

    import datetime
    today = datetime.date.today()
    formatted_date = today.strftime("%d %B %Y")
    st.write(formatted_date)

    st.markdown("<br>", unsafe_allow_html=True)

    mx_shares, mx_new_film_count = st.columns(2)

    with mx_shares:
        curr_shares = market_shares_2011_now['marketShare'].iloc[-1]
        prev_shares = market_shares_2011_now['marketShare'].iloc[-2]

        if curr_shares == 0 and prev_shares == 0:
            shares_diff_pct = 0
        else:
            shares_diff_pct = 100.0 * (curr_shares - prev_shares) / prev_shares

        st.metric(
            label = "Shares",
            value = f"{curr_shares:.0f}", 
            delta = f"{shares_diff_pct:.2f}%"
        )

    with mx_new_film_count:
        curr_new_film_count = total_new_title['total_new_title'].iloc[-1]
        prev_new_film_count = total_new_title['total_new_title'].iloc[-2]

        new_film_count_diff = curr_new_film_count - prev_new_film_count

        st.metric(
            label = "New Film Count",
            value = f"{curr_new_film_count:.0f}", 
            delta = f"{new_film_count_diff:.0f}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    # labels = [five_averages_distributors[0]+', ', five_averages_distributors[1]+', ', five_averages_distributors[2]+', ', five_averages_distributors[3]+', ', five_averages_distributors[4]]
    # color_labels = ' '.join([f'<span style="color: {color};">{label}</span>' for color, label in zip(colors, labels)])
    # st.markdown('Color Legend : ' + color_labels, unsafe_allow_html=True)
    # st.markdown("<br>", unsafe_allow_html=True)

    # Bagi layar menjadi 2 kolom
    col1, col2 = st.columns(2)

    # Tampilkan chart pada kolom pertama
    with col1:
        source = films_five_highest_share.groupby(films_five_highest_share.year).agg(total_gross=('total_gross', 'sum')).reset_index()

        chart = alt.Chart(source).mark_line().encode(
            alt.X('year', title='Year'),
            alt.Y('total_gross', title='Gross Earn')
        ).properties(
            title='Total Gross Earn',
            height=500
        ).configure_title(
            anchor='middle'
        )
        st.altair_chart(chart, use_container_width=True)

    with col2:
        overall_film_showing_status = film_showing_status.loc[(film_showing_status['year'] - film_showing_status['first_launch_year']) != 1].reset_index().drop(columns=['index'])
        # overall_film_showing_status

        chart = alt.Chart(overall_film_showing_status).mark_bar().encode(
            x=alt.X('count(status):Q', title='Count'),
            y=alt.Y('status:O', title=''),
            color=alt.Color('status:N', legend=None),
            row=alt.Row('distributor_x:N', title='', sort=five_averages_distributors)
        ).properties(
            title='Film Showing Status Counts',
            height=58
        ).configure_title(
            anchor='middle'
        ).configure_axis(
            labelColor='black',  # Warna tulisan pada sumbu x dan sumbu y
            titleColor='black'  # Warna judul sumbu x dan sumbu y
        )

        st.altair_chart(chart)
    

if nav_button_2:
    st.title("Tables")

    shares, tab2 = st.tabs(["Shares", "Movies"])

    with shares:

        list_tabs = (["t_1","t_2","t_3","t_4","t_5","t_6","t_7","t_8","t_9","t_10","t_11","t_12","t_13"])
        list_year = year_shares[-1:-14:-1]
        list_year_str = [str(year.year) for year in list_year]

        year_datever_shares_picked = year_datever_shares[-1:-14:-1]

        list_tabs = st.tabs([list_year_str[-13],list_year_str[-12],list_year_str[-11],list_year_str[-10],list_year_str[-9],list_year_str[-8],list_year_str[-7],list_year_str[-6],list_year_str[-5],list_year_str[-4],list_year_str[-3],list_year_str[-2],list_year_str[-1]])

        for i in range(len(list_tabs)):
            with list_tabs[i]:
                data = market_shares[['distributor', 'marketShare', 'marketPercentage']].loc[market_shares['year'] == year_datever_shares_picked[i]].reset_index().drop(columns=['index'])
                data = data.assign(percentage=data['marketShare']/total_market_shares['marketShare'].iloc[-1-i])
                data = data.rename(columns={'distributor': 'Distributor', 'marketShare': 'Market Share','percentage': 'Percentage'})
                def format_percentage(value):
                    return '{:.2%}'.format(value)
                data['Percentage'] = data['Percentage'].apply(format_percentage)
                data = data.sort_values(by='Market Share', ascending=False).reset_index().drop(columns=['index'])
                st.dataframe(data, use_container_width=True)

    with tab2:

        list_tabs = (["t_1","t_2","t_3","t_4","t_5","t_6","t_7","t_8","t_9","t_10","t_11","t_12","t_13"])
        list_year = year_shares[-1:-14:-1]
        list_year_str = [str(year.year) for year in list_year]

        year_datever_shares_picked = year_datever_shares[-1:-14:-1]

        list_tabs = st.tabs([list_year_str[-13],list_year_str[-12],list_year_str[-11],list_year_str[-10],list_year_str[-9],list_year_str[-8],list_year_str[-7],list_year_str[-6],list_year_str[-5],list_year_str[-4],list_year_str[-3],list_year_str[-2],list_year_str[-1]])

        for i in range(len(list_tabs)):
            with list_tabs[i]:
                data = film_showing_status[['film', 'distributor_x', 'status']].loc[film_showing_status['year'] == ((film_showing_status['year'].max())-i)].reset_index().drop(columns=['index'])
                data = data.rename(columns={'film': 'Title', 'distributor_x': 'Distributor','year': 'Year', 'status': 'Status'})
                data = data.sort_values(by='Title', ascending=True).reset_index().drop(columns=['index'])
                st.dataframe(data, use_container_width=True)


if nav_button_3:
    st.title("Distributors")
    
    five_averages_distributors_modif = st.tabs([five_averages_distributors[0], five_averages_distributors[1], five_averages_distributors[2], five_averages_distributors[3], five_averages_distributors[4]])

    for i in range(len(five_averages_distributors_modif)):
        with five_averages_distributors_modif[i]:

            mx_shares, mx_earns, mx_new_film_count = st.columns(3)

            with mx_shares:
                curr_shares = pivot_five_avg_biggest[five_averages_distributors[i]].iloc[-1]
                prev_shares = pivot_five_avg_biggest[five_averages_distributors[i]].iloc[-2]

                if curr_shares == 0 and prev_shares == 0:
                    shares_diff_pct = 0
                else:
                    shares_diff_pct = 100.0 * (curr_shares - prev_shares) / prev_shares

                st.metric(
                    label = "Shares",
                    value = f"{curr_shares:.0f}", 
                    delta = f"{shares_diff_pct:.2f}%"
                )

            with mx_earns:
                curr_earns = pivot_accumulation_gross_2011_now[five_averages_distributors[i]].iloc[-1]
                prev_earns = pivot_accumulation_gross_2011_now[five_averages_distributors[i]].iloc[-2]

                if curr_earns == 0 and prev_earns == 0:
                    earns_diff_pct = 0
                else:
                    earns_diff_pct = 100.0 * (curr_earns - prev_earns) / prev_earns

                st.metric(
                    label = "Earns",
                    value = f"{curr_earns:.0f}", 
                    delta = f"{earns_diff_pct:.2f}%"
                )

            with mx_new_film_count:
                curr_new_film_count = pivot_count_first_showing_film[five_averages_distributors[i]].iloc[-1]
                prev_new_film_count = pivot_count_first_showing_film[five_averages_distributors[i]].iloc[-2]

                new_film_count_diff = curr_new_film_count - prev_new_film_count

                st.metric(
                    label = "New Film Count",
                    value = f"{curr_new_film_count:.0f}", 
                    delta = f"{new_film_count_diff:.0f}"
                )

            st.markdown("<br>", unsafe_allow_html=True)

            film_titles = highest_gross_film_title['film'].loc[highest_gross_film_title['distributor'] == five_averages_distributors[i]].tolist()
            film_titles = [title.title() for title in film_titles]
            years = highest_gross_film_title['year'].loc[highest_gross_film_title['distributor'] == five_averages_distributors[i]].astype(str).tolist()
            film_year_pairs = zip(film_titles, years)
            formatted_pairs = [f"{title} ({year})" for title, year in film_year_pairs]
            st.write("Best earn film title : ", ", ".join(formatted_pairs))

            highest_earns = highest_gross_film_title['total_gross'].loc[highest_gross_film_title['distributor'] == five_averages_distributors[i]].astype(str).tolist()
            formatted_earns = [f'£{earn}' for earn in highest_earns]
            st.write("Earns : ", ", ".join(formatted_earns))



if nav_button_4:

    st.title("Market Shares")
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Total Shares Movements")
    total_shares = alt.Chart(market_shares_2011_now).mark_line().encode(
    alt.X('year', title='Year'),
    alt.Y('marketShare', title='Total Share')
    ).properties(
        # title='Total Shares Movements',
        height=500
    ).configure_title(
        anchor='middle'
    )
    st.altair_chart(total_shares,use_container_width=True)

    st.subheader("Shares Movement of Five Distributor")
    # Five distributors in a chart
    st.markdown("<br>", unsafe_allow_html=True)
    line_chart = alt.Chart(shares_of_five_biggest_avg).mark_line(point=True).encode(
        alt.X('year', title='Year'),
        alt.Y('marketShare', title='Market Shares'),
        alt.Color('distributor', title='Distributor', scale=alt.Scale(scheme='category10'), sort=five_averages_distributors)
    ).properties(
        # title='Distributor Average Shares Movements',
        height=500
    ).configure_title(
        anchor='middle'
    )
    st.altair_chart(line_chart,use_container_width=True)

    # Chart per distributor
    five_averages_distributors_modif = st.tabs([five_averages_distributors[0], five_averages_distributors[1], five_averages_distributors[2], five_averages_distributors[3], five_averages_distributors[4]])

    for i in range(len(five_averages_distributors_modif)):
        with five_averages_distributors_modif[i]:
            shares_line = alt.Chart(pivot_five_avg_biggest).mark_line().encode(
                alt.X('year', title='Year'),
                alt.Y(five_averages_distributors[i], title='Market Share')
            )
            st.altair_chart(shares_line,use_container_width=True)

if nav_button_5:

    st.title("Films")
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Films Count of Five Distributor")
    # Five distributors in a chart
    st.markdown("<br>", unsafe_allow_html=True)
    line_chart = alt.Chart(count_films_of_five_2011_now).mark_line(point=True).encode(
        alt.X('year', title='Year'),
        alt.Y('film_count', title='Film Count'),
        alt.Color('distributor', title='Distributor', scale=alt.Scale(scheme='category10'), sort=five_averages_distributors)
    ).properties(
        # title='Films Count Movements',
        height=500
    ).configure_title(
        anchor='middle'
    )
    st.altair_chart(line_chart,use_container_width=True)
    # Chart per distributor
    five_averages_distributors_modif = st.tabs([five_averages_distributors[0], five_averages_distributors[1], five_averages_distributors[2], five_averages_distributors[3], five_averages_distributors[4]])

    for i in range(len(five_averages_distributors_modif)):
        with five_averages_distributors_modif[i]:
            films_line = alt.Chart(pivot_count_films_of_five_2011_now).mark_line().encode(
                alt.X('year', title='Year'),
                alt.Y(five_averages_distributors[i], title='Films Count')
            )
            st.altair_chart(films_line,use_container_width=True)

            st.dataframe(films_five_highest_share[['year', 'film']].loc[films_five_highest_share['distributor'] == five_averages_distributors[i]].reset_index().drop(columns=['index']), use_container_width=True)

if nav_button_6:

    st.title("Gross Earns")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Highest Gross
    st.subheader("Highest Gross of Five Distributor")
    ## Five distributors in a chart
    st.markdown("<br>", unsafe_allow_html=True)
    line_chart = alt.Chart(highest_gross_2011_now).mark_line(point=True).encode(
        alt.X('year', title='Year'),
        alt.Y('highest_gross', title='Highest Gross'),
        alt.Color('distributor', title='Distributor', scale=alt.Scale(scheme='category10'), sort=five_averages_distributors)
    ).properties(
        # title='Distributor Average Shares Movements',
        height=500
    ).configure_title(
        anchor='middle'
    )
    st.altair_chart(line_chart,use_container_width=True)
    ## Chart per distributor
    five_averages_distributors_modif = st.tabs([five_averages_distributors[0], five_averages_distributors[1], five_averages_distributors[2], five_averages_distributors[3], five_averages_distributors[4]])

    for i in range(len(five_averages_distributors_modif)):
        with five_averages_distributors_modif[i]:
            highest_earns_line = alt.Chart(pivot_highest_gross_2011_now).mark_line().encode(
                alt.X('year', title='Year'),
                alt.Y(five_averages_distributors[i], title='Highest Gross')
            )
            st.altair_chart(highest_earns_line,use_container_width=True)

    # Accumulation Gross
    st.subheader("Accumulation Gross of Five Distributor")
    ## Five distributors in a chart
    st.markdown("<br>", unsafe_allow_html=True)
    line_chart = alt.Chart(accumulation_gross_2011_now).mark_line(point=True).encode(
        alt.X('year', title='Year'),
        alt.Y('accumulation_gross', title='Accumulation Gross'),
        alt.Color('distributor', title='Distributor', scale=alt.Scale(scheme='category10'), sort=five_averages_distributors)
    ).properties(
        # title='Accumulation Gross Movements',
        height=500
    ).configure_title(
        anchor='middle'
    )
    st.altair_chart(line_chart,use_container_width=True)
    ## Chart per distributor
    five_averages_distributors_modif = st.tabs([five_averages_distributors[0], five_averages_distributors[1], five_averages_distributors[2], five_averages_distributors[3], five_averages_distributors[4]])

    for i in range(len(five_averages_distributors_modif)):
        with five_averages_distributors_modif[i]:
            total_earns_line = alt.Chart(pivot_accumulation_gross_2011_now).mark_line().encode(
                alt.X('year', title='Year'),
                alt.Y(five_averages_distributors[i], title='Accumulation Gross')
            )
            st.altair_chart(total_earns_line,use_container_width=True)

if nav_button_7:
    st.title("Kemunduran 20th Century Fox dari Dunia Bioskop")
    st.write("**Oleh : Christopher Chandra, S. Kom. (12 Juni 2023)**")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1: 

        col3, col4 = st.columns(2)

        with col3:
            st.image('century_fox_logo.png', use_column_width=True, caption='Logo 20th Century Fox')

        with col4:
            st.image('disney_logo.png', use_column_width=True, caption='Logo Disney')

        st.markdown("""
            <p style='text-align: justify;'>20th Century Fox (sekarang adalah 20th Century Studio) dulunya adalah salah satu perusahaan distributor studio perfilman, sebelum akhirnya diakuisisi oleh The Walt Disney Studio untuk menjadi bagian dari anak perusahaannya. Akuisisi tersebut terjadi pada tahun 2019 yang lalu yang di mana The Walt Disney Studio (salah satu divisi dari The Walt Disney Company) itu sendiri membeli sebagian besar aset perusahaan branding Fox dan mengganti semua nama studio yang berelasi dengannya. Kejadian akuisisi tersebut dapat terlihat dari <b>pergerakan saham 20th Century Fox yang di mana tahun 2019 menjadi perhentian terakhirnya</b>. Walaupun demikian, aset fox yang masih tersisa hingga saat ini adalah Fox Corp yang merupakan tayangan berita dan olahraga, dengan jaringan Fox Sports, Fox News, dan Fox TV.</p>
        """, unsafe_allow_html=True)

    with col2:
        shares_line = alt.Chart(pivot_five_avg_biggest).mark_line().encode(
            alt.X('year', title='Tahun'),
            alt.Y("20TH CENTURY FOX", title='Nilai Saham (£)')
        ).properties(
            title='Pergerakan Nilai Saham 20th Century Fox'
        ).configure_title(
            anchor='middle'
        )
        st.altair_chart(shares_line,use_container_width=True)

        five_averages_shares = five_averages_shares.rename(columns={'distributor': 'Studio', 'marketShare': 'Nilai Saham (£)'})
        pivot_five_averages_shares = five_averages_shares.pivot_table(columns='Studio', values='Nilai Saham (£)').reset_index().drop(columns=['index'])
        pivot_five_averages_shares[pivot_distributors_columns]

    st.markdown("""
        <p style='text-align: justify;'>Dari data yang diperoleh dari <em>Box Office Inggris</em> (boxofficedata.co.uk) dengan periode 2011-sekarang, diseleksi lima perusahaan yang memiliki nilai rata-rata pergerakan saham terbesar setiap tahunnya. 20th Century Fox dan The Walt Disney Company adalah dua perusahaan dengan peringkat teratas yang memiliki nilai rata-rata pergerakan saham (tabel sebelah kanan).</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:

        line_chart = alt.Chart(count_films_of_five_2011_now).mark_line(point=True).encode(
            alt.X('year', title='Tahun'),
            alt.Y('film_count', title='Jumlah Film'),
            alt.Color('distributor', title='Distributor', scale=alt.Scale(scheme='category10'), sort=five_averages_distributors)
        ).properties(
            title='Jumlah Film Ditayangkan',
            height=500
        ).configure_title(
            anchor='middle'
        )
        st.altair_chart(line_chart,use_container_width=True)

    with col6:

        line_chart = alt.Chart(accumulation_gross_2011_now).mark_line(point=True).encode(
            alt.X('year', title='Tahun'),
            alt.Y('accumulation_gross', title='Pendapatan Mentah (£)'),
            alt.Color('distributor', title='Distributor', scale=alt.Scale(scheme='category10'), sort=five_averages_distributors)
        ).properties(
            title='Akumulasi Pendapatan Mentah',
            height=500
        ).configure_title(
            anchor='middle'
        )
        st.altair_chart(line_chart,use_container_width=True)

    st.markdown("""
        <p style='text-align: justify;'>Perjalanan dari kedua perusahaan tersebut (20th Century Fox dan The Walt Disney Company) dapat ditinjau dengan melihat perbandingan pergerakan jumlah film yang ditayangkan dan akumulasi perolehan pendapatan mentah. Sepuluh tahun sebelum memasuki pandemi COVID-19 (2020), <b>The Walt Disney Company memasarkan film dengan jumlah paling sedikit</b> dibandingkan dengan empat perusahaan lainnya (juga dengan posisi di bawah 20th Century Fox). Sedangkan 20th Century Fox menempati posisi yang lebih unggul dalam pemasaran film hingga penurunan terjadi dalam 2 tahun terakhir (2018-2019). Walaupun demikian, posisi The Walt Disney Company secara garis besar lebih mendominasi dalam akumulasi perolehan pendapatan mentah dibandingkan dengan perusahaan lainnya. Melalui perbandingan tersebut dapat diasumsikan bahwa film yang dipasarkan oleh The Walt Disney Company memiliki jumlah peminat film yang sangat banyak.</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    col7, col8 = st.columns(2)

    with col7:
        overall_film_showing_status = film_showing_status.loc[(film_showing_status['year'] - film_showing_status['first_launch_year']) != 1].reset_index().drop(columns=['index'])

        pandemic_film_showing_status = overall_film_showing_status.loc[overall_film_showing_status['year'] > 2019].reset_index().drop(columns=['index'])
        pandemic_film_showing_status = pandemic_film_showing_status.groupby([pandemic_film_showing_status['distributor_x'], pandemic_film_showing_status['year'], pandemic_film_showing_status['status']]).agg(film_count = ('status','count')).reset_index()

        chart = alt.Chart(pandemic_film_showing_status).mark_bar().encode(
            x=alt.X('sum(film_count):Q', title='Jumlah Film'),
            y=alt.Y('status:O', title=''),
            color=alt.Color('status:N', legend=None),
            row=alt.Row('distributor_x:N', title='', sort=five_averages_distributors)
        ).properties(
            title='Jumlah Status Penayangan Film Sejak Pandemi',
            height=58
        ).configure_title(
            anchor='middle'
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        )

        st.altair_chart(chart)

    with col8:

        st.markdown("""
            <p style='text-align: justify;'>Memasuki awal masa pandemi (tahun 2020), sebagian besar dari beberapa perusahaan tersebut mengalami penurunan performa, baik dalam jumlah film yang dipasarkan maupun jumlah pendapatan mentahnya yang diperolehnya. Berbeda dengan tiga perusahaan lainnya, jumlah film yang dipasarkan oleh The Walt Disney Company dan Warner Bros meningkat, akan tetapi jumlah pendapatan mentah The Walt Disney Company menurun drastis dan berbanding terbalik dengan angka jumlah pendapatan mentah dari Warner Bros yang meningkat lebih drastis dibandingkan tahun sebelumnya.</p>
        """, unsafe_allow_html=True)

        st.markdown("""
            <p style='text-align: justify;'>Pemasaran / penayangan yang terdaftar dalam Box Office inggris adalah tidak hanya film baru saja, juga terdapat penayangan kembali film yang sudah ditayangkan sebelumnya. Melalui chart di samping didapatkan bahwa mulai dari awal pandemi hingga saat ini, hanya 20th Century Fox sendiri lah yang memiliki angka jumlah penayangan kembali lebih besar dibandingkan dengan jumlah penayangan film baru.</p>
        """, unsafe_allow_html=True)

if nav_button_8:
    st.title("Source")
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Datasets")
    st.markdown(f"[{'Box Office Data'}]({'https://boxofficedata.co.uk'})")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Articles")
    st.markdown(f"[{'20th Century Studios - Wiki'}]({'https://en.wikipedia.org/wiki/20th_Century_Studios'})")
    st.markdown(f"[{'20th Century Studios - Ensiklopedoa Dunia'}]({'https://p2k.stekom.ac.id/ensiklopedia/20th_Century_Studios'})")
    st.markdown(f"[{'Disney Akhiri Sejarah 20th Century Fox Setelah 85 Tahun Produksi'}]({'https://www.inews.id/finance/bisnis/disney-akhiri-sejarah-20th-century-fox-setelah-85-tahun-produksi'})")
    st.markdown(f"[{'Akuisisi Fox Bikin Amunisi Disney Semakin Komplit'}]({'https://lifestyle.sindonews.com/berita/1433258/158/akuisisi-fox-bikin-amunisi-disney-semakin-komplit'})")


if nav_button_9:
    st.title("Source")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: justify;'>Hello, my name is Christopher Chandra. I created this simple dashboard and simple analysis story in purpose of practicing data science, and also as my capstone project in my data analytics course from DQLab Indonesia.</p>
    """, unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: justify;'>These creations are still too far from perfect, so feel free to dropby to my email for any critics and suggestions you wanna share : arimayuuto.db@gmail.com</p>
    """, unsafe_allow_html=True)
    st.markdown(f"[{'And also u can dropby to my Linkedin'}]({'https://www.linkedin.com/in/christopher-chandra-000/'})")
