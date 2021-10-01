from numpy.core.fromnumeric import size
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# price and salers
# ranking time without promotion (+platform)
#  login = name + platform naeme (Steam/Microsoft etc.)
# https://github.com/PablocFonseca/streamlit-aggrid


def app(data,data_whs):
    #data_df = preprocess_data(load_metadata_forecast())


    st.title('Promo Overview and Performance')
    col1, col2 = st.beta_columns([1,3])

    #st.sidebar("Vizualisations")

    # with col0:
    #     st.write("Promo Name")
    #     st.write("Title Series")
    #     st.write("Title")
    #     st.write("Publisher")
    
    with col1:
        selection = construct_filters(data)

    with col2:
        with st.beta_container():
            # with st.beta_expander("Performance Graph"):
            #     values = ["Agents of Mayhem","Saints Row 2","Saints Row IV","Homefront: The Revolution - Expansion Pass"] #Title
            #     data_plot = combine_data(data_df,'Date','Gross Steam Sales (USD)','Game',values)
            #     data_plot['Date'] = pd.to_datetime(data_plot["Date"].dt.strftime('%Y-%m'))
            #     st.write(data_plot.head())
            #     data_df = data_df[data_df.Game.isin([values])]
            #     data_df.plot()

            #     fig, axs = plt.subplots(nrows = 2, ncols = 1, figsize = (10,5))
            #     #ax = data_plot(x='Date',y = ["Gross Steam Sales (USD)","Gross Steam Sales (USD)_x"])
            #     axs[0] = sns.lineplot(data = data_plot)
            #     #ax0.set_xticklabels(['2019-01','2019-02','2019-03','2019-04','2019-05','2019-06','2019-07','2019-08','2019-09','2019-10','2019-11','2019-12'])

            #     axs[1] = sns.relplot(x = "Date", y = "Gross Steam Sales (USD)", kind = 'line', data = data_df)
            #     axs[1].fig.autofmt_xdate()
            #     # #plt.legend(values)
            #     st.write(fig)

            filt = data.Promo_Name.isin(selection[0]) & data.Title_Series.isin(selection[1]) & data.Title.isin(selection[2]) & data.Publisher.isin(selection[3])
            selected_data = data[filt]
            st.table(selected_data)
    
    grouped = data.groupby(by = "Title_Series")
    st.write(grouped.sum())
            
def construct_filters(df):

    promo_name = st.selectbox(
        f"Promo Name",
        df.Promo_Name.unique()
    )

    title_series = st.selectbox(
        f"Title Series",
        sorted(df.Title_Series.unique())
    )
    
    title = st.multiselect(
        f"Title",
        sorted(df.Title[df.Title_Series.isin([title_series])].unique())
    )

    publisher = df[df.Title_Series.isin([title_series])].Publisher.unique().item()
    st.write("Publisher:", publisher)
    
    # publisher = st.selectbox(
    #     f"Publisher",
    #     sorted(df.Publisher.unique())
    # )

    start_period, end_period = st.select_slider(
    'When do you start?',
    options=['01/01/2019', '01/01/2020', '01/01/2021','01/01/2022','01/01/2023'],
    value=('01/01/2019', '01/01/2023'))
    st.write("Range:", start_period, end_period)

    #st.checkbox("Checkboxes")

    start_time = st.slider(
    "When do you start?",
     value=datetime(2020, 1, 1, 9, 30), 
     format="MM/DD/YY -hh:mm"
)

#     cols1, _ = st.beta_columns((1,2))
#     slider = cols1.slider('Select date', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)

    values = [[promo_name], [title_series], title, [publisher], start_period, end_period]
    for n,i in enumerate(values):
        if not isinstance(i, list):
            # If type is not list then make it list
            values[n] = [values]

    return values

@st.cache(allow_output_mutation=True)
def load_metadata_forecast():
    #DATA_URL = "C:\\Users\\o.georgievskiy\\Koch Media GmbH\\Internship - Oleg Georgievskiy - General\\Promo Tracker\\Promo_Old_c.csv"
    #df = pd.read_csv(DATA_URL, delimiter = ";", index_col="Promo_ID")   #check for delimiter in csv or other file format adjust accordingly
    PATH = "C:\\Users\\o.georgievskiy\\Koch Media GmbH\\Internship - Oleg Georgievskiy - General\\Forecasting\\"
    filename = "Data for Arima.csv"     
    df = pd.read_csv(PATH+""+filename, header = 0, skiprows = 2, index_col=0, parse_dates = True)   #check for delimiter in csv or other file format adjust accordingly
    df.columns = df.columns.str.strip()
    return df

@st.cache(allow_output_mutation=True)
def preprocess_data(data_df):
    filt = (data_df["Net Units Sold"]<0) & (data_df["Gross Units Sold"]>0)
    data_df = data_df[~filt].copy()
    #Add "Discount anti-rate" (share of original price)
    data_df["Discount"] = data_df["Sale Price"]/data_df["Base Price"]
    #data_df.Date = pd.to_datetime(data_df.Date, format = "%m%d%Y")
    return data_df
    #taking Numerical values by groupby
    # grouped = data_df[all_values].groupby(["Date"]).sum()
    # grouped["Average_Discount"] = grouped["Sale Price"]/grouped["Base Price"]
    #grouped.reset_index(inplace = True)


