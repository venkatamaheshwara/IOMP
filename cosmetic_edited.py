import base64
import streamlit as st #open source web-framework for front end 
import pandas as pd #package built top of numpy used for data analysis ,for manipulating tabular data 
import numpy as np #package for used for  of math operation on arrays(oprerations indexing,sorting)
from sklearn.manifold import TSNE #libraray which provides tools for ml and statistical mpodelling such as classification,regression,clustering etc..
from scipy.spatial.distance import cdist #scientific python it provides utility fucntions for optimization ()

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background:linear-gradient(rgba(0,0,0,.5),rgba(237,174,192,0.9)),url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}

    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('bg-3.jpg')

 #to insert content
st.markdown('<style>h1{color: rgb(255,255,255);font-size:5rem}</style>', unsafe_allow_html=True)
st.title(' Find the Right Skin Care for you')

st.markdown('<style>p{color: #E7F2F8;font-size:2rem;font-family:times new roman}</style>', unsafe_allow_html=True)
st.write("Hi there! If you have a skincare product you currently like We can help you to find a similar one based on the ingredients.")

st.write('Please select a product below so to recommend similar ones ')
#st.write('My dataset contains 1400+ products :star2: but unfortunately it is possible that I do not have the product you are looking for :disappointed:')
# Load the data
df = pd.read_csv(".
/cosmetic_dataset.csv")

# Choose a product category
st.markdown('<style>.css-k3w14i{color: #3B0404;font-size:1.5rem;font-weight:bold}</style>', unsafe_allow_html=True)
st.markdown('<style>.row-widget{margin-top:2rem}</style>', unsafe_allow_html=True)

category = st.selectbox(label='Select a product category', options= df['Label'].unique() )
category_subset = df[df['Label'] == category]
# Choose a brand
brand = st.selectbox(label='Select a brand', options= sorted(category_subset['Brand'].unique()))
category_brand_subset = category_subset[category_subset['Brand'] == brand]
# Choose product
product = st.selectbox(label='Select the product', options= sorted(category_brand_subset['Name'].unique() ))

#skin_type = st.selectbox(label='Select your skin type', options= ['Combination',
#       'Dry', 'Normal', 'Oily', 'Sensitive'] )

## Helper functions
# Define the oh_encoder function
def oh_encoder(tokens):
    x = np.zeros(N)
    for ingredient in tokens:
        # Get the index for each ingredient
        idx = ingredient_idx[ingredient]
        # Put 1 at the corresponding indices
        x[idx] = 1
    return x

def closest_point(point, points):
    """ Find closest point from a list of points. """
    return points[cdist([point], points).argmin()]


if category is not None:
    category_subset = df[df['Label'] == category]

if product is not None:
    #skincare_type = category_subset[category_subset[str(skin_type)] == 1]

    # Reset index
    category_subset = category_subset.reset_index(drop=True)

    # Display data frame
    #st.dataframe(category_subset)

    # Initialize dictionary, list, and initial index
    ingredient_idx = {}
    corpus = []
    idx = 0

    # For loop for tokenization
    for i in range(len(category_subset)):    
        ingredients = category_subset['Ingredients'][i]
        ingredients_lower = ingredients.lower()
        tokens = ingredients_lower.split(', ')
        corpus.append(tokens)
        for ingredient in tokens:
            if ingredient not in ingredient_idx:
                ingredient_idx[ingredient] = idx
                idx += 1

                
    # Get the number of items and tokens 
    M = len(category_subset)
    N = len(ingredient_idx)

    # Initialize a matrix of zeros
    A = np.zeros((M,N))

    # Make a document-term matrix
    i = 0
    for tokens in corpus:
        A[i, :] = oh_encoder(tokens)
        i +=1
st.markdown('<style>.css-5uatcg{margin-top:2rem;margin-left:15rem;border-radius:50px;}</style>', unsafe_allow_html=True)

model_run = st.button('Find similar products!')


if model_run:

    st.write('Based on the ingredients of the product you selected')
    st.write('here are the top 10 products that are the most similar :sparkles:')
    
    # Run the model
    model = TSNE(n_components = 2, learning_rate = 150, random_state = 42)
    tsne_features = model.fit_transform(A)

    # Make X, Y columns 
    category_subset['X'] = tsne_features[:, 0]
    category_subset['Y'] = tsne_features[:, 1]

    target = category_subset[category_subset['Name'] == product]

    target_x = target['X'].values[0]
    target_y = target['Y'].values[0]

    df1 = pd.DataFrame()
    df1['point'] = [(x, y) for x,y in zip(category_subset['X'], category_subset['Y'])]

    category_subset['distance'] = [cdist(np.array([[target_x,target_y]]), np.array([product]), metric='euclidean') for product in df1['point']]

    # arrange by descending order
    top_matches = category_subset.sort_values(by=['distance'])

    # Compute ingredients in common
    target_ingredients = target.Ingredients.values
    c1_list = target_ingredients[0].split(",")
    c1_list = [x.strip(' ') for x in c1_list]
    c1_set = set(c1_list)

    top_matches['Ingredients in common'] = [c1_set.intersection( set([x.strip(' ')for x in product.split(",")]) ) for product in top_matches['Ingredients']]

    # Select relevant columns
    top_matches = top_matches[['Label', 'Brand', 'Name', 'Price', 'Ingredients','Ingredients in common']]
    top_matches = top_matches.reset_index(drop=True)
    top_matches = top_matches.drop(top_matches.index[0])

    st.dataframe(top_matches.head(10))