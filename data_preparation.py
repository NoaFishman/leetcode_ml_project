import pandas as pd
import json
import joblib
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import spacy
import matplotlib.pyplot as plt


def balance_graph_distrution(difficulty_counts, name):

    color_map = {
        'Easy': '#A6CDC6',
        'Medium': '#3B6790',
        'Hard': '#DDA853'
    }

    labels = difficulty_counts.index
    colors = [color_map[label] for label in labels]

    # Create pie chart with custom colors
    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        difficulty_counts,
        labels=None,  # Leave labels off the pie slices
        autopct='%1.1f%%',
        startangle=140,
        colors=colors
    )
    plt.legend(
        wedges,
        [f"{label} ({difficulty_counts[label]})" for label in labels],
        title="Difficulty Level",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )
    plt.title('Distribution of Problems by Difficulty Level')
    plt.axis('equal')  # Makes the pie chart a circle
    plt.tight_layout() 
    # plt.show()
    plt.savefig(f"{name}.jpg")


def data_balancing(df):
   
    difficulty_counts = df['difficulty'].value_counts()
    print("Original class distribution:\n", difficulty_counts)
    balance_graph_distrution(difficulty_counts, "plots/original_difficulty_distribution")

    # Step 1: Find the minimum count among the classes
    min_count = difficulty_counts.min()

    # Step 2: Undersample each class to have `min_count` examples
    df_balanced = (
        df.groupby('difficulty', group_keys=False)
        .apply(lambda x: x.sample(min_count, random_state=42).copy())
        .reset_index(drop=True)
    )
    
    # Step 3: Check new distribution
    balanced_difficulty_counts = df_balanced['difficulty'].value_counts()
    print("Balanced class distribution:\n", balanced_difficulty_counts)
    balance_graph_distrution(balanced_difficulty_counts, "plots/balanced_difficulty_distribution")
    
    # Step 4: Save the balanced DataFrame to a CSV file
    df_balanced.to_csv('data_files/balanced_data.csv', index=False)

    return df_balanced


