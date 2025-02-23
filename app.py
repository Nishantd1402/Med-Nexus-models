import os
from flask import Flask, request , session
#import tensorflow as tf
# from tensorflow.keras.preprocessing import image
import numpy as np
# from io import BytesIO
from flask_cors import CORS
from groq import Groq
from test import extract_text_from_pdf
import re
import json
from test_email import send_html_email

# def prepare_image(img, target_size=(150, 150)):
#     img = image.load_img(img, target_size=target_size)  # Load the image with target size
#     img_array = image.img_to_array(img)  # Convert the image to a numpy array
#     img_array = np.expand_dims(img_array, axis=0)  # Add a batch dimension
#     img_array = img_array / 255.0  # Rescale the image to the same range as the training data
#     return img_array

def extract_json(data):
     # Use regex to extract content inside triple backticks
    match = re.search(r'```(.*?)```', data, re.DOTALL)
    
    if match:
        json_str = match.group(1).strip()  # Extract JSON content and remove extra spaces
        try:
            return json.loads(json_str)  # Convert to Python dictionary
        except json.JSONDecodeError as e:
            print("Invalid JSON:", e)
            return None
    else:
        print("No JSON found in backticks")
        return None

def extract_json_0(input_text):
    try:
        start = input_text.find('{')
        end = input_text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(input_text[start:end + 1])
        else:
            return "No JSON-like structure found."
    except Exception as e:
        return f"An error occurred: {e}"

FILENAME = "pneumonia_model.h5"
folder_path = 'files'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

def get_completion_0(data , prompt):
    try:
            client = Groq(api_key="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")
            
            # Generate the completion using the OpenAI client
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"{prompt}. here is the data : {data}"}
                ],
                model="llama3-70b-8192",
                temperature=0.01  # Adjust randomness
            )
            response = chat_completion.choices[0].message.content
            return response
    except Exception as e:
        return "An error occurred while generating the response."
      
def get_completion(prompt , data=None):
    try:
            client = Groq(api_key="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")

            # Generate the completion using the OpenAI client
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"{prompt}"}
                ],
                model="llama3-70b-8192",
                temperature=0.01  # Adjust randomness
            )
            response = chat_completion.choices[0].message.content
            return response
    except Exception as e:
        return "An error occurred while generating the response."

# Load the model only once during initialization
# pneumonia_model = tf.keras.models.load_model(FILENAME)
app = Flask(__name__)
CORS(app)
app.secret_key = 'your-strong-secret-key'


# @app.route('/pneumonia', methods=['POST'])
# def detect():
#     # Get the image from the request
#     img = request.files['img']
    
#     # Convert the image to a file-like object using BytesIO
#     img = BytesIO(img.read())
    
#     # Process the image
#     img = prepare_image(img)  # Use the image object directly
    
#     # Get the model prediction
#     prediction = pneumonia_model.predict(img)
    
#     # Classify the result based on the prediction
#     predicted_class = 'Pneumonia' if prediction > 0.5 else 'Normal'
    
#     # Return the classification result
#     return predicted_class

@app.route('/prescription' , methods=['POST'])
def prescription():
    prompt = """You are an intelligent medical assistant that extracts structured information from prescriptions. Given the extracted text from a PDF prescription, generate a structured JSON output that includes the following details:

Medicine Name - The exact name of the medicine prescribed.
Purpose - The reason for prescribing this particular medicine in the whole prescription (e.g., "Pain Relief", "Blood Pressure Control", etc.).
Dosage - The prescribed dose of the medicine (e.g., "500 mg", "1 tablet").
Frequency - How often the medicine should be taken (e.g., "Once daily", "Twice daily").
Timing - When the medicine should be taken (e.g., "Before Breakfast", "After Lunch", "At Night").
Duration - The number of days or weeks the medicine should be taken.
Make sure to analyze the prescription carefully and format the response in a valid JSON format as shown in the skeleton below:

{
  "medications": [
    {
      "medicine_name": "",
      "purpose": "",
      "dosage": "",
      "frequency": "",
      "timing": "",
      "duration": ""
    },
    {
      "medicine_name": "",
      "purpose": "",
      "dosage": "",
      "frequency": "",
      "timing": "",
      "duration": ""
    }
  ]
}

"""
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath , prompt=prompt)
    response = get_completion_0(prompt=prompt , data= data)
    print(response)
    response = extract_json_0(response)
    return response

