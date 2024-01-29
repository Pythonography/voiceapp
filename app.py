
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_player import st_player
import streamlit.components.v1 as components
import datetime

from speech_translation import translate_speech
import utils
import video_services

speech_translation_object = translate_speech()

def main():

    st.title("Translation and Transcription")
    

    service_request = st.sidebar.selectbox("Choose service request", ("Speech Recognition","Text-to-Speech", "Text Translation","Speech Translation", "Video Services"),key="request") 

    if service_request in ["Speech Recognition", "Speech Translation"]:
        audio_input_type = st.sidebar.selectbox("Choose audio input type", ("AudioFile Upload", "Record Audio"),key="audio_input_type")
        
    elif service_request in ["Text-to-Speech", "Text Translation"]:
        text_input_type = st.sidebar.selectbox("Choose text input type", ("DocumentFile Upload", "Input Text"),key="text_input_type") 

    elif service_request in ["Video Services"]:
        video_input_type = st.sidebar.selectbox("Choose video input type", ("Insert Video URL", "Local Video Upload"),key="video_input_type") 
        video_service_type = st.sidebar.selectbox("Choose video service type", ("Video Transcribe", "Video Translate", "Add Subtitles"), key = "video_service_type")

            
    

    if service_request == "Video Services": 
        if video_input_type == "Local Video Upload":
            if video_service_type == "Video Transcribe": 
                language = st.selectbox("Choose transcription language", ("English", "Tamil"))
                if 'clicked' not in st.session_state: 
                    st.session_state.clicked = {5:False} 
                else:
                    st.session_state.clicked = {5:True}  
                try:
                    # if video_input_type == "Insert Video URL":
                    #     st_player("https://youtu.be/CmSKVW1v0xM")
                    #if video_input_type == "Local Video Upload": 
                    video_uploaded_file = st.file_uploader("Upload file", type=["mp4"], key="video_file_uploader_obj1")  
                    if video_uploaded_file is not None:        
                        st.session_state.clicked[5] = st.button("Transcribe Video", on_click=utils.clicked, args=[5]) 
                        t1 = datetime.datetime.now()
                        if st.session_state.clicked[5]:
                            
                            if video_uploaded_file is not None:
                                st.write("Play Original Video")
                                st.video(video_uploaded_file)
                                vfpath = utils.save_audio_file(video_uploaded_file,video_input_type) 
                                originalfilename = vfpath.split("\\")[-1].split(".")[0]
                                originalfilename = utils.remove_non_alphanumeric(originalfilename)
                                audio_file_path = video_services.extract_audio(vfpath, originalfilename) 
                                audio_file = open(audio_file_path, "rb")
                                st.write("Play Extracted Audio")
                                utils.play_audio_fn(audio_file)
                                transcription_subclips = video_services.video_transcribe(audio_file_path, originalfilename,language, audio_input_type= "Extracted Audio")
                                transcription = " ".join(transcription_subclips)
                                t2 = datetime.datetime.now()
                                t = t2-t1
                                st.write("total time",t)
                                # audio_input_type = "Extracted Audio"    
                                # if language == "English":                     
                                #     transcription = speech_translation_object.transcribe_english(audio_file_path, audio_input_type) 
                                # elif language == "Tamil":
                                #     print("audio file path", audio_file_path)
                                #     transcription = speech_translation_object.transcribe_tamil(audio_file_path, audio_input_type)
                                st.write("Extracted Audio Text: ","\n", transcription)
                       
                except Exception as e:
                    st.write("Exception is ", e)
                    st.write("Upload a mp4 file")
            elif video_service_type == "Add Subtitles": 
                language = st.selectbox("Choose transcription language", ("English", "Tamil"))
                if 'clicked' not in st.session_state: 
                    st.session_state.clicked = {7:False} 
                else:
                    st.session_state.clicked = {7:True}  
                try:
                    # if video_input_type == "Insert Video URL":
                    #     st_player("https://youtu.be/CmSKVW1v0xM")
                    #elif video_input_type == "Local Video Upload":
                    video_uploaded_file = st.file_uploader("Upload file", type=["mp4"], key="video_file_uploader_obj3") 
                    if video_uploaded_file is not None:             
                        st.session_state.clicked[7] = st.button("Add Subtitles", on_click=utils.clicked, args=[7]) 
                        if st.session_state.clicked[7]:
                            if video_uploaded_file is not None:
                                st.write("Play Original Video")
                                st.video(video_uploaded_file)
                                vfpath = utils.save_audio_file(video_uploaded_file,video_input_type)
                                subttitled_video_path = video_services.add_subtitiles(vfpath,language)
                                st.video(subttitled_video_path)
                except Exception as e:
                    st.write("Exception is ", e)
                    st.write("Upload a mp4 file")
                            
            elif video_service_type == "Video Translate":
                sr_language = st.selectbox("Choose source language", ("English", "Tamil"),key="source3") 
                tr_language = st.selectbox("Choose target language", ("English", "Tamil"),key="target3")
                if 'clicked' not in st.session_state: 
                    st.session_state.clicked = {6:False} 
                else:
                    st.session_state.clicked = {6:True}
                try:
                    video_uploaded_file = st.file_uploader("Upload file", type=["mp4"], key="video_file_uploader_obj2") 
                    if video_uploaded_file is not None: 
                        st.write("Original video")
                        st.video(video_uploaded_file)
                        #vfpath = utils.save_audio_file(video_uploaded_file,video_input_type) 
                        vfpath = utils.save_video_file(video_uploaded_file) 
                        originalfilename = vfpath.split("\\")[-1].split(".")[0]
                        originalfilename = utils.remove_non_alphanumeric(originalfilename)
                                     
                        st.session_state.clicked[6] = st.button("Translate Video", on_click=utils.clicked, args=[6]) 
                        if st.session_state.clicked[6]:  
                            if sr_language == "English" :                           
                                audio_destination_path = speech_translation_object.speech_translate(video_uploaded_file, video_input_type, sr_language, tr_language)                        
                            elif sr_language == "Tamil":
                                t1 = datetime.datetime.now()
                                audio_file_path = video_services.extract_audio(vfpath, originalfilename) 
                                audio_file = open(audio_file_path, "rb")
                                st.write("Play Extracted Audio")
                                utils.play_audio_fn(audio_file)
                                audio_destination_path = video_services.video_translate(audio_file_path, originalfilename,sr_language, tr_language)
                                t2= datetime.datetime.now()
                                st.write("time taken: ", t2-t1)     
                            st.write("Play Translated Audio")  
                            audio2 = open(audio_destination_path, 'rb')
                            audio_bytes = audio2.read()                        
                            st.audio(audio_bytes, format = "audio/mp3") 
                            #video_destination_path = utils.save_video_file(video_uploaded_file)
                            final_video = video_services.add_translation(vfpath, audio_destination_path)
                            st.video(final_video)
                                
                except Exception as e:
                    st.write("Exception is ", e)
                    st.write("Enter an audio file or record audio")

       

    if service_request == "Speech Recognition":
        language = st.selectbox("Choose transcription language", ("English", "Tamil"))
        if 'clicked' not in st.session_state: 
            st.session_state.clicked = {1:False} 
        else:
            st.session_state.clicked = {1:True}        
        try:
            if audio_input_type == "AudioFile Upload":
                audio_uploaded_file = st.file_uploader("Upload file", type=["mp3","wav","ogg"], key="audio_file_uploader_obj1")
                if audio_uploaded_file is not None:
                    st.write("Play original audio")    
                    utils.play_audio_fn(audio_uploaded_file) 
            elif audio_input_type == "Record Audio":
                audio_bytes = audio_recorder()
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
            st.session_state.clicked = {1:False}
            st.session_state.clicked[1] = st.button("Transcribe Audio", on_click=utils.clicked, args=[1]) 
            if st.session_state.clicked[1]:
                if audio_input_type == "AudioFile Upload": 
                    vfpath= utils.save_audio_file(audio_uploaded_file, audio_input_type) 
                    originalfilename = audio_uploaded_file.name
                    extracted_audio_path = video_services.extract_audio(vfpath, originalfilename)
                elif audio_input_type == "Extracted Audio":
                    extracted_audio_path = utils.save_audio_file(audio_bytes, audio_input_type)
                transcription = video_services.video_transcribe(extracted_audio_path, originalfilename,language, audio_input_type="Extracted Audio")
                # if language == "English": 
                #     if audio_input_type == "AudioFile Upload":             
                #         transcription = speech_translation_object.transcribe_english(audio_uploaded_file, audio_input_type)                        
                #     elif audio_input_type == "Record Audio":
                #         transcription = speech_translation_object.transcribe_english(audio_bytes, audio_input_type)                     
                # elif language == "Tamil":
                #     if audio_input_type == "AudioFile Upload":             
                #         transcription = speech_translation_object.transcribe_tamil(audio_uploaded_file, audio_input_type)                        
                #     elif audio_input_type == "Record Audio":
                #         transcription = speech_translation_object.transcribe_tamil(audio_bytes, audio_input_type)
                st.write("Transcripted Text: ",transcription)
        except Exception as e:
            st.write("Exception is ", e)
            st.write("Enter an audio file or record audio")

    
    if service_request == "Text-to-Speech":
        language = st.selectbox("Choose transcription language", ("English", "Tamil"))
        if 'clicked' not in st.session_state: 
            st.session_state.clicked = {2:False} 
        else:
            st.session_state.clicked = {2:True}
        try:
            if text_input_type == "DocumentFile Upload":   
                try:             
                    document_uploaded_file = st.file_uploader("Upload document file", type=["txt", "docx", "pdf"], key="document_file_uploader_obj1")
                    if document_uploaded_file is not None:            
                        data = utils.process_document_file_upload(document_uploaded_file, language)
                        file_details = {"Filename":document_uploaded_file.name,"FileType":document_uploaded_file.type,"FileSize":document_uploaded_file.size}
                        st.session_state.clicked = {2:False}
                except:
                    st.write("Enter a document file")
                finally:
                    st.session_state.clicked = {2:False}         
            if text_input_type == "Input Text":
                try:
                    input_text = st.text_area("Input text to be processed")
                    if input_text!="":
                        data = input_text
                    else:
                        st.write("Please enter some text")
                except:
                    st.write("Enter text")
                finally:
                    st.session_state.clicked = {2:False}
            st.session_state.clicked[2] = st.button("Convert to Speech", on_click=utils.clicked, args=[2]) 
            if st.session_state.clicked[2]:
                audio_destination_path = speech_translation_object.reverse_transcription(data, language)
                st.write("Play generated audio")
                audio_file = open(audio_destination_path, 'rb')
                utils.play_audio_fn(audio_file)                         
        except Exception as e:
            st.write("Enter text or upload doc")
               
    if service_request == "Text Translation":
        sr_language = st.selectbox("Choose source language", ("English", "Tamil"),key="source1") 
        tr_language = st.selectbox("Choose target language", ("English", "Tamil"),key="target1")
        if 'clicked' not in st.session_state: 
            st.session_state.clicked = {3:False} 
        else:
            st.session_state.clicked = {3:True}
        try:
            if text_input_type == "DocumentFile Upload":  
                try:             
                   document_uploaded_file = st.file_uploader("Upload document file", type=["txt", "docx", "pdf"], key="document_file_uploader_obj2")
                   print(document_uploaded_file)
                   if document_uploaded_file is not None:            
                        data = utils.process_document_file_upload(document_uploaded_file, sr_language)
                except:
                    st.write("Enter a document file")
                finally:
                    st.session_state.clicked = {3:False}
            if text_input_type == "Input Text":
                try:
                    input_text = st.text_area("Input text to be processed")                    
                    if input_text!="":
                        data = input_text
                    else:
                        st.write("Please enter some text")
                except:
                    st.write("Enter text")
                finally:
                    st.session_state.clicked = {3:False}
            st.session_state.clicked[3] = st.button("Translate", on_click=utils.clicked, args=[3])
            if st.session_state.clicked[3]:
                translation = speech_translation_object.translation(data, sr_language, tr_language)
                st.write("Translated Text: ",translation)      
        except:
            st.write("Enter text or upload doc")
 

    if service_request == "Speech Translation":
        sr_language = st.selectbox("Choose source language", ("English", "Tamil"),key="source2") 
        tr_language = st.selectbox("Choose target language", ("English", "Tamil"),key="target2")
        if 'clicked' not in st.session_state:
            st.session_state.clicked = {4:False}
        try:
            if audio_input_type == "AudioFile Upload":
                audio_uploaded_file = st.file_uploader("Upload file", type=["mp3","wav","ogg"], key="audio_file_uploader_obj2")
                if audio_uploaded_file is not None:
                    st.write("Play original audio")    
                    utils.play_audio_fn(audio_uploaded_file) 
            elif audio_input_type == "Record Audio":
                audio_bytes = audio_recorder()
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
            st.session_state.clicked = {4:False}
            st.session_state.clicked[4] = st.button("Translate Speech", on_click=utils.clicked, args=[4]) 
            if st.session_state.clicked[4]:
                if audio_input_type == "AudioFile Upload":             
                    audio_destination_path = speech_translation_object.speech_translate(audio_uploaded_file, audio_input_type, sr_language, tr_language)                        
                elif audio_input_type == "Record Audio":
                    audio_destination_path = speech_translation_object.speech_translate(audio_bytes, audio_input_type, sr_language, tr_language)                    
                st.write("Play Translated Audio")  
                audio2 = open(audio_destination_path, 'rb')
                audio_bytes = audio2.read()
                st.audio(audio_bytes, format = "audio/mp3") 
        except Exception as e:
            st.write("Exception is ", e)
            st.write("Enter an audio file or record audio")


      

if __name__ == '__main__':
	main()