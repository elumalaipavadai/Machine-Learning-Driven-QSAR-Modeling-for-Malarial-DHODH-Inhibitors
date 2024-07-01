import streamlit as st
#from molfeat.calc import FP_FUNCS
#import datamol as dm
import pandas as pd
from rdkit import Chem
import joblib
from PIL import Image
import subprocess
import os
import base64
from rdkit.Chem import Draw
import io
from molfeat.calc import FPCalculator
from molfeat.trans import MoleculeTransformer
#from molfeat.calc import FP_FUNCS

# Page title
st.markdown("""
    <style>
    .reportview-container .markdown-text-container {
        font-family: monospace;
        color: #0000FF;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
# <span style='color:#0000FF'>MalariaDHODHPredicter</span>
            
Small-molecules's Bioactivity Prediction App for Malarial Dihydroorotate Dehydrogenase (DHODH). 

With this app, you can predict how effective a small-molecule compound can inhibit the Malarial DHODH enzyme, a validated drug target for combating Malaria.
""", unsafe_allow_html=True)

# Logo image
image = Image.open('image/FINAL_malaria.png')
st.image(image, use_column_width=True)
st.markdown("""           
**References**
- Malaria DHODH bioactivity data was retrieved from the [ChEMBL Database](https://www.ebi.ac.uk/chembl/)
- PubChem Sketcher was used to draw the chemical structures [[Link]](https://pubchem.ncbi.nlm.nih.gov/edit2/index.html)   
- Descriptor calculated using [molfeat from datamol](https://molfeat.datamol.io/) and [RDKit](https://www.rdkit.org/)                         
- App was developed using `Python` and `Streamlit`   
                       
""")

st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #ADD8E6;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title('1. Draw a Chemical Structure')

# Provide link to PubChem Sketcher
st.sidebar.markdown("[Draw a structure in the PubChem Sketcher](https://pubchem.ncbi.nlm.nih.gov/edit2/index.html), then copy the resulting SMILES string and paste it below or directly input your SMILES string if you have one.")
# Add text input for SMILES string
smiles_string = st.sidebar.text_input('Paste your SMILES string here')

# Insert "OR"
st.sidebar.markdown("<p style='text-align: center; margin: 0.5em;'>OR</p>", unsafe_allow_html=True)

# Use markdown instead of header for the next section
st.sidebar.markdown("<h2 style='margin-top: 0;'>Upload your SMILES string in CSV</h2>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['csv'])

# Display an example input file
st.sidebar.markdown("""[Example input file](https://raw.githubusercontent.com/dataprofessor/bioactivity-prediction-app/main/example_acetylcholinesterase.txt)""")

# Sidebar
st.sidebar.title('2. Choose Your Favorite Model')

# our model names
model_names = ['cat_model', 'lgbm_model', 'xgb_model', 'hgbr_model']  # Replace with your actual model names

# Map each model name to its directory
model_directories = {
    'cat_model': '../data/model_data/cat_model.joblib',
    'lgbm_model': '../data/model_data/lgbm_model.joblib',
    'xgb_model': '../data/model_data/xgb_model.joblib',
    'hgbr_model': '../data/model_data/hgbr_model.joblib'
}

# Let the user select a model
selected_model_name = st.sidebar.selectbox('Select a model', model_names)
# Get the directory for the selected model
selected_model_directory = model_directories[selected_model_name]

# Display the selected model directory
#st.write(f"Directory for {selected_model_name}: {selected_model_directory}")

# Sidebar
st.sidebar.title('3. Make Prediction')
# Load the selected model
model = joblib.load(f'data/model_data/{selected_model_name}.joblib')


if st.sidebar.button('Predict Activity'):
    # Define your DataFrame here
    if smiles_string:
        df = pd.DataFrame({
            'canonical_smiles': [smiles_string]  # Use the input SMILES string
        })
    elif uploaded_file:
        try:
            df = pd.read_table(uploaded_file, header=None)
            df.columns = ['canonical_smiles']  # Assign column name
            df.to_csv('uploaded_file.smi', sep = '\t', header = False, index = False)
        except pd.errors.ParserError:
            print("There was an error parsing the uploaded file. Please ensure it is a valid CSV.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}") 
    print(df)  # Print the DataFrame to debug           

    # Calculate the fingerprints
    calc = FPCalculator("atompair") 
    trans = MoleculeTransformer(calc) 
    with dm.without_rdkit_log(): # suppress the RDKit warnings
        df['fp'] = trans.transform(df.canonical_smiles.values) 

    # Convert the fingerprints to the format expected by the model
    X = df['fp'].tolist()

    # Predict the activity
    df['activity (pIC50)'] = model.predict(X)

    # Convert pIC50 to IC50
    df['activity (IC50) nM'] = 10**(-df['activity (pIC50)']) * 1e9   

    # Drop the 'fp' column
    df = df.drop(columns=['fp'])
    #df = df.drop(columns=['fp', 'activity (pIC50)'])
    # Check if the DataFrame is not empty
    if not df.empty:
        # Display the DataFrame with the calculated fingerprints and predicted activity
        #st.write(df)

        # Display a title after the output
        #st.header("Prediction Results:")
        st.markdown("<h1 style='color: purple;'>Prediction Results:</h1>", unsafe_allow_html=True)
        # Display the DataFrame with the calculated fingerprints and predicted activity
        st.write(df)