@app.route('/symptoms' , methods=['POST'])
def symptom():
  data = request.form.get('symptom')
  prompt = f"""Here is a list of symptoms observed in a patient. Provide a list of conditions they may suffer from. Analyze the symptoms carefully and only include conditions that have a strong likelihood based on the given symptoms.

Symptoms:
{data}

Provide the output in the following JSON format:

{{
    "conditions": [
        {{
            "name": "<Condition Name>",
            "likelihood": "<High/Moderate>",
            "reasoning": "<Brief explanation based on symptoms>"
        }},
        {{
            "name": "<Condition Name>",
            "likelihood": "<High/Moderate>",
            "reasoning": "<Brief explanation based on symptoms>"
        }}
    ]
}}"""
  
  analysis = extract_json_0(get_completion(prompt=prompt , data=None))
  session['analysis'] = analysis
  prompt2 = f"""You are given an initial analysis of a user's symptoms: ```{data}```, try to identify and narrow down the possible condition from the given analysis: ```{analysis}``` and narrow down on those conditions by asking only 2 questions.

Provide the output in the following JSON format:

{{
    "questions": [
        {{
            "question_1": "Does the headache occur with a throbbing or pulsating sensation?",
            "options_1": ["Yes", "No", "Not Sure"]
        }},
        {{
            "question_2": "Have you experienced any aura (flashing lights, blind spots, or tingling) before the headache starts?",
            "options_2": ["Yes", "No", "Not Sure"]
        }}
    ]
}}
"""

  question = extract_json(get_completion(prompt=prompt2 , data=None))
  session['symp'] = data
  return question

@app.route('/final_symptom' , methods=["POST"])
def final_symptom():
  conv = request.form.get('symptom')
  
  prompt3 = f"""analyze the question and symptoms narrow down to 1-2 condition with which user might have and suggest next steps to confirm the condition mentioned in analysis, using tests or visiting the doctor. Symtoms = ```{session.get('symp')}```. initial analysis - ```{session.get('analysis')}``` questions and user ansers = ```{conv}```


Provide the output in the following JSON format:
{{
    "conditions": [
        {{
            "name": "name of condition",
            "likelihood": "Low/Moderate/High",
            "reason": "Brief explanation of why this condition is likely based on symptoms and user responses.",
            "next_steps": [
                "Step 1 for confirmation (e.g., consult a specialist).",
                "Step 2 for further evaluation (e.g., medical tests).",
                "Step 3 for monitoring or management."
            ]
        }},
        {{
            "name": "name of condition",
            "likelihood": "Low/Moderate/High",
            "reason": "Brief explanation of why this condition is considered but with less certainty.",
            "next_steps": [
                "Step 1 for confirmation.",
                "Step 2 for further evaluation.",
                "Step 3 for symptom tracking."
            ]
        }}
    ]
}}"""
  results = extract_json_0((get_completion(prompt=prompt3 , data=None)))
  return results