def data_preparation(df):
    # Apply Multi-Hot Encoding to the 'companies' column
    df['companies'] = df['companies'].fillna('')
    df['companies'] = df['companies'].str.split(',')
    mlb = MultiLabelBinarizer()
    companies_encoded = mlb.fit_transform(df['companies'])
    companies_df = pd.DataFrame(companies_encoded, columns=mlb.classes_)
    df = pd.concat([df, companies_df], axis=1)
    df = df.drop(columns=['companies'])

    # Apply Multi-Hot Encoding to the 'related_topics' column
    df['related_topics'] = df['related_topics'].fillna('')
    df['related_topics'] = df['related_topics'].str.split(',')
    mlb = MultiLabelBinarizer()
    related_topics_encoded = mlb.fit_transform(df['related_topics'])
    related_topics_df = pd.DataFrame(related_topics_encoded, columns=mlb.classes_)
    df = pd.concat([df, related_topics_df], axis=1)
    df = df.drop(columns=['related_topics'])

    companies_columns = list(companies_df.columns)
    related_topics_columns = list(related_topics_df.columns)

    # Save column names to JSON
    encoding_metadata = {
        "companies_columns": companies_columns,
        "related_topics_columns": related_topics_columns
    }
    with open("data_files/encoding_metadata.json", "w") as f:
        json.dump(encoding_metadata, f)

    # Function to convert to float
    def convert_to_float(value):
        if 'K' in value:
            return float(value.replace('K', '')) * 1_000
        elif 'M' in value:
            return float(value.replace('M', '')) * 1_000_000
        return float(value)  # If it's already a number

    # Apply function convert from K and M to float
    df['submissions'] = df['submissions'].apply(convert_to_float)
    df['accepted'] = df['accepted'].apply(convert_to_float)

    # Label encode 'difficulty_encoder'
    difficulty_encoder = LabelEncoder()
    df['difficulty'] = difficulty_encoder.fit_transform(df['difficulty'])
    joblib.dump(difficulty_encoder, "models/difficulty_encoder.pkl")

    # Label encode 'title'
    title_encoder = LabelEncoder()
    df['title'] = title_encoder.fit_transform(df['title'])
    joblib.dump(title_encoder, "models/title_encoder.pkl")

    nlp = spacy.load("en_core_web_sm")

    # Ensure 'description' and 'difficulty' columns exist
    if "description" not in df.columns:
        raise ValueError("The CSV file must contain 'description' column.")

    # Extract descriptions and difficulties
    descriptions = df["description"]

    # Function for manual word mapping after lemmatization
    def apply_word_mapping(text):
        words = text.split()
        mapped_words = [word_mapping.get(word, word) for word in words]  # Replace with mapped word if exists
        return " ".join(mapped_words)

    # Function for lemmatizing words in the description text
    def lemmatize_text(text):
        doc = nlp(text)
        lemmatized_words = [token.lemma_ for token in doc]
        return " ".join(lemmatized_words)

    # Define manual word mapping (add more as needed)
    word_mapping = {
        "arr": "array",
        "nums": "num",
        "num": "number",
        "str": "string",
        "bool": "boolean",
        "int": "integer",
        "node": "node",
        "val": "value"
    }

    # Apply lemmatization first
    lemmatized_descriptions = descriptions.apply(lemmatize_text)

    # Apply the manual word mapping after lemmatization
    mapped_lemmatized_descriptions = lemmatized_descriptions.apply(apply_word_mapping)

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        stop_words="english",  # Removes common English words
        max_features=100,  # Select top 50 words
        min_df=2,  # Ignore words appearing in <2 documents
        max_df=0.8,  # Ignore words appearing in >80% of documents
    )

    # Fit and transform the TF-IDF Vectorizer on the processed descriptions
    tfidf_matrix = vectorizer.fit_transform(mapped_lemmatized_descriptions)

    description_vectors = tfidf_matrix.toarray()  # Convert the TF-IDF matrix to an array of numerical vectors
    top_words = vectorizer.get_feature_names_out()  # Get the top words from TF-IDF (which will be the column names)
    # to avoid duplicates
    # top_words = np.delete(top_words, np.where(top_words == "nums"))
    # top_words = np.delete(top_words, np.where(top_words == "arr"))
    # Update encoding_metadata with top words
    encoding_metadata["top_words"] = top_words.tolist()

    # Save the updated metadata to the JSON file
    with open("data_files/encoding_metadata.json", "w") as f:
        json.dump(encoding_metadata, f)

    description_df = pd.DataFrame(description_vectors, columns=top_words)  # Create a DataFrame with the same number of rows as your original data and columns corresponding to the words

    df = pd.concat([df, description_df], axis=1)  # Concatenate the new description columns with the rest of the DataFrame
    df = df.drop(columns=['description'])  # Drop the old 'description' column if no longer needed

    # Save the DataFrame with the new column
    df.to_csv('data_files/data_with_numerical_encodings.csv', index=False)
    joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")

    # Show the first few rows to verify
    print(df.head())

    # # Get the TF-IDF vector for the first description
    # first_description_vector = description_vectors[1]  # Get first row (first question)
    #
    # # Get the words corresponding to the columns
    # top_words = vectorizer.get_feature_names_out()  # List of words in TF-IDF
    #
    # # Print only non-zero values with their words
    # print("Non-zero TF-IDF values for the first question:\n")
    # for word, value in zip(top_words, first_description_vector):
    #     if value > 0:
    #         print(f"{word}: {value:.4f}")

    return df


url = 'https://raw.githubusercontent.com/NoaFishman/leetcode_ml_project/refs/heads/main/data_files/data.csv'
df = pd.read_csv(url)
df = data_balancing(df)
df = data_preparation(df)