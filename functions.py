import os
import random
import codecs
import json
import pandas as pd
import numpy
import datetime


#Add the category (name of the file) to each JSON object in the file
def prepare_json():
    if not os.path.exists("data_modified"):
        os.makedirs("data_modified")

    for i in os.listdir(os.getcwd()+"/data"):
        if i.endswith(".json"):
            current_doc = pd.read_json("data/"+i)
            current_doc.loc["from"] = i
            current_doc.to_json("data_modified/transformed" + i)


#Merge all the movies from all the JSON into a unique JSON
def merge_json():
    #Choose a random file to start the concatenation of all the movies
    random_file = random.choice(os.listdir(os.getcwd()+"/data_modified"))
    with codecs.open("data_modified/"+random_file, encoding='utf-8') as fi:
        all_movies = json.load(fi)
    #Iter on all the file to concatenate them
    for file_name in os.listdir(os.getcwd()+"/data_modified"):
        if file_name != random_file:
            with codecs.open("data_modified/"+file_name, encoding='utf-8') as fi:
                all_movies.update(json.load(fi))
    #Print all the movies in a json
    if not os.path.exists("movies"):
        os.makedirs("movies")
    with open("movies/movies.json", "w") as fi:
        json.dump(all_movies, fi)


#This function will create all the clusters. It takes in parameter the number
#of cluster you want and epsilon (Stop condition).
#Once epsilon reached that mean the cluster as ended their convergence
#Parameters:
#k: integer the number of cluster u want
#epsilon: float stop condition, must be > 0
def k_means(k, epsilon):
    list_movies = list_of_movies()
    min_max = get_min_max(list_movies)
    centroids = generate_centroid(k, min_max)
    centroids_difference = (5,) * k
    while centroids_difference > (epsilon,)*k:
        for movie in list_movies:
            movie['centroid'] = get_nearest_centroid(centroids, movie)
        new_centroids = define_new_centroids(centroids, list_movies)
        centroids_difference = tuple(numpy.fabs(numpy.subtract(new_centroids, centroids)))
        centroids = new_centroids
    for movie in list_movies:
        movie['centroid'] = get_nearest_centroid(centroids, movie)
    clusters = ()
    for centroid in centroids:
        cluster = tuple(filter(lambda x: x['centroid'] == centroid, list_movies))
        clusters = clusters + (cluster,)
    return clusters


#This function will return a list of JSON object, each object is a movie
#There will be all the movie included in the dataset in that list
def list_of_movies():
    list_movies = []
    with open("movies/movies.json", "r") as fi:
        movies = json.load(fi)
    for movie in movies:
        list_movies.append(movies[movie])
    return filter(lambda x: x['user_rating'] != None, list_movies)


#This function return the minimum and maximum user_rating
#Parameters:
#movies: List of JSON object
def get_min_max(movies):
    min_user_rating = 5
    max_user_rating = 0
    for movie in movies:
        if movie['user_rating'] < min_user_rating:
            min_user_rating = movie['user_rating']
        if movie['user_rating'] > max_user_rating:
            max_user_rating = movie['user_rating']
    return (min_user_rating, max_user_rating)


#This function generate k centroids between the max and the min user_rating
#Parameters:
#k: integer (number of cluster you want)
#min_max: pair of float
def generate_centroid(k, min_max):
    centroids = ()
    for centroid in range(0, k):
        centroids = centroids + (random.uniform(min_max[0], min_max[1]),)
    return tuple(sorted(centroids))


#This function take in parameter the centroids and an element and return the
#value of the nearest centroid
#Parameters:
#centroids: tuples of float
#elem: JSON object
def get_nearest_centroid(centroids, elem):
    minimum_distance = 5
    nearest_centroid = 0
    for centroid in centroids:
        if abs(elem['user_rating'] - centroid) < minimum_distance:
            nearest_centroid = centroid
            minimum_distance = abs(elem['user_rating'] - centroid)
    return nearest_centroid


#This function determine the barycenter of all the points which belongs to
#a specific centroid. This barycenterwill be the new centroid
#Parameters:
#Centroids: tuple of float
#Movies: list of JSON object
def define_new_centroids(centroids, movies):
    new_centroids = ()
    for centroid in centroids:
        new_centroid = 0
        movies_by_centroid = filter(lambda x: x['centroid'] == centroid, movies)
        for movie in movies_by_centroid:
            new_centroid = new_centroid + movie['user_rating']
        new_centroids = new_centroids + (new_centroid/len(movies_by_centroid),)
    return tuple(sorted(new_centroids))


#This function will create the folder "clusters" which will include the result
#of the clusterisation, each file will correspond to a cluster
#Parameters:
#clusters: Tuple of list of JSON object
def save_clusters(clusters):
    if not os.path.exists("clusters"):
        os.makedirs("clusters")
    for index, cluster in enumerate(clusters):
        with codecs.open("clusters/cluster"+str(index + 1) + "-" + str(datetime.datetime.now().time()) + ".txt", "w", encoding='utf-8') as fi:
            fi.write("Cluster ayant pour centroid: " + str(cluster[0]['centroid']) + '\n\n')
            for movie in cluster:
                fi.write(movie['title_french'] + " " + str(movie['user_rating']) + '\n')
    print "Clusters saved"