@app.route('/CBC_report' , methods=["POST"])
def CBC_report():
    prompt = """You are given a pathology report in text format. Extract the relevant values for the Complete Blood Count (CBC) and format them in the following JSON structure. Ensure that each value is associated with its correct unit, and ignore any unnecessary information. Below is the expected structure of the output:

Extract the following values from the report:
WBC (White Blood Cell count)
RBC (Red Blood Cell count)
Hemoglobin (Hb)
Hematocrit (PCV)
Platelet Count
MCV (Mean Corpuscular Volume)
MCH (Mean Corpuscular Hemoglobin)
MCHC (Mean Corpuscular Hemoglobin Concentration)"""
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath , prompt=prompt)
    prompt = """You are a medical AI assistant specializing in hematology and blood analysis. Given a patient's CBC (Complete Blood Count) data in JSON format, analyze the parameters to identify possible diseases, their severity, and provide necessary precautions. Your response should include:

Disease Detection:

Identify potential diseases or conditions based on abnormalities in CBC values.
Provide reasoning based on parameter deviations.
Severity Assessment:

Categorize as Normal, Mild, Moderate, or Severe based on threshold deviations.
Precautions & Preventive Measures:

Suggest lifestyle changes, diet recommendations, and monitoring guidelines.
Recommend when to seek medical attention.
Treatment Recommendations (General Guidance):

Basic dietary or lifestyle changes.
When to consult a doctor.
Urgency Indicator:

Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue.

Follow this Output format strictly.
{
  "output_format": {
    "disease_detection": {
      "possible_conditions": ["Anemia", "Leukopenia", "Leukocytosis", "Thrombocytopenia", "Thrombocytosis", "Infection", "Bone Marrow Disorders"],
      "analysis": "Detailed explanation of detected abnormalities in RBC, WBC, hemoglobin, hematocrit, and platelets, along with their medical significance."
    },
    "severity_assessment": {
      "category": "Normal / Mild / Moderate / Severe",
      "explanation": "Justification based on standard reference ranges for CBC parameters and clinical interpretation."
    },
    "recommendations": {
      "dietary_changes": "List of recommended foods for blood health, including iron-rich foods, vitamin B12 sources, and hydration tips.",
      "lifestyle_changes": "Suggestions for maintaining healthy blood parameters, including exercise, hydration, and stress management.",
      "medical_attention": "Guidance on when to consult a hematologist for further testing or treatment."
    },
    "urgency": "Immediate Concern / Follow-up Needed / No Significant Issue"
  }
}
"""
    response = get_completion_0(data=data , prompt=prompt)
    response = extract_json_0(response)
    print(response)
    if response["output_format"]["severity_assessment"]["category"] == "Moderate" or response["output_format"]["severity_assessment"]["category"] == "Severe":
      send_html_email("jainmitesh2393@gmail.com", "Ashish Yadav", "moderate" , filepath)
      print("done")
    return response

@app.route('/Thyroid_report' , methods=["POST"])
def Thyroid_report():
    prompt = """You are given a Thyroid Profile Test report in text format. Extract the relevant values for the following thyroid-related parameters and format them in the specified JSON structure. Ensure that each value is associated with its correct unit, and ignore any unnecessary information. Below is the expected structure of the output:

Extract the following parameters from the report:
TSH (Thyroid Stimulating Hormone)
T3 (Triiodothyronine)
T4 (Thyroxine)
Free T3
"""
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath , prompt=prompt)
    prompt = """You are a medical AI assistant specializing in endocrinology and thyroid function analysis. Given a patient's Thyroid Profile Test data in JSON format, analyze the parameters to identify potential diseases, assess their severity, and provide necessary precautions.

Analysis Requirements:
Disease Detection:

Identify possible thyroid-related conditions such as hypothyroidism, hyperthyroidism, Hashimoto’s thyroiditis, or Graves' disease based on deviations in TSH, T3, T4, Free T3, Free T4, and thyroid antibodies.
Provide reasoning based on clinical thresholds and correlations between parameters.
Severity Assessment:

Categorize findings as Normal, Mild, Moderate, or Severe based on standard reference ranges.
Precautions & Preventive Measures:

Suggest dietary recommendations (e.g., iodine-rich foods, selenium intake, avoiding goitrogens).
Lifestyle modifications for thyroid health and hormonal balance.
When to monitor thyroid levels and seek medical attention.
Treatment Recommendations (General Guidance):

Provide basic lifestyle or dietary modifications.
Advise when to consult an endocrinologist for medication or further tests.
Urgency Indicator:

Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue.

{
  "output_format": {
    "disease_detection": {
      "possible_conditions": ["Hypothyroidism", "Hyperthyroidism", "Hashimoto’s Thyroiditis", "Graves' Disease", "Thyroid Nodules", "Thyroiditis"],
      "analysis": "Detailed explanation of detected abnormalities in TSH, T3, T4, Free T3, Free T4, and thyroid antibodies, along with their medical significance."
    },
    "severity_assessment": {
      "category": "Normal / Mild / Moderate / Severe",
      "explanation": "Justification based on standard reference ranges for thyroid function tests and clinical interpretation."
    },
    "recommendations": {
      "dietary_changes": "List of recommended foods such as iodine-rich foods, selenium sources, and goitrogen avoidance.",
      "lifestyle_changes": "Suggestions for maintaining thyroid health, including stress management, regular exercise, and sleep hygiene.",
      "medical_attention": "Guidance on when to consult an endocrinologist for medication adjustments, imaging, or further hormonal assessments."
    },
    "urgency": "Immediate Concern / Follow-up Needed / No Significant Issue"
  }
}
"""
    response = get_completion_0(data=data , prompt=prompt)
    response = extract_json_0(response)
    if response["output_format"]["severity_assessment"]["category"] == "Moderate" or response["output_format"]["severity_assessment"]["category"] == "Severe":
      send_html_email("jainmitesh2393@gmail.com", "Ashish Yadav", "moderate" , filepath)
      print("done")
    return response
