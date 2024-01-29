import streamlit as st
import docx2txt
import tempfile
import pdfplumber
import wordninja
import os
import shutil
from pydub import AudioSegment
from pydub.utils import make_chunks
import re

def save_audio_file(audio, audio_input_type):
    if audio_input_type == "AudioFile Upload":
        # Create a temporary file using tempfile module
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        # Save the uploaded file to the temporary file
        temp_file.write(audio.getvalue())
        # Close the temporary file
        temp_file.close()
        # Use the temporary file path for further processing or analysis
        temp_file_path = temp_file.name
    elif audio_input_type in ["Record Audio", "Extracted Audio"]:
        print("audio ip", audio, audio_input_type)
        if audio_input_type == "Record Audio":
            record_destination_path = "recording.wav"
        elif audio_input_type == "Extracted Audio":
            try:
                audio_name = audio.name.split(".")[0]
                if audio_name.endswith(".wav"):
                    record_destination_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','ExtractedAudio',audio_name)
                else:
                    record_destination_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','ExtractedAudio',audio_name+".wav")
                with open(record_destination_path, 'wb') as f:
                    f.write(audio)
                    temp_file_path = record_destination_path
            except:
                temp_file_path = audio
    elif audio_input_type == "Local Video Upload":
        # # Create a temporary file using tempfile module
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        # Save the uploaded file to the temporary file
        temp_file.write(audio.read())    
        temp_file_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedVideo', audio.name)
        with open(temp_file_path, "wb") as tf:
            shutil.copy(temp_file.name, temp_file_path)
    return temp_file_path

def save_video_file(video_uploaded_file):
    video_destination_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedVideo',video_uploaded_file.name)
    with open(video_destination_path, "wb") as tf:
        tf.write(video_uploaded_file.getvalue())
    return video_destination_path

def play_audio_fn(audio):
    audio_bytes = audio.read()    
    st.audio(audio_bytes, format = "audio/mp3")

def language_code_mbart(language):
    language_mappings = {"English":"en_XX", "Tamil":"ta_IN"}
    return language_mappings[language]

# Function to update the value in session state
def clicked(button):
    st.session_state.clicked[button] = True
    return st.session_state.clicked



def process_document_file_upload(document_uploaded_file, language):
    file_details = {"filename":document_uploaded_file.name, "filetype":document_uploaded_file.type,"filesize":document_uploaded_file.size}
    if file_details:
        if document_uploaded_file.type == "text/plain":
            raw_text = str(document_uploaded_file.read(),"utf-8") # works with st.text and st.write,used for further processing
            data = document_uploaded_file.getvalue().decode("utf-8")
            st.write("Original file contents: ",raw_text) 
        elif document_uploaded_file.type == "application/pdf":
            try:                   
                if language!= "English":
                    st.info("Please upload a docx or txt file", icon="ℹ️")
                    pass                    
                elif language == "English":
                    with pdfplumber.open(document_uploaded_file) as mypdf:
                        pages = mypdf.pages[0] 
                        data = pages.extract_text()
                        data = " ".join(wordninja.split(data))
                        st.write("Original file contents: ",data)
            except Exception as e:
                st.write("Exception is ", e)
                st.write("Original file contents: ","None")
                data = None
        else:
            data = docx2txt.process(document_uploaded_file)
            st.write("Original file contents: ",data)    
    else:
        data = None
    return data

def highest_multiple_of_chunksize(totaldur, chunksize):
  """
  This function finds the highest multiple of 5 which is less than a given number x.

  Args:
    x: An integer number.

  Returns:
    The highest multiple of 5 which is less than x.
  """
  # converts float to nearest integer
  x = int(totaldur)
  # Check if x is already a multiple of 5
  if x % chunksize == 0:
    return x
  # Otherwise, subtract 5 until we find a multiple of 5
  else:
    while x % chunksize != 0:
      x -= 1
    return x
  



def remove_non_alphanumeric(text):
    """
    This function removes all non-alphanumeric characters from a string.

    Args:
        text: The string to be processed.

    Returns:
        The string with all non-alphanumeric characters removed.
    """
    return re.sub(r"[^\w\s]", "", text).strip()
  
  


