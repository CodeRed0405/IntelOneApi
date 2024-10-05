import re
import os
import csv
from pdfminer.high_level import extract_text
import spacy

# Load the SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Predefined list of possible skills for matching (all in lowercase for consistency)
skills_set = [skill.lower() for skill in [
    'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Swift', 'Kotlin', 'PHP',
    'R', 'TypeScript', 'Go', 'Rust', 'Perl', 'SQL', 'HTML', 'CSS', 'Bash/Shell scripting',
    'Frontend Development', 'Backend Development', 'Full Stack Development', 'React.js',
    'Angular.js', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Express.js', 'ASP.NET',
    'Ruby on Rails', 'HTML5', 'CSS3', 'jQuery', 'Bootstrap', 'RESTful APIs', 'GraphQL',
    'Android Development', 'iOS Development', 'Flutter', 'React Native', 'SwiftUI',
    'Kotlin Multiplatform', 'Xamarin', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite',
    'NoSQL', 'Oracle DB', 'Microsoft SQL Server', 'Firebase Firestore', 'Redis',
    'AWS', 'Google Cloud Platform', 'Microsoft Azure', 'Heroku', 'IBM Cloud',
    'Cloud Foundry', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI/CD', 'Travis CI',
    'CircleCI', 'Ansible', 'Terraform', 'Puppet', 'Chef', 'Git',
    'Continuous Integration (CI)', 'Continuous Deployment (CD)', 'Data Analysis',
    'Machine Learning', 'Deep Learning', 'Natural Language Processing (NLP)',
    'Computer Vision', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
    'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Apache Spark', 'Hadoop',
    'Jupyter Notebooks', 'Data Visualization', 'Big Data', 'Information Security',
    'Network Security', 'Ethical Hacking', 'Penetration Testing', 'Vulnerability Assessment',
    'OWASP', 'Kali Linux', 'Wireshark', 'Nmap', 'Firewalls', 'IDS/IPS Systems',
    'Encryption', 'SSL/TLS', 'VPN', 'Artificial Intelligence (AI)', 'Robotics',
    'ROS (Robot Operating System)', 'GitHub', 'GitLab', 'Bitbucket',
    'SVN (Subversion)', 'Jira', 'Trello', 'Confluence', 'Slack', 'Microsoft Teams',
    'Asana', 'Agile Methodology', 'Scrum', 'Linux', 'Windows', 'macOS',
    'Ubuntu', 'Red Hat', 'CentOS', 'Unix', 'Automated Testing', 'Selenium',
    'JUnit', 'Mockito', 'TestNG', 'Postman', 'Katalon Studio', 'JMeter', 'Cypress']]

# Function to extract text from a PDF resume
def extract_text_from_pdf(pdf_file_path):
    try:
        text = extract_text(pdf_file_path)
        return text
    except Exception as e:
        print(f"Error reading the PDF file: {e}")
        return ""

# Function to extract skills from the resume text using NLP
def extract_resume_skills(resume_text):
    resume_text = resume_text.lower()  # Convert the text to lowercase for matching
    doc = nlp(resume_text)
    extracted_skills = set()

    # Check for skills in the predefined skills set
    for skill in skills_set:
        if re.search(r'\b' + re.escape(skill) + r'\b', resume_text):
            extracted_skills.add(skill)

    # Use SpaCy to find entities that may indicate skills (based on dependencies)
    for token in doc:
        if token.dep_ == "nsubj" and token.lemma_.lower() in skills_set:
            extracted_skills.add(token.lemma_.lower())

    return extracted_skills

# Function to read GitHub skills from the CSV file
def read_github_skills_from_csv(csv_file_path):
    github_skills = []
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Remove all numbers from each skill in the row
                cleaned_row = [re.sub(r'\d+', '', skill).strip() for skill in row]
                github_skills.extend(cleaned_row)  # Add the cleaned skills to the list
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
    return github_skills

# Function to score each candidate based on the evaluation matrix
def score_candidate(resume_skills, github_skills):
    # Convert both resume and GitHub skills to lowercase for case-insensitive comparison
    resume_skills_lower = {skill.lower() for skill in resume_skills}
    github_skills_set = {skill.lower() for skill in github_skills}

    # Find resume skills that are present in the GitHub skills
    verified_skills = {skill for skill in resume_skills_lower if skill in github_skills_set}

    total_resume_skills = len(resume_skills_lower)

    if total_resume_skills == 0:
        return 0.0, verified_skills  # Avoid division by zero

    # Score based on the percentage of resume skills found in GitHub skills
    verification_score = (len(verified_skills) / total_resume_skills) * 100
    return verification_score, verified_skills


# Function to decide if the candidate is qualified
def is_candidate_qualified(total_score, threshold=50):
    return total_score >= threshold

# Main execution to run the above functions
def main(resume_file_path, github_csv_path, job_role):
    # Extract resume text and skills
    resume_text = extract_text_from_pdf(resume_file_path)
    if not resume_text:
        print("No resume text found. Exiting.")
        return

    resume_skills = extract_resume_skills(resume_text)
    print(f"Extracted Resume Skills: {resume_skills}")

    # Extract GitHub skills
    github_skills = read_github_skills_from_csv(github_csv_path)
    if not github_skills:
        print("No GitHub skills found. Exiting.")
        return
    print(f"Extracted GitHub Skills: {github_skills}")

    # Score the candidate based on the evaluation matrix
    total_score, verified_skills = score_candidate(resume_skills, github_skills)
    print(f"Total Score: {total_score:.2f}%")
    print(f"Verified Skills: {verified_skills}")

    # Determine if the candidate is qualified based on job role
    qualified = is_candidate_qualified(total_score)
    if qualified:
        print(f"Candidate is qualified for the {job_role}.")
    else:
        print(f"Candidate is not qualified for the {job_role}.")

# Example Usage
resume_file_path = r'C:\Users\rmjay\OneDrive\Desktop\intel\Tejasram_ats_resume_new.pdf'  # Replace with the actual resume file path
github_csv_path = r'C:\Users\rmjay\OneDrive\Desktop\intel\tejasram2003_output\tejasram2003_tech_stack_keywords.csv'  # Replace with the actual path to the GitHub skills CSV
job_role = 'Software Engineer'

# Run the process
main(resume_file_path, github_csv_path, job_role)
