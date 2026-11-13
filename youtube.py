import os
from dotenv import load_dotenv

load_dotenv()
print("MongoDB URI loaded:", bool(os.getenv("MONGODB_URI")))
print("MongoDB Atlas:", os.getenv("MONGODB_URI", "").startswith("mongodb+srv://"))


Api_key=os.getenv("YOUTUBE_API_KEY")
from googleapiclient.discovery import build
from pprint import pprint
import pymongo
import mysql.connector
import pandas as pd
import streamlit as st
import isodate

api_service_name = "youtube"
api_version = "v3"
youtube =build(api_service_name, api_version, developerKey=Api_key)

mydb = mysql.connector.connect(
host="localhost",
user="root",
password="",
database= "youtube_data"

)

mycursor = mydb.cursor(buffered=True)


# Getting Channel Information

def get_Channelinfo(Channel_ID):
    api_service_name = "youtube"
    api_version = "v3"
    youtube =build(api_service_name, api_version, developerKey=Api_key)


    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=Channel_ID
    )
    response = request.execute()

    Ch_data = dict(Channel_Name = response["items"][0]["snippet"]['title'],
                    channel_ID = response["items"][0]["id"], 
                    Description = response["items"][0]["snippet"]['description'],
                    Subscribers = response["items"][0]['statistics']["subscriberCount"],
                    Published_On = response["items"][0]["snippet"]["publishedAt"],
                    Video_Count = response["items"][0]['statistics']["videoCount"],
                    View_Count = response["items"][0]["statistics"]["viewCount"],
                    Playlist_ID = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])
    return Ch_data



# Getting video IDs

def get_Video_IDs(Channel_ID):
    Video_ID = []
    request = youtube.channels().list(
        part="contentDetails",
        id= Channel_ID
    )
    response = request.execute()

    Play_ID = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    next_page_token = None

    while True:
        
        request1= youtube.playlistItems().list(
                                        part="snippet,contentDetails",playlistId= Play_ID,
                                        maxResults=50,
                                        pageToken=next_page_token
        )
        response1= request1.execute()

        
        for i in range(len(response1["items"])):
            Video_ID.append(response1["items"][i]["snippet"]["resourceId"]["videoId"])
            next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break

    return Video_ID

 

#Getting Video information

def get_VideoInfo(Total_Vid_ID):
    Video_Data = []
    for videoid in Total_Vid_ID:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=videoid
        )
        response = request.execute()

        Vid_data = dict (Video_Name= response["items"][0]["snippet"]["title"],
                        Channel_Name = response["items"][0]["snippet"]["channelTitle"],
                        Video_ID = response["items"][0]["id"],
                        Channel_ID = response["items"][0]["snippet"]["channelId"],
                        Video_Description= response["items"][0]["snippet"].get("description"),
                        Published_On = response["items"][0]["snippet"]["publishedAt"],
                        View_Count = response["items"][0]["statistics"].get("viewCount"),
                        Like_Count = response["items"][0]["statistics"].get("likeCount"),
                        Favourite_Count= response["items"][0]["statistics"]["favoriteCount"],
                        Comment_Count = response["items"][0]["statistics"].get("commentCount"),
                        Duration = response["items"][0]["contentDetails"]["duration"],
                        Thumbnails = response["items"][0]["snippet"]["thumbnails"]["default"]["url"],
                        Caption_Status= response["items"][0]["contentDetails"]["caption"]
                        )

        Video_Data.append(Vid_data)
    
    return Video_Data



# Getting Comment Informations

