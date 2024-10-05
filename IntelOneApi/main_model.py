import torch
from sentence_transformers import SentenceTransformer, util
from pdfminer.high_level import extract_text
import re

# Load both models
gtr_model = SentenceTransformer('sentence-transformers/gtr-t5-large')
mpnet_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Function to extract text from a PDF resume
def extract_text_from_pdf(pdf_file_path):
    try:
        text = extract_text(pdf_file_path)
        return text
    except Exception as e:
        print(f"Error reading the PDF file: {e}")
        return ""

# Function to clean and check resume content
def is_valid_resume_text(resume_text, min_words=50):
    resume_text = re.sub(r'\s+', ' ', resume_text)
    words = resume_text.split()
    return len(words) >= min_words

# Function to calculate similarity between resume and job description using both models
def calculate_combined_similarity(resume_text, job_description, weight_gtr=0.6, weight_mpnet=0.4):
    # Preprocess and clean the job description text
    job_description = re.sub(r'\s+', ' ', job_description)

    # Generate embeddings using both models
    resume_embedding_gtr = gtr_model.encode(resume_text, convert_to_tensor=True)
    job_desc_embedding_gtr = gtr_model.encode(job_description, convert_to_tensor=True)

    resume_embedding_mpnet = mpnet_model.encode(resume_text, convert_to_tensor=True)
    job_desc_embedding_mpnet = mpnet_model.encode(job_description, convert_to_tensor=True)

    # Calculate cosine similarity for both models
    cosine_sim_gtr = util.pytorch_cos_sim(resume_embedding_gtr, job_desc_embedding_gtr)
    cosine_sim_mpnet = util.pytorch_cos_sim(resume_embedding_mpnet, job_desc_embedding_mpnet)

    # Combine the cosine similarities using a weighted average
    combined_similarity = (weight_gtr * cosine_sim_gtr.item()) + (weight_mpnet * cosine_sim_mpnet.item())

    # Cosine similarity returns a value between -1 and 1. Multiply by 100 for percentage
    similarity_score = combined_similarity * 100

    # Clear the GPU VRAM after processing
    if torch.cuda.is_available():
        torch.cuda.empty_cache()  # Clear unused memory

    return similarity_score

# Function to process resume and job description
def process_resume(resume_file_path, job_description):
    # Extract resume text
    resume_text = extract_text_from_pdf(resume_file_path)
    if not is_valid_resume_text(resume_text):
        print("Invalid or empty resume.")
        return

    # Calculate similarity
    similarity_score = calculate_combined_similarity(resume_text, job_description)
    print(f"Resume to Job Description Similarity: {similarity_score}%")

    # Optionally clear VRAM after each step for better optimization
    if torch.cuda.is_available():
        torch.cuda.empty_cache()  # Clear VRAM

# Example job description and file path
resume_file_path = r'C:\Users\rmjay\OneDrive\Desktop\intel\Tejasram_ats_resume_new.pdf'  # Replace with the actual resume file path
job_description = '''
Selected intern's day-to-day responsibilities include:1. NLP: Work on vector space modeling in NLP, LSTMS, sequence modeling, attention modeling, BERT, transformers2. Use the above-mentioned techniques to perform document classification, semantic similarity, NER, sentiment analysis3. Perform time series analysis using ARIMA, SARIMA, LSTMs, etc4. Work on feature engineering, feature selection/feature importance, dimensionality

Skill(s) required

Data ScienceMachine LearningNatural Language Processing (NLP)Python

Earn certifications in these skills

Learn Python
Learn Voice App Development
Learn Machine Learning
Learn Data Science

Who can apply

Only those candidates can apply who:

1. are available for the work from home job/internship

2. can start the work from home job/internship between 18th Dec'23 and 22nd Jan'24

3. are available for duration of 3 months

4. have relevant skills and interests

- Women wanting to start/restart their career can also apply.

Added requirements

1. Hands-on with Python/R programming and knowledge of machine learning tools like Scikit-Learn, Pandas, TensorFlow

2. Knowledge of statistical modeling and popular machine learning models
'''

process_resume(resume_file_path, job_description)