# ind = 'Date', what=Amounts/Sales/etc, by_what = Title/Title_Series/Publisher/Platform.., games = 
# Returns a dataframe with what-game columns side by side. Index = "Date"
@st.cache(allow_output_mutation=True)
def combine_data(df, ind, what,by_what, values):
    all_values = ["Gross Steam Sales (USD)","Net Steam Sales (USD)",'Net Units Sold','Base Price','Sale Price', 'Discount']
    df = df.groupby([by_what,ind])[all_values].sum().reset_index()
    y_val = df[[ind,by_what,what]].set_index([ind],append=True)
    data_plot = pd.DataFrame(columns = [ind,by_what,what])
    for value in values:
        i = 1
        data_plot = y_val[y_val.loc[:,by_what].isin([value])].merge(data_plot,how = 'left',on = ind)
        # data_plot.columns.values[i] = "{}_{}".format(what,value)
        # data_plot.columns.values[i+1] = "{}_{}".format(by_what,value)
        data_plot.columns.values[i] = "{}".format(value)
        data_plot.columns.values[i+1] = "{}_{}".format(what,value)
    
    #data_plot.loc[:,ind] = pd.to_datetime(data_plot.loc[:,ind]).strftime('%m%d%Y')
    return data_plot.iloc[:,:-2] #for some reason additional 2 columsn appear at the end


# p = df.pivot_table(index=['Hour'], columns='DOW', values='Changes', aggfunc=np.mean).round(0)
# p.fillna(0, inplace=True)

# columns = ["1Sun", "2Mon", "3Tue", "4Wed", "5Thu", "6Fri", "7Sat"]
# p = p.reindex(columns=columns)
# p[columns] = p[columns].astype(int)


# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# import plotly.graph_objects as go
# st.title("Welcome to Streamlit!")

# fig = go.Figure(
#     data=[go.Pie(
#         labels=['A', 'B', 'C'],
#         values=[30, 20, 50]
#     )]
# )
# fig = fig.update_traces(
#     hoverinfo='label+percent',
#     textinfo='value',
#     textfont_size=15
# )

# st.write("Pie chart in Streamlit")
# st.plotly_chart(fig)


    # st.sidebar.markdown(
    #     '<p class="header-style">Choose Filters</p>',
    #     unsafe_allow_html=True
    # )


# names = [{'name':'Jay', 'value':'1'},{'name':'roc', 'value':'9'},{'name':'Jay', 'value':'7'},
#          {'name':'roc', 'value':'2'}]

# df = pd.DataFrame(names)
# df['value'] = df['value'].astype(int)
# group = df.groupby('name')['value'].sum().to_dict()
# result = [{'name': name, 'value': value} for name, value in group.items()]

# DATE_FORMAT = "%m/%d/%Y"
#     b = datetime.today().strftime('%m/%d/%Y')

# st.markdown("<hr>", unsafe_allow_html=True)
#     a = st.sidebar.text_input('startdate (mm/dd/yyyy)',"01/29/2021")

# try:
#         startx = dt.datetime.strptime(a,'%m/%d/%Y').date()
#         #numberofcasesdayzero = int(numberofcasesdayz)
#     except:
#         st.error("Please make sure that the date is in format mm/dd/yyyy")
#         st.stop()

#  NUMBEROFDAYS = st.sidebar.slider('Number of days in graph', 15, 720, 60)
#     global numberofdays_
#     numberofdays_ = NUMBEROFDAYS

#  d1 = datetime.strptime(a, '%m/%d/%Y')
#         d2 = datetime.strptime(turningpointdate,'%m/%d/%Y')
#         if d2<d1:
#             st.error("Turning point cannot be before startdate")
#             st.stop()
#         turningpoint =  abs((d2 - d1).days)



# # Some manipulation of the x-values (the dates)
#     then = startx + dt.timedelta(days=NUMBEROFDAYS)
#     x = mdates.drange(startx,then,dt.timedelta(days=1))  #import matplotlib.dates as mdates
#     # x = dagnummer gerekend vanaf 1 januari 1970 (?)
#     # y = aantal gevallen
#     # z = dagnummer van 1 tot NUMBEROFDAYS
#     z  = np.array(range(NUMBEROFDAYS))

#     a_ = dt.datetime.strptime(a,'%m/%d/%Y').date()
#     b_ = dt.datetime.strptime(b,'%m/%d/%Y').date()
#     datediff = ( abs((a_ - b_).days))


# disclaimernew=('<style> .infobox {  background-color: lightyellow; padding: 10px;margin: 20-px}</style>'
#                 '<div class=\"infobox\"><h3>Disclaimer</h3><p>For illustration purpose only.</p>'
#                 '<p>Attention: these results are different from the official models'
#                 ' probably due to simplifications and different (secret) parameters.'
#                 '(<a href=\"https://archive.is/dqOjs\" target=\"_blank\">*</a>) '
#                     'The default parameters on this site are the latest known parameters of the RIVM'
#                     '</p><p>Forward-looking projections are estimates of what <em>might</em> occur. '
#                     'They are not predictions of what <em>will</em> occur. Actual results may vary substantially. </p>'
#                     '<p>The goal was/is to show the (big) influence of (small) changes in the R-number. '
#                 'At the bottom of the page are some links to more advanced (SEIR) models.</p></div>')

#     st.markdown(disclaimernew,  unsafe_allow_html=True)



# with st.beta_expander("Show bargraph per week - Attention - doesn't display well when there are two years involved and/or the weeks aren't complete. Weeks are Monday until Sunday"):
#     #     fig1x = plt.figure()
#     #     output.plot()
#     #     plt.legend(loc='best')
#     #     #st.pyplot(fig1x)
#     #     #st.write(fig1x)
#     #     titlex="Number of casees per week"
#     #     configgraph(titlex)

#     #     st.bar_chart(output)