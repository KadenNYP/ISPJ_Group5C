# ML_Model.py
import os
import re
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

def load_data(data_folder):
    documents = []
    labels = []
    for category in os.listdir(data_folder):
        category_path = os.path.join(data_folder, category)
        if os.path.isdir(category_path):
            for filename in os.listdir(category_path):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(category_path, filename)
                    text = extract_text_from_pdf(file_path)
                    if text:
                        cleaned_text = clean_text(text)
                        documents.append(cleaned_text)
                        labels.append(category)
    return documents, labels

def train_model(data_folder, model_path='document_classification_model.joblib'):
    try:
        documents, labels = load_data(data_folder)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Loaded {len(documents)} documents from {data_folder}")
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents)

    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

    model = LogisticRegression(solver='liblinear', multi_class='auto')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")

    joblib.dump((vectorizer, model), model_path)
    print(f"Model saved to {model_path}")

def predict_document_class(pdf_path, model_path='document_classification_model.joblib'):
    try:
        vectorizer, model = joblib.load(model_path)
    except FileNotFoundError:
        return "Model file not found. Please train the model first."
    except Exception as e:
        return f"Error loading the model: {e}"

    text = extract_text_from_pdf(pdf_path)
    if not text:
        return "Could not extract text from PDF."

    cleaned_text = clean_text(text)
    X = vectorizer.transform([cleaned_text])
    prediction = model.predict(X)[0]
    return prediction

if __name__ == '__main__':
    # Example usage:
    data_folder = 'training_data'  # Replace with the path to your training data folder
    model_path = 'document_classification_model.joblib'

    # Train the model (only needs to be done once or when training data changes)
    train_model(data_folder, model_path)

    # Example prediction
    pdf_file_path = 'test_document.pdf'  # Replace with the path to your PDF file
    predicted_class = predict_document_class(pdf_file_path, model_path)
    print(f"Predicted class for {pdf_file_path}: {predicted_class}")