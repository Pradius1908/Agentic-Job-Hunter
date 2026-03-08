"""#include <stdio.h>"""
from pdfminer.high_level import extract_text
import os 
import re 
import csv

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def clean_text(text):
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r'\r', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_email(text):
    email = re.search(r'\S+@\S+', text)
    return email.group(0) if email else None

def extract_phone_number(text):
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?:[-.\s]?\d{1,4})?'
    match = re.search(phone_regex, text)
    return match.group(0) if match else None

def extract_name(text):
    name = re.search(r'\b[A-Z][a-z]+\b', text)
    return name.group(0) if name else None

def extract_skills(text):
    skills = re.findall(r'\b[A-Z][a-z]+\b', text)
    return skills

def extract_education(text):
    education = re.findall(r'\b[A-Z][a-z]+\b', text)
    return education

def extract_work_experience(text):
    work_experience = re.findall(r'\b[A-Z][a-z]+\b', text)
    return work_experience

def parse():
    file = open("resume_summary.csv", "w")

    sample_text = extract_text_from_pdf("resume.pdf")
    # print(sample_text[:1000])
    cleaned_text = clean_text(sample_text)

    name = extract_name(cleaned_text)
    email = extract_email(cleaned_text)
    phone_number = extract_phone_number(cleaned_text)
    skills = extract_skills(cleaned_text)
    education = extract_education(cleaned_text)
    work_experience = extract_work_experience(cleaned_text)

    writer = csv.writer(file)
    writer.writerow(["Name", "Email", "Phone Number", "Skills", "Education", "Work Experience"])
    writer.writerow([name, email, phone_number, skills, education, work_experience])
    
    file.close()


    """print(cleaned_text+"\n \n \n")
    print(name)
    print(email)
    print(phone_number)
    print(skills)
    print(education)
    print(work_experience)"""
    
parse()