def get_Comment_Info(Total_Vid_ID):
    Comment_Details = []
    try:
        for videoid in Total_Vid_ID:
            request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=videoid,
            maxResults=50
            )
            response = request.execute()

            Comm_Data = dict(Comment_ID= response["items"][0]["snippet"]["topLevelComment"]["id"],
                                Video_ID= response["items"][0]["snippet"]["videoId"],
                                Comment_Text = response["items"][0]["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                                Comment_Author = response["items"][0]["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                Comment_Published_Date = response["items"][0]["snippet"]["topLevelComment"]["snippet"]["publishedAt"])

            Comment_Details.append(Comm_Data)
    except:
        pass

    return Comment_Details



# Getting Playlist information

def get_Playlist_Info(Channel_ID):
    
    Playlist = []
    next_page_token = None

    while True:

        request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=Channel_ID,
            maxResults=50,
            pageToken= next_page_token
        )
        response = request.execute()

    

        for i in range(len(response["items"])):
            
            Play_Data = dict(Playlist_ID = response["items"][i]["id"],
                            Channel_ID = response["items"][i]["snippet"]["channelId"],
                            Playlist_Name = response["items"][i]["snippet"]["title"],
                            Channel_Name = response["items"][i]["snippet"]["channelTitle"],
                            Video_Count = response["items"][i]["contentDetails"]["itemCount"],
                            Published_On = response["items"][i]["snippet"]["publishedAt"])

            Playlist.append(Play_Data)
        next_page_token=response.get('nextPageToken')
        
        if next_page_token is None:
            break
        
    return Playlist



# Uploading in mongodb

client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
database=client.youtube_data
collection1=database.channel_details



def channel_details(Channel_ID):
    ch_details=get_Channelinfo(Channel_ID)
    play_details=get_Playlist_Info(Channel_ID)
    vd_ids=get_Video_IDs(Channel_ID)
    vd_details=get_VideoInfo(vd_ids)
    cmt_details=get_Comment_Info(vd_ids)

    collection1.insert_one({"channel_information":ch_details,
                            "playlist_information":play_details,
                            "video_information":vd_details,
                            "comment_information":cmt_details})
    
    return "Upload done"
    


# Creating table for Channels:

