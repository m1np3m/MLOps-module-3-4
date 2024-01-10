import json

def genres_and_keywords_to_string(row):
    genres = json.loads(row["genres"])
    genres = " ".join("".join(j["name"].split()) for j in genres)

    keywords = json.loads(row["keywords"])
    keywords = " ".join("".join(j["name"].split()) for j in keywords)
    return "%s %s" % (genres, keywords)