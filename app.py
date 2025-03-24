import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS

#run using: streamlit run app.py
st.title('Sentiment Analysis of Tweets about US Airlines')
st.sidebar.title('Sentiment Analysis of Tweets about US Airlines')

st.markdown("Streamlit Dashboard for Analysing Tweet Sentiments")
st.sidebar.markdown("Streamlit Dashboard for Analysing Tweet Sentiments")

DATA_PATH= 'Tweets.csv'

@st.cache_data
#store the results of expensive function calls and reuse them when the function is called with the same arguments again

def load_data(path):
    data=pd.read_csv(path)
    data['tweet_created']=pd.to_datetime(data['tweet_created'])
    return data

data=load_data(DATA_PATH)

#st.write(data) #writes it to page

st.sidebar.subheader("Show Random Tweet")
options= data['airline_sentiment'].unique()
random_tweet= st.sidebar.radio('Sentiment',options)

random_tweet_text=data.query("airline_sentiment == @random_tweet")[["text"]].sample(n=1).iloc[0,0] #using query of pandas
#In Pandas .query() function, the @ symbol is used to reference Python variables inside the query string.
#"airline_sentiment == @random_tweet" is a string-based query expression.
#The @ symbol tells Pandas to look for a variable named random_tweet in the Python environment and use its value in the query.
#This replaces @random_tweet with the actual value stored in random_tweet

st.sidebar.markdown(random_tweet_text)


st.sidebar.subheader('Number of Tweets by Sentiment')
drop_op=['Histogram','Pie Chart']
drop_select= st.sidebar.selectbox('Visualisation Type',drop_op,key='1')
#key used so that streamlit doesnt confuse state of this widget with another select box widget later

sentiment_count= data['airline_sentiment'].value_counts()
sentiment_count= pd.DataFrame({'Sentiment':sentiment_count.index, 'Tweets':sentiment_count.values})

if not(st.sidebar.checkbox('Hide',True,key='2')):
    #by default checkbox is hidden so that visualisations appear only when required by user
    st.markdown("## Number of Tweets by Sentiment")
    if(drop_select=='Histogram'):
        figure=px.bar(sentiment_count,x='Sentiment',y='Tweets',color='Sentiment',height=500)
        st.plotly_chart(figure)
    elif(drop_select=='Pie Chart'):
        figure=px.pie(sentiment_count,names='Sentiment',values='Tweets')
        st.plotly_chart(figure)

#st.map(data) #to get location of user tweeting

st.sidebar.subheader('When and where are users tweeting from?')
min_time=0 #12am
max_time=23 #11pm
hour=st.sidebar.slider('Hour of day (24 Hour Format)',min_time,max_time)
#can also use:
#hour=st.sidebar.number_input('Hour of day (24 Hour Format)',min_value=min_time,max_value=max_time)
modified_data= data[data['tweet_created'].dt.hour == hour]

if not (st.sidebar.checkbox('Close',True,key='3')):
    st.markdown("## Tweets Location Based on Time of Day")
    st.markdown('##### **%i tweets between %i:00 and %i:00**'%(len(modified_data),hour,(hour+1)%24))
    st.map(modified_data)

    if (st.sidebar.checkbox("Show raw data",False)):
        st.markdown('##### **Raw data for Tweets shown on Map between %i:00 and %i:00**'%(hour,(hour+1)%24))
        st.write(modified_data)


st.sidebar.subheader('Breakdown Airline Tweets by Sentiments')
air_options=data['airline'].unique()
air_choice=st.sidebar.multiselect('Choose Airlines (Multiple)',air_options,key='4')

if len(air_choice)>0:
    air_choice_data= data[data['airline'].isin(air_choice)] 
    #ensures airlines selected from original dataframe are those selected by user
    figure_air=px.histogram(air_choice_data,x='airline',y='airline_sentiment',
                            histfunc='count',color='airline_sentiment',
                            facet_col='airline_sentiment',labels={'airline_sentiment':'tweets'},
                            height=600, width=800) 
    
    #histfunc applies a function on y axis. Here, each airline_sentiment is counted for each selected airline
    #facet_col will give individual bar chart columns for each airlines based on airline_sentiment so each airline will
    #have separate bars for positive,negative and neutral tweets

    #labels={'airline_sentiment':'tweets'} renames 'airline_sentiment' to 'tweets' 
    
    st.markdown("## Airlines Tweets By Sentiments")
    st.plotly_chart(figure_air)


st.sidebar.header("Word Cloud")
word_sentiment=st.sidebar.radio('Display word cloud for chosen sentiment',options,key='5')
#options was used to previously store sentiments

if not (st.sidebar.checkbox('Close Word Cloud',True,key='6')):
    st.markdown("## Word Cloud for Sentiment: '%s'"%word_sentiment)

    sentiment_data=data[data['airline_sentiment']==word_sentiment]
    words= ' '.join(sentiment_data['text'])
    processed_words= ' '.join([word for word in words.split() 
                               if 'http' not in word and not word.startswith('@')
                               and word!='RT'])  #RT means retweet
    
    wordcloud=WordCloud(stopwords=STOPWORDS,height=640,width=800).generate(processed_words)
    #stopwords are words to be excluded

    # plt.imshow(wordcloud)
    # plt.xticks([])
    # plt.yticks([])

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear") 
    #"bilinear" is generally preferred for word clouds—it creates a smoother image
    ax.axis("off")  # Hides axis ticks
    st.pyplot(fig)