def Channels_Table(Name_of_the_channel):

    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database= "youtube_data"
    )
    mycursor = mydb.cursor(buffered=True)


    mycursor.execute('''create table if not exists channels(Channel_Name VARCHAR(100),
                                                            channel_ID VARCHAR(50) primary key,
                                                            Description TEXT,
                                                            Subscribers BIGINT,
                                                            Published_On VARCHAR(50),
                                                            Video_Count INT,
                                                            View_Count BIGINT,
                                                            Playlist_ID VARCHAR(50))''')
    mydb.commit()


    Channel_det=[]
    database=client.youtube_data
    collection1=database.channel_details

    for ch_data in collection1.find({"channel_information.Channel_Name":Name_of_the_channel},{"_id":0}):
        Channel_det.append(ch_data["channel_information"])

    df_ChannelInfo = pd.DataFrame(Channel_det)


    for index,row in df_ChannelInfo.iterrows():
        insert_query='''insert into channels(Channel_Name,
                                            channel_ID,
                                            Description,
                                            Subscribers,
                                            Published_On,
                                            Video_Count,
                                            View_Count,
                                            Playlist_ID)
                                            values(%s,%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['channel_ID'],
                row['Description'],
                row['Subscribers'],
                row['Published_On'],
                row['Video_Count'],
                row['View_Count'],
                row['Playlist_ID'])
        

        try:
            mycursor.execute(insert_query,values)
            mydb.commit()
        except:
             msg=f"OOPS SORRY!!! The details of  {Name_of_the_channel} is inserted already"
             return msg



# Creating Table for Playlists:

def Playlists_Table(Name_of_the_channel):

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database= "youtube_data"

        )
        mycursor = mydb.cursor(buffered=True)


        mycursor.execute('''create table if not exists playlists(Playlist_ID VARCHAR(100) primary key,
                                                                Channel_ID VARCHAR(50),
                                                                Playlist_Name VARCHAR(100),
                                                                Channel_Name VARCHAR(50),
                                                                Video_Count INT,
                                                                Published_On TIMESTAMP
                                                                )''')
        mydb.commit()

        Playlist_det=[]
        database=client.youtube_data
        collection1=database.channel_details

        for ch_data in collection1.find({"channel_information.Channel_Name":Name_of_the_channel},{"_id":0}):
                Playlist_det.append(ch_data["playlist_information"])

        df_PlaylistInfo = pd.DataFrame(Playlist_det[0])


        for index,row in df_PlaylistInfo.iterrows():
                insert_query1='''insert into playlists(Playlist_ID,
                                                Channel_ID,
                                                Playlist_Name,
                                                Channel_Name,
                                                Video_Count,
                                                Published_On
                                                )
                                                values(%s,%s,%s,%s,%s,%s)'''
                values1=(row['Playlist_ID'],
                        row['Channel_ID'],
                        row['Playlist_Name'],
                        row['Channel_Name'],
                        row['Video_Count'],
                        row['Published_On']
                        )
                
                mycursor.execute(insert_query1,values1)
                mydb.commit()                          




# Creating table for Videos 

def Videos_Table(Name_of_the_channel):

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database= "youtube_data"

        )

        mycursor = mydb.cursor(buffered=True)


        mycursor.execute('''create table if not exists videos(Video_Name VARCHAR(100),
                                                                Channel_Name VARCHAR(50),
                                                                Video_ID VARCHAR(30) primary key,
                                                                Channel_ID VARCHAR(50),
                                                                Video_Description TEXT,
                                                                Published_On TIMESTAMP,
                                                                View_Count BIGINT,
                                                                Like_Count BIGINT,
                                                                Favourite_Count INT,
                                                                Comment_Count BIGINT,
                                                                Duration INT,
                                                                Thumbnails VARCHAR(100),
                                                                Caption_Status VARCHAR(10),
                                                                Duration_Seconds INT
                                                                )''')
        mydb.commit()


        Video_det=[]
        duration_iso=[]
        Duration_Seconds=[]
        database=client.youtube_data
        collection1=database.channel_details

        for ch_data in collection1.find({"channel_information.Channel_Name":Name_of_the_channel},{"_id":0}):
                Video_det.append(ch_data["video_information"])

        df_VideoInfo = pd.DataFrame(Video_det[0])

        for i in Video_det[0]:
                duration_iso.append(i["Duration"])

        for duration in duration_iso:
                seconds=int(isodate.parse_duration(duration).total_seconds())
                Duration_Seconds.append(seconds)

        df_VideoInfo["Duration_Seconds"]=Duration_Seconds



        for index,row in df_VideoInfo.iterrows():
                        insert_query2='''insert into videos(Video_Name,
                                                                Channel_Name,
                                                                Video_ID,
                                                                Channel_ID,
                                                                Video_Description,
                                                                Published_On,
                                                                View_Count,
                                                                Like_Count,
                                                                Favourite_Count,
                                                                Comment_Count,
                                                                Duration,
                                                                Thumbnails,
                                                                Caption_Status,
                                                                Duration_Seconds
                                                        )
                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        values2=(row['Video_Name'],
                                row['Channel_Name'],
                                row['Video_ID'],
                                row['Channel_ID'],
                                row['Video_Description'],
                                row['Published_On'],
                                row['View_Count'],
                                row['Like_Count'],
                                row['Favourite_Count'],
                                row['Comment_Count'],
                                row['Duration'],
                                row['Thumbnails'],
                                row['Caption_Status'],
                                row['Duration_Seconds']
                                )
                        
                
                        mycursor.execute(insert_query2,values2)
                        mydb.commit()
                       




# Creating table for Comments

def Comments_Table(Name_of_the_channel):

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database= "youtube_data"

        )

        mycursor = mydb.cursor(buffered=True)


        mycursor.execute('''create table if not exists comments(Comment_ID VARCHAR(100) primary key,
                                                                Video_ID VARCHAR(50),
                                                                Comment_Text TEXT,
                                                                Comment_Author VARCHAR(50),
                                                                Comment_Published_Date TIMESTAMP
                                                                )''')
        mydb.commit()

        Comments_det=[]
        database=client.youtube_data
        collection1=database.channel_details

        for ch_data in collection1.find({"channel_information.Channel_Name":Name_of_the_channel},{"_id":0}):
                Comments_det.append(ch_data["comment_information"])

        df_CommentInfo = pd.DataFrame(Comments_det[0])


        for index,row in df_CommentInfo.iterrows():
                        insert_query3='''insert into comments(Comment_ID,
                                                                Video_ID,
                                                                Comment_Text,
                                                                Comment_Author,
                                                                Comment_Published_Date
                                                        )
                                                        values(%s,%s,%s,%s,%s)'''
                        values3=(row['Comment_ID'],
                                row['Video_ID'],
                                row['Comment_Text'],
                                row['Comment_Author'],
                                row['Comment_Published_Date']
                                )
                        
                
                        mycursor.execute(insert_query3,values3)
                        mydb.commit()
                                                                     



