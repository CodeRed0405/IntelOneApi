# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pymongo import MongoClient
from django.core.files.storage import default_storage
import os

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['trail_database']
collection = db['candidate_details']

# Index page
def index(request):
    return HttpResponse('root aka index page of the candidate home page')

# Submit form view
def submit_form(request):
    if request.method == 'POST':
        # Collect form data
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        job_title = request.POST.get('jobTitle')
        job_description = request.POST.get('jobDescription')
        github_url = request.POST.get('github')
        linkedin_url = request.POST.get('linkedin')

        # Handle resume file upload
        resume = request.FILES.get('resume')
        if resume:
            resume_name = default_storage.save(resume.name, resume)
            resume_path = os.path.join('media', resume_name)

        # Store the collected data in MongoDB
        candidate_data = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'job_title': job_title,
            'job_description': job_description,
            'resume': resume_path,  # File path to the resume
            'github_url': github_url,
            'linkedin_url': linkedin_url,
            'score':0
        }

        # Insert data into MongoDB
        collection.insert_one(candidate_data)

        # Redirect to the success page after form submission
        return redirect('success_page')  # This uses the URL name defined in urls.py

    # Render the form page if it's not a POST request
    return render(request, 'application_page.html')

# Success page view
def success_page(request):
    return render(request, 'cand_success.html')

