import chromadb
import feedparser
import re
import torch
import embedClustering

import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from sklearn.manifold import TSNE
import pandas as pd
matplotlib.use('Agg')

from wordcloud import WordCloud, STOPWORDS
from newspaper import Article
from SonarEmbeddingFunction import SonarEmbeddingFunction
from chromadb.utils import embedding_functions
from tqdm import tqdm

from textblob import TextBlob

import nltk
import os


from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def uniquify_path(path):
    # If the path does not exist, return it as is
    if not os.path.exists(path):
        return path
    
    # Split the file name and extension
    base, ext = os.path.splitext(path)
    
    # Start with the number 1 and keep appending it until the path is unique
    counter = 1
    new_path = f"{base}_{counter}{ext}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base}_{counter}{ext}"
    
    return new_path

def extract_article_text(url):
        article = Article(url)
        try:
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
            return None
    
def clean_text(text):
    
    text = re.sub(r'https?://\S+|www\.\S+', '', str(text)) 

    text = re.sub(r'\n+', ' ', text)
        
    cleaned_text = re.sub(r'[^A-Za-z0-9\s]+', '', text)

    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
    cleaned_lemmatized_text = cleaned_text.lower() 

    cleaned_lemmatized_text = re.sub('[^a-z]', ' ', cleaned_lemmatized_text) 
        
    cleaned_lemmatized_text = cleaned_lemmatized_text.split() 

    cleaned_lemmatized_text = [lemmatizer.lemmatize(word) for word in cleaned_lemmatized_text if word not in set( 
            stopwords.words('english'))] 

    cleaned_lemmatized_text = ' '.join(cleaned_lemmatized_text)

    return cleaned_text, cleaned_lemmatized_text

CHROMA_DATA_PATH = "chroma_data/"
COLLECTION_NAME = "news_articles"

class RSSNLP:
    def __init__(self):
        
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            x = torch.ones(1, device=device)
            print (x)
        else:
            print ("MPS device not found.")

        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        nltk.download('punkt')
        nltk.download('punkt_tab')

        self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        
        self.embedding_func = SonarEmbeddingFunction()
        
        self.lemmatizer = WordNetLemmatizer()

        self.stop_words = set(stopwords.words('english'))
        
        self.rss_feeds = []
        
        self.articles = []
    
    def get_articles(self): 
        for rss_url in tqdm(self.rss_feeds, desc="RSS Feeds"):
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if "summary" in entry:
                    self.articles.append({
                        "title": entry.title,
                        "link": entry.link,
                    })
        
    
    def get_articles_text(self):
        valid_articles = []
        for article in tqdm(self.articles, desc="Extracting article text"):
            article_text = extract_article_text(article["link"])
            if article_text:
                article_text, cleaned_lemmatized_text = clean_text(article_text)
                if len(article_text) > 0 and isinstance(article_text, str):
                    article["text"] = article_text
                    article["lemmatized_text"] = cleaned_lemmatized_text
                    valid_articles.append(article)  
            
        self.articles = valid_articles
        self.df = pd.DataFrame(self.articles)

    def collection_add(self):
        
        self.collection = self.client.get_collection(COLLECTION_NAME, embedding_function=self.embedding_func)

        metadata_cols = self.df.drop(columns=['title']).to_dict(orient='records')

        for i in tqdm(range(len(self.df)), desc="Adding documents"):
            self.collection.add(
                documents=[self.df["title"].iloc[i]],
                metadatas=[metadata_cols[i]],          
                ids=[f"id{i}"]                         
            )
    
    def word_cloud(self): 
        print("generating word cloud")
        
        wd_list = self.df['lemmatized_text']
        
        stopwords = set(STOPWORDS) 
        all_words = ' '.join([text for text in wd_list]) 
        wordcloud = WordCloud(
            background_color='black', 
            stopwords=stopwords, 
            width=1600, height=800, 
            max_words=100, 
            max_font_size=200, 
            colormap="viridis"
        ).generate(all_words) 
        
        plt.figure(figsize=(12, 10)) 
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis('off') 
        
        path = './public/assets/news/wordcloud.png'
        plt.savefig(path, bbox_inches='tight')  # Save the image
        plt.close()  # Close the figure after saving to free memory
        
        return path
        
    def generate_embedding_plot(self):
        
        print("generating embedding plot")
        
        embeddings = np.array(self.collection.get(include=['embeddings'])['embeddings'])
        documents = np.array(self.collection.get(include=['documents'])['documents'])
        
        articles = np.array([meta["text"] for meta in self.collection.get(include=['metadatas'])["metadatas"]])
        links = np.array([meta["link"] for meta in self.collection.get(include=['metadatas'])["metadatas"]])
        polarities = np.array([meta["polarity"] for meta in self.collection.get(include=['metadatas'])["metadatas"]])
        subjectivities = np.array([meta["subjectivity"] for meta in self.collection.get(include=['metadatas'])["metadatas"]])
        sentiments = np.array([meta["sentiment"] for meta in self.collection.get(include=['metadatas'])["metadatas"]])
        
        print("Reducing embeddings...")
        
        print(len(embeddings), len(embeddings[0]))
        print(type(embeddings), type(embeddings[0]))
        
        tsne = TSNE(n_components=2, perplexity=min(30, len(embeddings) - 1))
        reduced_embeddings = tsne.fit_transform(embeddings)
        
        print("Clustering embeddings...")
        
        labels, n_clusters, n_noise = embedClustering.dbscanEMB(reduced_embeddings, eps=0.37, min_samples=2)
        
        tsne_df = pd.DataFrame(reduced_embeddings, columns=['Component 1', 'Component 2'])

        tsne_df['title'] = [title for title in documents]
        tsne_df['link'] = [link for link in links]  # These are the URLs for each point
        tsne_df['polarity'] = [round(polarity, 2) for polarity in polarities]
        tsne_df['subjectivity'] = [round(subjectivity, 2) for subjectivity in subjectivities]
        tsne_df['sentiment'] = [sentiment for sentiment in sentiments]
        tsne_df['cluster'] = labels

        fig = px.scatter(
            tsne_df,
            x='Component 1',
            y='Component 2',
            color='cluster',
            hover_data={
                'title': True,
                'subjectivity': True,
                'polarity': True,
                'sentiment': True,
                'link': False  # Do not show the link in hover text
            },
            custom_data=['link']  # Include 'link' in custom data
        )

        fig.update_traces(marker=dict(size=12))  # Adjust 'size' to your preference

        
        # Define the path where the HTML file will be saved
        path = "./public/assets/news/cluster.html"

        # JavaScript code to handle click events
        post_script = '''
        var myPlot = document.getElementById('myDiv');
        myPlot.on('plotly_click', function(data){
            var point = data.points[0];
            var url = point.customdata[0];  // Access the link from customdata
            window.open(url, '_blank');     // Open the link in a new tab
        });
        '''

        # Save the plot as an HTML file with the JavaScript code included
        fig.write_html(path, div_id='myDiv', post_script=post_script)

        return path
    
    def compute_sentiment(self):
        print("Computing sentiment scores...")
        
        def get_sentiment(text):
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            # Determine sentiment score
            if polarity > 0:
                sentiment_score = "Positive"
            elif polarity == 0:
                sentiment_score = "Neutral"
            else:
                sentiment_score = "Negative"
            
            return pd.Series([polarity, subjectivity, sentiment_score])
        
        self.df[['polarity', 'subjectivity', 'sentiment']] = self.df['lemmatized_text'].apply(get_sentiment)