def All_Tables(One_channel):
   msg=Channels_Table(One_channel)
   if msg:
      return msg
   else:
      Playlists_Table(One_channel)
      Videos_Table(One_channel)
      Comments_Table(One_channel)
      return "Details Inserted In Table Successfully"



def Channels_Dataframe():
    ch_list=[]
    database=client.youtube_data
    collection1=database.channel_details


    for ch_data in collection1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=st.dataframe(ch_list)

    return df



def Playlists_Dataframe():    
    pl_list=[]
    database=client.youtube_data
    collection1=database.channel_details

    for pl_data in collection1.find({},{"_id":0,"playlist_information":1}):
            for i in range(len(pl_data["playlist_information"])):
                    pl_list.append(pl_data["playlist_information"][i])

    dfplay=st.dataframe(pl_list)

    return dfplay



def Videos_Dataframe():
    vid_list=[]
    database=client.youtube_data
    collection1=database.channel_details


    for vid_data in collection1.find({},{"_id":0,"video_information":1}):
            for i in range(len(vid_data["video_information"])):
                    vid_list.append(vid_data["video_information"][i])

    dfvid=st.dataframe(vid_list)

    return dfvid



def Comments_Dataframe():
    cmt_list=[]
    database=client.youtube_data
    collection1=database.channel_details


    for cmt_data in collection1.find({},{"_id":0,"comment_information":1}):
            for i in range(len(cmt_data["comment_information"])):
                    cmt_list.append(cmt_data["comment_information"][i])

    dfcomment=st.dataframe(cmt_list)

    return dfcomment



# Exhibiting in Streamlit 
import streamlit as st
import time as t


st.balloons()
st.title(":blue[Youtube Data Harvesting And Warehousing]")
st.sidebar.header(":violet[Skills used]")
st.sidebar.caption("Python")
st.sidebar.caption("Data Manipulation using SQL and MongoDB")
st.sidebar.caption("API Integration")
st.sidebar.caption("Streamlit web app")

Channel_ID=st.text_input(":green[Enter the Channel Id]")
if st.button("Submit"):
    ch_ids=[]
    database=client.youtube_data
    collection1=database.channel_details
    for i in collection1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(i["channel_information"]["channel_ID"])
    if Channel_ID in ch_ids:
        st.error("Channel already exists")
    else:
        insert=channel_details(Channel_ID)
        st.success(insert)

Submitted_Channels=[]
database=client.youtube_data
collection1=database.channel_details

for ch_data in collection1.find({},{"_id":0,"channel_information":1}):
    Submitted_Channels.append(ch_data["channel_information"]["Channel_Name"])

Channels_Available=st.selectbox("Select the channel Name",Submitted_Channels)
        

if st.button("Insert details in Table"):
    Tables=All_Tables(Channels_Available)
    st.success(Tables)


Radio=st.radio("Choose the table name to view details",["Channels","Playlists","Videos","Comments"])
if Radio=="Channels":
    Channels_Dataframe()
elif Radio=="Playlists":
    Playlists_Dataframe()
elif Radio=="Videos":
    Videos_Dataframe()
elif Radio=="Comments":
    Comments_Dataframe()


