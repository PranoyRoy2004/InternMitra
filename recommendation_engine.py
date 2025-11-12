import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import gradio as gr
import os
import openai
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. Data Creation ---

# Create synthetic internship data
internships_data = {
    'Internship ID': range(1, 21),
    'Internship Title': [
        'Software Engineering Intern', 'Data Science Intern', 'Product Management Intern',
        'UX/UI Design Intern', 'Marketing Intern', 'Financial Analyst Intern',
        'HR Intern', 'Legal Intern', 'Operations Intern', 'Strategy Intern',
        'Research Intern', 'Consulting Intern', 'Technical Writing Intern',
        'Sales Intern', 'Customer Success Intern', 'Cybersecurity Intern',
        'Cloud Engineering Intern', 'AI/ML Development Intern', 'Bioinformatics Intern',
        'Sustainability Intern'
    ],
    'Company': [f'Company {i % 5 + 1}' for i in range(20)],
    'Location': ['Seattle, WA', 'San Francisco, CA', 'New York, NY', 'Austin, TX'] * 5,
    'Stipend': np.random.randint(1000, 5000, 20),
    'Description': [
        'Develop and test software applications. Work with Python, Java, and cloud platforms.',
        'Analyze large datasets using Python and R. Build and evaluate machine learning models.',
        'Assist product managers with roadmap and strategy. Conduct market research and user interviews.',
        'Design and prototype user interfaces. Work with Figma, Sketch, and conduct user testing.',
        'Develop and execute digital marketing campaigns. Manage social media and content creation.',
        'Perform financial modeling and analysis. Assist with budgeting and forecasting.',
        'Support the HR department with recruitment and onboarding. Assist with employee relations.',
        'Conduct legal research and draft documents. Assist with compliance and contract review.',
        'Optimize operational processes and logistics. Analyze supply chain data.',
        'Support high-level strategic research on various topics. Analyze data and prepare reports.',
        'Support consulting projects and assist with client presentations. Conduct industry research.',
        'Write and edit technical documentation. Create user manuals and guides.',
        'Assist sales team with lead generation and client outreach. Prepare sales materials.',
        'Support customer success initiatives. Help onboard new customers and address inquiries.',
        'Assist with cybersecurity analysis and threat detection. Learn about security protocols.',
        'Work on cloud infrastructure projects. Deploy and manage cloud resources.',
        'Develop and implement AI and machine learning models. Work with data scientists and engineers.',
        'Analyze biological data using computational tools. Work on genomics and proteomics projects.',
        'Support environmental impact assessments and sustainability projects. Conduct field research.'
    ]
}
internships_df = pd.DataFrame(internships_data)

# Create synthetic student data
students_data = {
    'Student ID': range(101, 111),
    'Student Name': [f'Student {i}' for i in range(1, 11)],
    'Skills': [
        'Python, Java, C++, Data Structures, Algorithms, Web Development',
        'Python, R, SQL, Machine Learning, Data Analysis, Statistics',
        'Product Management, Market Research, Strategy, Communication, Agile',
        'UI/UX Design, Figma, Sketch, Adobe XD, Prototyping, User Research',
        'Digital Marketing, SEO, Social Media, Content Creation, Analytics',
        'Financial Modeling, Excel, Valuation, Accounting, Risk Analysis',
        'Recruitment, Training, Employee Relations, HRIS, Labor Law',
        'Legal Research, Contract Drafting, Public Policy, Moot Court',
        'Supply Chain Management, Logistics, Process Optimization, SAP',
        'Data Science, Artificial Intelligence, Analytics, Research'
    ],
    'Interests': [
        'Software Development, Cloud Computing, AI, Technology',
        'Data Science, Machine Learning, Analytics, Research',
        'Product Development, Business Strategy, Entrepreneurship, Technology',
        'User Experience, Interaction Design, Human-Computer Interaction',
        'Marketing, Social Media, Advertising, Content Creation',
        'Finance, Investment Banking, Corporate Strategy',
        'Human Resources, Talent Acquisition, Organizational Development',
        'Law, Public Service, Corporate Governance',
        'Operations, Logistics, Business Process Reengineering',
        'AI/ML, Data-Driven Decision Making, Research'
    ],
    'Experience': [
        'Contributed to open-source projects using Python and Java. Built a personal portfolio website.',
        'Worked on several data analysis projects using Python and R. Participated in Kaggle competitions.',
        'Gained experience in product management through a previous internship and academic projects.',
        'Designed an app interface for a school project. Proficient with Figma and Sketch.',
        'Managed social media accounts for student organizations. Created marketing content for events.',
        'Completed a virtual internship in financial modeling. High proficiency in Excel.',
        'Interned at the HR department of a small company. Assisted with recruitment tasks.',
        'Interned at a law firm and conducted legal research. Participated in moot court competitions.',
        'Assisted with logistics for university events. Optimized processes for a student club.',
        'Published a research paper on machine learning in a student conference.'
    ]
}
students_df = pd.DataFrame(students_data)

