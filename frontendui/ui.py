import streamlit as st
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(layout="wide")

img = Image.open("uimage.jpg").convert("RGBA")
st.markdown('<h6 align="right"> Profile  </h6>', unsafe_allow_html=True)
# Convert image to base64
buffered = BytesIO()
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()


st.markdown("""


""", unsafe_allow_html=True)

st.markdown("""
<style>
.faded-image {
    width: 100%;
    height: auto;
    opacity: 0.5;
    -webkit-mask-image: radial-gradient(circle, black 50%, transparent 100%);
    mask-image: radial-gradient(circle, black 50%, transparent 100%);
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>

            
                
.image-container {{
    position: relative;
    width: 100%;
}}

.faded-image {{
    width: 100%;
    height: auto;
    opacity: 0.5;
    -webkit-mask-image: radial-gradient(circle, black 50%, transparent 100%);
    mask-image: radial-gradient(circle, black 50%, transparent 100%);
}}

.large-text {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 100px;
    font-weight: bold;
    color: white;
    text-shadow: 3px 3px 20px rgba(0,0,0,0.8);
}}
            
.medium-text {{
            
       position: absolute;
    top: 70%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 30px;
    font-weight: bold;
    color: white;
    text-shadow: 3px 3px 20px rgba(0,0,0,0.8);         
}}
</style>

<div class="image-container">
    <img src="data:image/png;base64,{img_str}" class="faded-image">
    <div class="large-text">JOBIFY<br></div>
    <div class="medium-text">Your AI Job-Search Assistant</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<br><br><br>', unsafe_allow_html=True)


st.markdown("""
<style>
.rcard {
    width: 300px;
    height: 350px;
    padding: 20px;
    border-radius: 10px;
    background: linear-gradient(135deg, #38069c, #62069c);
    color: white;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.pjcard {
    width: 300px;
    height: 350px;
    padding: 20px;
    border-radius: 10px;
    background: linear-gradient(135deg,#38069c, #147350);
    color: white;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.rcard:hover{
    transform: translateY(-10px);
    box-shadow: 5px 25px 25px rgba(220, 25, 250,0.5);
}
            
.pjcard:hover {
    transform: translateY(-10px);
    box-shadow: 5px 25px 25px rgba(60, 240, 171,0.5);
}

.ajcard {
    width: 300px;
    height: 350px;
    padding: 20px;
    border-radius: 10px;
    background: linear-gradient(135deg,#38069c, #0f8a88);
    color: white;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.ajcard:hover {
    transform: translateY(-10px);
    box-shadow: 5px 25px 25px rgba(60, 198, 240,0.5);
}

.card-container {
    display: flex;
    justify-content: center;
    gap: 100px;
    margin-top: 50px;
}
</style>         
""", unsafe_allow_html=True)


st.markdown("""
<p style="font-size: 18px; font-family :system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;">
            This AI Job Search Assistant is designed to revolutionize your job hunting experience. By leveraging advanced AI algorithms, we analyze your resume and preferences to curate a personalized list of job opportunities that align with your skills and aspirations. Whether you're looking for specific job titles, locations, or industries, our assistant ensures you receive tailored recommendations to help you find the perfect job match.</p>
""", unsafe_allow_html=True)

resume_img = Image.open("resume.png").convert("RGBA")
buffered_resume = BytesIO()
resume_img.save(buffered_resume, format="PNG")
resume_str = base64.b64encode(buffered_resume.getvalue()).decode()

choiceimg = Image.open("choicetr.png").convert("RGBA")
buffered_choice = BytesIO()
choiceimg.save(buffered_choice, format="PNG")
choice_str = base64.b64encode(buffered_choice.getvalue()).decode()

jobimg = Image.open("jobtr.png").convert("RGBA")
buffered_job = BytesIO()
jobimg.save(buffered_job, format="PNG")
job_str = base64.b64encode(buffered_job.getvalue()).decode()

html_cards = f"""
<div class="card-container">
    <div class="rcard">
        <h3 align="center">Upload Resume  ✦</h3>
        <img src="data:image/png;base64,{resume_str}" width="100" style="margin-left: 80px;">
        <p>Simply upoad you Resume and out AI agent will analyse your skills
        to find the best Job Opportunities for you.</p>
    </div>
    <div class="pjcard">
        <h3 align="center">Your Preferences</h3>
        <img src="data:image/png;base64,{choice_str}" width="150" style="margin-left: 50px;margin-top: 5px;">
        <p> Select you preferred job titles, locations, and industries to get personalized job recommendations.</p>
    </div>
    <div class="ajcard">
        <h3 align="center">AI Job Search  ✦</h3>
        <img src="data:image/png;base64,{job_str}" width="125" style="margin-left: 75px;margin-top: 5px;">
        <p>Our AI Agent curates a Job List as per you preferences and resume</p>
    </div>
</div>
"""

st.markdown(html_cards, unsafe_allow_html=True)
