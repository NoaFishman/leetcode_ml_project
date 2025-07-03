# 🔍 Leetcode Machine Learning Analysis

This project applies various **machine learning and deep learning models** to analyze and predict attributes of Leetcode coding problems. It explores data-driven insights into question difficulty, user interaction metrics, and interview relevance using a real dataset scraped from Leetcode.

## 📁 Dataset

- **Source**: [Kaggle – Leetcode Problem Dataset](https://www.kaggle.com/datasets/gzipchrist/leetcode-problem-dataset/data)
- **Size**: 1,825 questions × 17 features
- **Features Include**:
  - Problem description and title
  - Difficulty (Easy, Medium, Hard)
  - Submission statistics (likes, dislikes, acceptance rate)
  - Associated companies and tags
  - Premium access status

## 🎯 Project Goals

1. Explore the structure and patterns in Leetcode problems
2. Visualize problem attributes across difficulty levels and companies
3. Build predictive models to answer:
   - Can we predict the number of likes/dislikes?
   - Can we estimate the number of accepted submissions?
   - Can we classify problem difficulty based on metadata and text?
   - Can we predict the related topics of a problem?

## 🧪 ML Tasks & Models

| Task                                 | Type             | Models Used |
|--------------------------------------|------------------|-------------|
| Predict accepted submissions         | Regression       | Linear Regression |
| Predict likes/dislikes               | Regression       | Linear Regression, Random Forest, Gradient Boosting, XGBoost |
| Classify problem difficulty          | Classification | Logistic Regression, Random Forest, SVM, KNN, Gradient Boosting, XGBoost, Neural Network |
| Predict related topics               | Multi-label Classification | Logistic Regression, Random Forest, SVM, KNN, XGBoost with OvR |

> Best-performing models: **XGBoost** for difficulty classification, **Random Forest** for multi-label topic prediction.

## 📊 Visualizations

- 📈 Difficulty distribution & acceptance rate trends
- 🧠 Word frequency across problem levels
- 🏢 Company preferences by topic and difficulty
- 🔥 Topic difficulty patterns (e.g., Graph & DP skew harder)

## ⚙️ Preprocessing

- Multi-hot encoding for multi-label features
- Label encoding for categorical fields
- Lemmatization and keyword normalization on descriptions
- TF-IDF extraction (top 100 terms) from problem text
- Threshold optimization for multi-label classification

## 📌 Challenges

- Balancing the dataset reduced model performance (due to loss of information)
- Neural networks underperformed due to limited data and feature complexity
- Title prediction using LSTM failed due to poor text embeddings and insufficient signal

## 🚀 Future Work

- Use pre-trained transformers (e.g., BERT) for feature extraction
- Apply NLP-specific data augmentation
- Collect more examples for underrepresented tags or difficulty levels
- Explore explainable AI methods to interpret predictions

## 🧠 Authors

- Noa Fishman
- Rachel Belokopytov  


