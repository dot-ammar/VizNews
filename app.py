from flask import Flask, request, jsonify
import chromadb
from SonarEmbeddingFunction import SonarEmbeddingFunction
from rss_nlp import RSSNLP
from flask_cors import CORS
import json

print("Starting the Flask server...")

print("Initializing the SonarEmbeddingFunction...")
embedding_func = SonarEmbeddingFunction()

print("Creating the ChromaDB collection...")
CHROMA_DATA_PATH = "chroma_data/"
COLLECTION_NAME = "news_articles"

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)


print("Initializing the RSSNLP...")
rss_nlp = RSSNLP()


app = Flask(__name__)
CORS(app)


@app.route("/process", methods=["POST"])
def process_data():
    data = request.json  # Get JSON data from the POST request
    # Perform your data processing here
    print(data)
    result = data_processing_function(data)
    return jsonify(result)  # Send JSON response back


def data_processing_function(data):

    try:
        client.delete_collection(COLLECTION_NAME)
        "ChromaDB collection deleted."
    except:
        print("ChromaDB collection does not exist.")

    client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_func)

    rss_nlp.rss_feeds = data["rssFeeds"]

    rss_nlp.get_articles()

    rss_nlp.get_articles_text()

    rss_nlp.compute_sentiment()

    rss_nlp.collection_add()

    worldcloudpath = rss_nlp.word_cloud()

    clusterpath = rss_nlp.generate_embedding_plot()

    numArticles = len(rss_nlp.articles)
    numSources = len(data["rssFeeds"])
    selected_columns = rss_nlp.df[
        ["title", "link", "polarity", "subjectivity", "sentiment"]
    ]

    average_polarity = rss_nlp.df["polarity"].mean()
    average_subjectivity = rss_nlp.df["subjectivity"].mean()

    data_dict = selected_columns.to_dict(orient="records")

    returnData = {
        "wordcloudpath": worldcloudpath,
        "clusterpath": clusterpath,
        "numSources": numSources,
        "numArticles": numArticles,
        "average_polarity": average_polarity,
        "average_subjectivity": average_subjectivity,
        "articles": data_dict
    }

    with open("output/data_output.json", "w") as json_file:
        json.dump(returnData, json_file, indent=4)

    return returnData


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
