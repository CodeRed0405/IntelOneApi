import requests
import os
import spacy
from spacy.matcher import PhraseMatcher

from collections import defaultdict
import re

# GitHub username to fetch details for
GITHUB_USERNAME = "JenniferRubina"  # Replace with any GitHub username

# Base URL for GitHub API
API_URL = "https://api.github.com/users/"

# Directory to save the final CSV file
SAVE_DIR = f"{GITHUB_USERNAME}_output"

# Load the spaCy NLP model for English language
nlp = spacy.load("en_core_web_sm")

# Keywords to search for in README files and project files (expanded for better coverage)
KEYWORDS = [
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
    'JUnit', 'Mockito', 'TestNG', 'Postman', 'Katalon Studio', 'JMeter', 'Cypress']

# Common project files to look for tech stack details
TECH_FILES = {
    "package.json": "javascript",
    "requirements.txt": "python",
    "pom.xml": "java",
    "build.gradle": "java",
    "Dockerfile": "docker",
    "setup.py": "python",
    "Gemfile": "ruby",
    "composer.json": "php"
}

# Function to fetch user repositories
def fetch_user_repos(username):
    url = API_URL + username + "/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repos: {response.status_code}")
        return None

# Function to fetch README content from a repository
def fetch_readme(repo_name, branch="main"):
    formats = ["README.md", "README.rst", "README.txt"]  # Try different README formats
    for fmt in formats:
        readme_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/{branch}/{fmt}"
        response = requests.get(readme_url)
        if response.status_code == 200:
            return response.text
    return None

# Function to preprocess text with NLP (tokenization, lemmatization, etc.)
def preprocess_text(text):
    doc = nlp(text.lower())  # Tokenize and process the text
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]  # Lemmatize and remove stop words
    return tokens

# Function to create the PhraseMatcher with the list of keywords
def create_keyword_matcher(nlp, keywords):
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(keyword.lower()) for keyword in keywords]  # Create patterns from keywords
    matcher.add("KeywordMatcher", None, *patterns)
    return matcher

# Function to extract keywords from README using PhraseMatcher
def extract_keywords_nlp(readme_content, keywords):
    matcher = create_keyword_matcher(nlp, keywords)  # Initialize PhraseMatcher with keywords
    found_keywords = defaultdict(int)

    # Apply spaCy NLP pipeline to the README content
    doc = nlp(readme_content.lower())
    
    # Find matches for the keywords
    matches = matcher(doc)
    
    # Increment the count of matched keywords
    for match_id, start, end in matches:
        keyword = doc[start:end].text
        found_keywords[keyword] += 1

    return dict(found_keywords)

# Function to save the extracted keywords into a CSV file (no project names, just keywords)
def save_keywords_to_csv(all_found_keywords):
    # Ensure the save directory exists
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Path to the final CSV file
    csv_file = os.path.join(SAVE_DIR, f"{GITHUB_USERNAME}_tech_stack_keywords.csv")

    # Write all keywords and their counts to the CSV file
    with open(csv_file, 'w', encoding='utf-8') as csvfile:
        csvfile.write("keyword,count\n")
        for keyword, count in all_found_keywords.items():
            csvfile.write(f"{keyword},{count}\n")

    print(f"Saved tech stack keywords to {csv_file}")

# Function to detect the default branch dynamically
def fetch_default_branch(repo_name):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('default_branch', 'main')
    return 'main'

# Function to fetch the list of files in the repository
def fetch_repo_files(repo_name, branch="main"):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/git/trees/{branch}?recursive=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('tree', [])
    return []

# Function to detect tech stack based on project files
def detect_tech_stack(files):
    tech_stack = set()
    for file_info in files:
        file_name = file_info['path'].lower()
        for tech_file, tech in TECH_FILES.items():
            if tech_file in file_name:
                tech_stack.add(tech)
    return tech_stack

# Main function to run the extraction process
def main():
    repos_data = fetch_user_repos(GITHUB_USERNAME)

    # Dictionary to store all found keywords and their counts
    all_found_keywords = defaultdict(int)

    if repos_data:
        print(f"\nTotal Repositories: {len(repos_data)}")

        for repo in repos_data:
            repo_name = repo['name']
            print(f"Fetching details for repository: {repo_name}...")

            default_branch = fetch_default_branch(repo_name)

            # Fetch README content
            readme_content = fetch_readme(repo_name, default_branch)

            if readme_content:
                # NLP-based keyword extraction
                found_keywords = extract_keywords_nlp(readme_content, KEYWORDS)

                # Merge the found keywords with the global dictionary
                for keyword, count in found_keywords.items():
                    all_found_keywords[keyword] += count

            # Fetch repository files
            repo_files = fetch_repo_files(repo_name, default_branch)

            if repo_files:
                tech_stack = detect_tech_stack(repo_files)
                if tech_stack:
                    print(f"Detected tech stack for {repo_name}: {tech_stack}")
                    # Update keyword counts based on detected tech stack
                    for tech in tech_stack:
                        all_found_keywords[tech] += 1
            else:
                print(f"No files found for {repo_name}.")

    # Save all the found keywords and counts to a single CSV file
    save_keywords_to_csv(all_found_keywords)

if __name__ == "__main__":
    main()