@app.route('/report' , methods=["POST"])
def report():
    prompt = '''Prompt:
    
You are given a Lipid Profile Test report in text format. Extract the relevant values for the following lipid profile parameters and format them in the specified JSON structure. Ensure that each value is associated with its correct unit, and ignore any unnecessary information. Below is the expected structure of the output:

Extract the following parameters from the report:
Total Cholesterol
HDL Cholesterol (High-Density Lipoprotein)
LDL Cholesterol (Low-Density Lipoprotein)
Triglycerides
VLDL Cholesterol (Very-Low-Density Lipoprotein)
Cholesterol/HDL Ratio
LDL/HDL Ratio'''
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath , prompt=prompt)
    print(data)
    prompt = """You are a medical AI assistant specializing in hepatology and liver function analysis. Given a patient's Liver Function Test data in JSON format, analyze the parameters to identify potential liver diseases, assess their severity, and provide necessary precautions.
    you will be given following details
    Total Cholesterol
HDL Cholesterol (High-Density Lipoprotein)
LDL Cholesterol (Low-Density Lipoprotein)
Triglycerides
VLDL Cholesterol (Very-Low-Density Lipoprotein)
Cholesterol/HDL Ratio
Analysis Requirements:
Disease Detection:
Identify possible liver-related conditions such as hepatitis, cirrhosis, fatty liver disease, liver failure, or cholestasis based on deviations in ALT, AST, ALP, bilirubin, albumin, and prothrombin time.
Provide reasoning based on clinical thresholds and correlations between these parameters.
Severity Assessment:
Categorize findings as Normal, Mild, Moderate, or Severe based on standard reference ranges for LFT parameters.
Consider abnormal results such as elevated enzymes, high bilirubin levels, or prolonged clotting times as potential indicators of liver dysfunction.
Precautions & Preventive Measures:
Suggest dietary recommendations (e.g., low-fat, high-antioxidant foods, avoiding alcohol).
Advise on lifestyle modifications for liver health, including weight management, avoiding toxins, and maintaining a healthy diet.
When to monitor liver levels and seek medical attention, especially in the case of chronic liver disease or acute liver injury.
Treatment Recommendations (General Guidance):
Provide basic lifestyle or dietary modifications to support liver health.
Advise when to consult a hepatologist or gastroenterologist for medication, further tests, or imaging.
Urgency Indicator:
Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue.
Highlight whether further testing or immediate medical intervention is required based on abnormal results.

Follow this output format strictly. Only JSON output
{
  "output_format": {
    "disease_detection": {
      "possible_conditions": ["Hepatitis", "Cirrhosis", "Fatty Liver Disease", "Liver Failure", "Cholestasis"],
      "analysis": "Detailed explanation of detected abnormalities and their medical significance."
    },
    "severity_assessment": {
      "category": "Normal / Mild / Moderate / Severe",
      "explanation": "Justification based on reference ranges and medical interpretation."
    },
    "recommendations": {
      "dietary_changes": "List of recommended foods and those to avoid.",
      "lifestyle_changes": "Suggestions for maintaining liver health.",
      "medical_attention": "When to consult a specialist."
    },
    "urgency": "Immediate Concern / Follow-up Needed / No Significant Issue"
  }
}

"""
    response = get_completion_0(data=data , prompt=prompt)
    response = extract_json_0(response)
    if response["output_format"]["severity_assessment"]["category"] == "Moderate" or response["output_format"]["severity_assessment"]["category"] == "Severe":
      send_html_email("jainmitesh2393@gmail.com", "Ashish Yadav", "moderate" , filepath)
      print("done")
    return response
  