Questions=st.selectbox("Select the Query",["1.What are the name of all the videos with Channel name?",
                                 "2.Which channels has most number of videos and the count?",
                                 "3.Top 10 most viewed videos and the channel name?",
                                 "4.Total comments of each video with the Video name?",
                                 "5.Which video has highest likes and the channel name?",
                                 "6.What is the count of all likes of each video with the corresponding video name?",
                                 "7.What is the total no.of views of each channel with their corresponding channel name?",
                                 "8.The name of the channels which published videos in 2022?",
                                 "9.What is the average duration of all the videos with channel names?",
                                 "10.Highest commented videos with the channel names"])

if Questions=="1.What are the name of all the videos with Channel name?":
    mycursor.execute("SELECT Video_Name, Channel_Name From videos")
    mydb.commit()
    out1=mycursor.fetchall()
    querry1=pd.DataFrame(out1,columns=["Video_Name","Channel_Name"])
    st.write(querry1)

elif Questions=="2.Which channels has most number of videos and the count?":
    mycursor.execute("SELECT Channel_Name,Video_Count FROM Channels ORDER BY Video_Count DESC")
    mydb.commit()
    out2=mycursor.fetchall()
    querry2=pd.DataFrame(out2,columns=["Channel Name","Video Count"])
    st.write(querry2)

elif Questions=="3.Top 10 most viewed videos and the channel name?":
    mycursor.execute("SELECT Video_Name,View_Count,Channel_Name FROM Videos WHERE View_Count is not null ORDER BY View_Count DESC LIMIT 10")
    mydb.commit()
    out3=mycursor.fetchall()
    querry3=pd.DataFrame(out3,columns=["Video Name","View Count","Channel Name"])
    st.write(querry3)

elif Questions=="4.Total comments of each video with the Video name?":
    mycursor.execute("SELECT Video_Name,Comment_Count FROM Videos")
    mydb.commit()
    out4=mycursor.fetchall()
    querry4=pd.DataFrame(out4,columns=["Video Name ","Comment Count"])
    st.write(querry4)

elif Questions=="5.Which video has highest likes and the channel name?":
    mycursor.execute("SELECT Video_Name,Like_Count,Channel_Name FROM Videos ORDER BY Like_Count DESC LIMIT 1")
    mydb.commit()
    out5=mycursor.fetchall()
    querry5=pd.DataFrame(out5,columns=["Video Name ","Like Count","Channel Name"])
    st.write(querry5)

elif Questions=="6.What is the count of all likes of each video with the corresponding video name?":
    mycursor.execute("SELECT Video_Name,Like_Count FROM Videos")
    mydb.commit()
    out6=mycursor.fetchall()
    querry6=pd.DataFrame(out6,columns=["Video Name ","Like Count"])
    st.write(querry6)

elif Questions=="7.What is the total no.of views of each channel with their corresponding channel name?":
    mycursor.execute("SELECT Channel_Name,View_Count FROM Channels")
    mydb.commit()
    out7=mycursor.fetchall()
    querry7=pd.DataFrame(out7,columns=["Channel Name","View Count"])
    st.write(querry7)

elif Questions=="8.The name of the channels which published videos in 2022?":
    mycursor.execute("SELECT Channel_Name,Video_Name,Published_On FROM Videos WHERE EXTRACT(YEAR from Published_On)=2022")
    mydb.commit()
    out8=mycursor.fetchall()
    querry8=pd.DataFrame(out8,columns=["Channel Name","Video Name","Released on 2022"])
    st.write(querry8)

elif Questions=="9.What is the average duration of all the videos with channel names?":
    mycursor.execute("SELECT Channel_Name,AVG(Duration_Seconds)as Average_Duration FROM Videos GROUP BY Channel_Name")
    mydb.commit()
    out9=mycursor.fetchall()
    querry9=pd.DataFrame(out9,columns=["Channel Name","Average Duration in Seconds"])
    st.write(querry9)

elif Questions=="10.Highest commented videos with the channel names":
    mycursor.execute("SELECT Video_Name,Channel_Name,Comment_Count FROM Videos ORDER BY Comment_Count DESC LIMIT 10")
    mydb.commit()
    out10=mycursor.fetchall()
    querry10=pd.DataFrame(out10,columns=["Video Name","Channel Name","Comment_Count"])
    st.write(querry10)





