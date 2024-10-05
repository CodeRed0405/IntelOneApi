# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pymongo import MongoClient


# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['trail_database']

# Index page
def index(request):
    return render(request, 'sign_up.html')

def retrieve(request):
    # Fetch all records from MongoDB
    collection = db['candidate_details']
    records = collection.find()  # This retrieves all the documents in the collection
    # Pass the records to the template
    return render(request, 'show_records.html', {'records': records})

 
def view_the_applicant(request):
    return render(request, 'applicant_profile.html')

def show_all_applicants(request):
    return render(request, 'applicants.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def create_role(request):
    collection = db['job_details']
    return render(request, 'new_role.html')


    