@app.route('/KFT_report' , methods=["POST"])
def KFT_report():
    prompt = """You are given a pathology report in text format. Extract the relevant values for the Kidney Function Test (KFT) and format them in the following JSON structure. Ensure that each value is associated with its correct unit, and ignore any unnecessary information. Below is the expected structure of the output:

Extract the following values from the report:
- Urea
- Creatinine
- Uric Acid
- Calcium
- Phosphorus
- Alkaline Phosphatase (ALP)
- Total Protein
- Albumin
- Sodium
- Potassium
- Chloride
"""
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath, prompt=prompt)

    analysis_prompt = """You are a medical AI assistant specializing in nephrology and kidney function analysis. Given a patient's Kidney Function Test (KFT) data in JSON format, analyze the parameters to identify possible kidney-related diseases, their severity, and provide necessary precautions. Your response should include:

    Disease Detection:
    - Identify potential diseases or conditions based on abnormalities in KFT values.
    - Provide reasoning based on parameter deviations.
    
    Severity Assessment:
    - Categorize as Normal, Mild, Moderate, or Severe based on threshold deviations.
    
    Precautions & Preventive Measures:
    - Suggest lifestyle changes, diet recommendations, and monitoring guidelines.
    - Recommend when to seek medical attention.
    
    Treatment Recommendations (General Guidance):
    - Basic dietary or lifestyle changes.
    - When to consult a doctor.
    
    Urgency Indicator:
    - Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue.

    Follow this Output format strictly.
    {
      "output_format": {
        "disease_detection": {
          "possible_conditions": ["Chronic Kidney Disease", "Acute Kidney Injury", "Electrolyte Imbalance", "Hyperuricemia", "Hypocalcemia", "Hyperphosphatemia", "Dehydration"],
          "analysis": "Detailed explanation of detected abnormalities in urea, creatinine, uric acid, electrolytes, and protein levels, along with their medical significance."
        },
        "severity_assessment": {
          "category": "Normal / Mild / Moderate / Severe",
          "explanation": "Justification based on standard reference ranges for KFT parameters and clinical interpretation."
        },
        "recommendations": {
          "dietary_changes": "List of recommended foods for kidney health, including low-sodium diet, hydration tips, and foods to avoid.",
          "lifestyle_changes": "Suggestions for maintaining kidney function, including exercise, hydration, and avoiding nephrotoxic substances.",
          "medical_attention": "Guidance on when to consult a nephrologist for further testing or treatment."
        },
        "urgency": "Immediate Concern / Follow-up Needed / No Significant Issue"
      }
    }
    """

    response = get_completion_0(data=data , prompt=prompt)
    response = extract_json_0(response)
    if response["output_format"]["severity_assessment"]["category"] == "Moderate" or response["output_format"]["severity_assessment"]["category"] == "Severe":
      send_html_email("jainmitesh2393@gmail.com", "Ashish Yadav", "moderate" , filepath)
      print("done")
    return response

@app.route('/urine_report' , methods=["POST"])
def urine_report():
    prompt = """You are given a pathology report in text format. Extract the relevant values for the Urine Culture & Sensitivity Test and format them in the following JSON structure. Ensure that each value is associated with its correct unit, and ignore any unnecessary information. Below is the expected structure of the output:

Extract the following values from the report:
- Organism Isolated
- Colony Count (CFU/ml)
- Impression
- Antibiotic Sensitivity (List of antibiotics categorized as Sensitive or Resistant)
"""
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath, prompt=prompt)

    analysis_prompt = """You are a medical AI assistant specializing in urinary tract infections (UTIs) and microbiology. Given a patient's Urine Culture & Sensitivity Test data in JSON format, analyze the parameters to identify possible infections, their severity, and provide necessary precautions. Your response should include:

    Infection Detection:
    - Identify possible infections based on the organism isolated and colony count.
    - Provide reasoning based on microbiological findings.
    
    Severity Assessment:
    - Categorize as Normal, Mild, Moderate, or Severe based on threshold deviations.
    
    Precautions & Preventive Measures:
    - Suggest hygiene practices, fluid intake recommendations, and monitoring guidelines.
    - Recommend when to seek medical attention.
    
    Treatment Recommendations (General Guidance):
    - Basic dietary or lifestyle changes.
    - Importance of completing prescribed antibiotic courses.
    - When to consult a doctor.
    
    Urgency Indicator:
    - Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue.

    Follow this Output format strictly.
    {
      "output_format": {
        "infection_detection": {
          "possible_conditions": ["Urinary Tract Infection (UTI)", "Kidney Infection", "Asymptomatic Bacteriuria", "Resistant Bacterial Infection"],
          "analysis": "Detailed explanation of detected bacterial organisms, their significance, and antibiotic sensitivity results."
        },
        "severity_assessment": {
          "category": "Normal / Mild / Moderate / Severe",
          "explanation": "Justification based on standard reference ranges for colony count and organism pathogenicity."
        },
        "recommendations": {
          "hygiene_practices": "Suggestions for personal hygiene, hydration, and UTI prevention.",
          "lifestyle_changes": "Tips on maintaining urinary tract health, avoiding triggers, and recognizing early symptoms.",
          "medical_attention": "Guidance on when to consult a urologist or start antibiotic treatment."
        },
        "urgency": "Immediate Concern / Follow-up Needed / No Significant Issue"
      }
    }
    """
    response = get_completion_0(data=data , prompt=prompt)
    response = extract_json_0(response)
    if response["output_format"]["severity_assessment"]["category"] == "Moderate" or response["output_format"]["severity_assessment"]["category"] == "Severe":
      send_html_email("jainmitesh2393@gmail.com", "Ashish Yadav", "moderate" , filepath)
      print("done")
    return response

