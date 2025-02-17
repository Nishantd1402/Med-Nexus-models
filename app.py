import os
from flask import Flask, request
# import tensorflow as tf
# from tensorflow.keras.preprocessing import image
import numpy as np
# from io import BytesIO
from flask_cors import CORS
from groq import Groq
from test import extract_text_from_pdf

# def prepare_image(img, target_size=(150, 150)):
#     img = image.load_img(img, target_size=target_size)  # Load the image with target size
#     img_array = image.img_to_array(img)  # Convert the image to a numpy array
#     img_array = np.expand_dims(img_array, axis=0)  # Add a batch dimension
#     img_array = img_array / 255.0  # Rescale the image to the same range as the training data
#     return img_array

FILENAME = "pneumonia_model.h5"

def get_completion_0(data , prompt):
    try:
            client = Groq(api_key="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")
            
            # Generate the completion using the OpenAI client
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"{prompt}. here is the data : {data}"}
                ],
                model="llama3-70b-8192",
                temperature=0.1  # Adjust randomness
            )
            response = chat_completion.choices[0].message.content
            return response
    except Exception as e:
        return "An error occurred while generating the response."

# Load the model only once during initialization
# pneumonia_model = tf.keras.models.load_model(FILENAME)
app = Flask(__name__)
CORS(app)


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
Structured Output (JSON format):

Provide a structured JSON output suitable for API integration."""
    return get_completion_0(data=data , prompt=prompt)

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

Indicate if the findings suggest Immediate Concern, Follow-up Needed, or No Significant Issue."""
    return get_completion_0(data=data , prompt=prompt)

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
"""
    return get_completion_0(data=data , prompt=prompt)

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