# Combine relevant columns for embedding
internships_df['combined_text'] = (
    internships_df['Internship Title'] + ". " +
    internships_df['Company'] + ". " +
    internships_df['Description']
)

students_df['combined_text'] = (
    students_df['Skills'] + ". " +
    students_df['Interests'] + ". " +
    students_df['Experience']
)

# --- 2. AI Recommendation Engine ---

# 2.1. Encoding
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

print(f"Encoding {len(internships_df)} internship descriptions...")
internship_embeddings = model.encode(internships_df['combined_text'].tolist(), convert_to_numpy=True)

print(f"Encoding {len(students_df)} student profiles...")
student_embeddings = model.encode(students_df['combined_text'].tolist(), convert_to_numpy=True)

# 2.2. FAISS Indexing and Search
d = internship_embeddings.shape[1]  # Dimension of the embeddings (384 for all-MiniLM-L6-v2)
index = faiss.IndexFlatL2(d)

# Add the internship embeddings to the index
index.add(internship_embeddings)

# Define the number of top recommendations
k = 5

# --- 3. Optional OpenAI Enhancement Function ---

def get_personalized_summary(student_name, internship_details):
    """
    Generates a personalized summary explaining why an internship is a good match
    for a student using OpenAI.
    """
    # Check if OpenAI API key is available
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        return "Personalized summary (OpenAI enhancement not available - Set OPENAI_API_KEY)."

    # Configure OpenAI API key
    openai.api_key = openai_api_key

    try:
        # Get student profile
        student_profile = students_df[students_df['Student Name'] == student_name].iloc[0]
        student_combined_text = student_profile['combined_text']

        # Construct the prompt for OpenAI
        prompt = f"""
        As an AI internship recommender, generate a concise, personalized summary (around 50-100 words) explaining why the following internship is a good match for the student based on their profile.

        Student Profile:
        {student_combined_text}

        Recommended Internship:
        Title: {internship_details['Internship Title']}
        Company: {internship_details['Company']}
        Description: {internship_details['Description']}
        """

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # Using a common, fast model
            messages=[
                {"role": "system", "content": "You are a helpful and professional internship recommender."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()

    except Exception as e:
        # Handle API errors gracefully
        print(f"OpenAI API Error: {e}")
        return "Personalized summary failed to generate due to API error."

# --- 4. Recommendation Function (Core Logic) ---

def recommend_internships(student_name):
    """
    Recommends top k internships for a given student based on their profile.
    """
    # Find the row of the input student
    student_row = students_df[students_df['Student Name'] == student_name]
    if student_row.empty:
        print(f"Student '{student_name}' not found.")
        return []

    student_idx = student_row.index[0]

    # Get the embedding for the specific student and reshape for FAISS
    student_embedding = student_embeddings[student_idx].reshape(1, -1)

    # Perform similarity search
    # FAISS uses L2 distance (smaller is better).
    distances, indices = index.search(student_embedding, k)

    # Retrieve recommended internship indices
    recommended_internship_indices = indices[0]

    # Create a list of dictionaries for recommended internships
    recommended_internships_list = []
    for i, internship_index in enumerate(recommended_internship_indices):
        internship_details = internships_df.iloc[internship_index]

        # Get personalized summary (optional)
        personalized_summary = get_personalized_summary(student_name, internship_details)

        recommendation = {
            'Internship Title': internship_details['Internship Title'],
            'Company': internship_details['Company'],
            'Location': internship_details['Location'],
            'Stipend (USD)': f"${internship_details['Stipend']}",
            'Personalized Summary': personalized_summary 
        }
        recommended_internships_list.append(recommendation)

    # Convert the list of dicts to a DataFrame for Gradio output
    recommendations_df = pd.DataFrame(recommended_internships_list)
    return recommendations_df

# --- 5. Gradio Web Interface ---

# Get the list of student names for the dropdown
student_names = students_df['Student Name'].tolist()

# Define the output component (DataFrame to display recommendations including personalized summary)
recommendations_output = gr.DataFrame(
    label="Recommended Internships", 
    headers=["Internship Title", "Company", "Location", "Stipend (USD)", "Personalized Summary"]
)

# Create the Gradio Interface
iface = gr.Interface(
    fn=recommend_internships,
    inputs=gr.Dropdown(choices=student_names, label="Select Student"),
    outputs=recommendations_output,
    title="🌟 AI-Based Internship Recommendation Engine 🌟",
    description=(
        "Select a student from the dropdown to get their top 5 internship recommendations "
        "based on their profile and the internship descriptions. "
        "A Sentence Transformer model (all-MiniLM-L6-v2) and FAISS are used for the matching. "
        "Personalized summaries are generated via OpenAI (if OPENAI_API_KEY is set)."
    )
)

# Launch the interface
if __name__ == "__main__":
    print("Launching Gradio Interface...")
    iface.launch(inbrowser=True)
    print("Gradio interface is running. Access it via the displayed URL.")