@app.route('/pet_scan_report' , methods=["POST"])
def pet_scan_report():
    prompt = """You are given a radiology report in text format. Extract the relevant values for the PET Scan and format them in the following JSON structure. Ensure that each value is associated with its correct unit, and ignore any unnecessary information. Below is the expected structure of the output:

Extract the following values from the report:
- Examination Type
- Radiotracer Used
- Dose (millicuries)
- Blood Glucose Level (mg/dL)
- Findings (Neck, Chest, Abdomen/Pelvis, Skeletal)
- Impression (Key observations)
"""
    file = request.files['report']
    filepath = 'files/'
    filename = file.filename
    filepath = os.path.join(filepath, filename)
    file.save(filepath)
    data = extract_text_from_pdf(filepath, prompt=prompt)

    analysis_prompt = """You are a medical AI assistant specializing in radiology and PET scan analysis. Given a patient's PET scan data in JSON format, analyze the parameters to identify possible abnormalities, their severity, and provide necessary precautions. Your response should include:

    Abnormality Detection:
    - Identify possible conditions based on PET scan findings.
    - Provide reasoning based on observed hypermetabolic or hypometabolic activity.
    
    Severity Assessment:
    - Categorize as Normal, Mild, Moderate, or Severe based on threshold deviations.
    
    Precautions & Preventive Measures:
    - Suggest follow-up imaging, biopsy recommendations, and lifestyle adjustments.
    - Recommend when to seek medical attention.
    
    Treatment Recommendations (General Guidance):
    - Basic lifestyle and dietary suggestions for metabolic health.
    - When to consult a radiologist or oncologist.
    
    Urgency Indicator:
    - Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue.

    Follow this Output format strictly.
    {
      "output_format": {
        "abnormality_detection": {
          "possible_conditions": ["Metastatic Cancer", "Benign Tumor", "Inflammatory Disease", "Esophagitis", "Lung Disease", "Bone Disorders"],
          "analysis": "Detailed explanation of detected abnormalities in various body regions based on PET scan results."
        },
        "severity_assessment": {
          "category": "Normal / Mild / Moderate / Severe",
          "explanation": "Justification based on standard reference ranges and clinical interpretation."
        },
        "recommendations": {
          "follow_up": "Suggestions for additional imaging, biopsies, or monitoring.",
          "lifestyle_changes": "Tips on maintaining overall metabolic health and addressing potential findings.",
          "medical_attention": "Guidance on when to consult a radiologist or oncologist for further evaluation."
        },
        "urgency": "Immediate Concern / Follow-up Needed / No Significant Issue"
      }
    }

    """

    response = get_completion_0(data=data , prompt=prompt)
    response = extract_json_0(response)
    if response["output_format"]["severity_assessment"]["category"] == "Moderate" or response["output_format"]["severity_assessment"]["category"] == "Severe":
      send_html_email("jainmitesh2393@gmail.com", "Ashish Yadav", "moderate" , filepath)
      print("done")
    return response

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
