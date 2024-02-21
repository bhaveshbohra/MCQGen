import os
import json
import pandas as pd
import traceback 
from dotenv import load_dotenv

from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st

from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGen import generate_evaluate_chain
from src.mcqgenerator.logger import logging

#loading json file 
with open('D:\MCQGen\Response.json','r') as file:
    RESPONSE_JSON= json.load(file)

# creating title for the app
st.title("MCQs Creator Application with Langchain")

#create a form using st.form
with st.form("user_inputs"):
    #file Upload
    uploaded_file= st.file_uploader("Upload a PDF or txt file")

    #Input Fields
    mcq_count= st.number_input("No. of MCQs", min_value=3, max_value=50)

    #Subject
    subject= st.text_input("Insert Subject", max_chars=20)

    #Quiz Tone
    tone=st.text_input("Complexity Level of Question", max_char=20, placeholder="simple")

    #Add Button
    submit_button= st.form_submit_button("create MCQs")

    #check if the button is clicked and all field have input 

    if submit_button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text= read_file(uploaded_file)
                #count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response= generate_evaluate_chain( 
                    {
                        "text":text,
                        "number": mcq_count,
                        "subject":subject,
                        "tone":tone,
                        "response_json":json.dumps(RESPONSE_JSON)
                    }
                ) 
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)

            else:
                print(f"Total Token:{cb.total_tokens}")
                print(f"Prompt Token:{cb.prompt_tokens}")
                print(f"Completion Token:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response,dict):
                    
                    quiz= response.get("quiz",None)
                    if quiz is not None:
                        table_data= get_table_data(quiz)
                        if table_data is not None:
                            df= pd.DataFrame(table_data)
                            df.index= df.index+1
                            st.table(df)
                            #Display the review in atext box as well
                            st.text_area(label="Review", value =response["review"])
                        else:
                            st.error("Error in the table data")
        
                else:
                    st.write(response)



