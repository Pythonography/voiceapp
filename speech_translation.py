import streamlit as st
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from gtts import gTTS
import torch
from deepmultilingualpunctuation import PunctuationModel
import tempfile
import utils


class translate_speech:
    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_english,  self.processor_english = self.model_load_english()
        self.model_tamil, self.processor_tamil = self.model_load_tamil()
        self.model, self.tokenizer = self.translate_model_load()
        self.punct_model = self.punct_model_load()
    
    @st.cache_resource(show_spinner="Please wait. Loading...",hash_funcs={"__speech_translation__.translate_speech": lambda x: hash(x.model_english, x.processor_english)})
    def model_load_english(_self,):
        model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny.en").to(_self.device)
        processor = WhisperProcessor.from_pretrained("openai/whisper-tiny.en")     
        return model, processor
    
    @st.cache_resource(show_spinner="Please wait. Loading...",hash_funcs={"__speech_translation__.translate_speech": lambda x: hash(x.model_tamil, x.processor_tamil)})
    def model_load_tamil(_self,):
        model = WhisperForConditionalGeneration.from_pretrained("vasista22/whisper-tamil-medium").to(_self.device)
        processor = WhisperProcessor.from_pretrained("vasista22/whisper-tamil-medium")
        return model, processor
    
     
    @st.cache_resource(show_spinner="Please wait. Loading...",hash_funcs={"__speech_translation__.translate_speech": lambda x: hash(x.model, x.tokenizer)})
    def translate_model_load(_self,):
        model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt").to(_self.device)
        tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
        return model, tokenizer
    
    @st.cache_resource(show_spinner="Please wait. Loading...",hash_funcs={"__speech_translation__.translate_speech": lambda x: hash(x.punct_model)})
    def punct_model_load(_self,):
        print("punct model load device", _self.device)
        punct_model = PunctuationModel(model="oliverguhr/fullstop-punctuation-multilingual-sonar-base")
        return punct_model
    
    def transcribe_english(self,audio, audio_input_type):
        if audio_input_type == "Extracted Audio":
            destination_path = audio
        elif audio_input_type == "Local Video Upload":
            destination_path = utils.save_video_file(audio)
        else:
            destination_path = utils.save_audio_file(audio, audio_input_type) 

        with st.spinner('Please wait. Processing...'):            
            speech, rate = librosa.load(destination_path,sr=16000) 
            input_features = self.processor_english(speech, sampling_rate=16000, return_tensors="pt").input_features.to(self.device) 
            # generate token ids
            predicted_ids = self.model_english.generate(input_features).to(self.device)
            # decode token ids to text
            transcription = self.processor_english.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription[0]

    def transcribe_tamil(self,audio, audio_input_type):
        print("device new", self.device)
        if audio_input_type == "Extracted Audio":
            destination_path = audio
        elif audio_input_type == "Local Video Upload":
            destination_path = utils.save_video_file(audio)
        else:
            destination_path = utils.save_audio_file(audio, audio_input_type) 
        with st.spinner('Please wait. Processing...'):
            forced_decoder_ids = self.processor_tamil.get_decoder_prompt_ids(language="tamil", task="transcribe")
            #load any audio file of your choice
            speech, rate = librosa.load(destination_path,sr=16000)
            input_features = self.processor_tamil(speech, sampling_rate=16000, return_tensors="pt").input_features.to(self.device) 
            # generate token ids
            predicted_ids = self.model_tamil.generate(input_features, forced_decoder_ids=forced_decoder_ids).to(self.device)
            # decode token ids to text
            transcription = self.processor_tamil.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        return transcription      

    def add_punctuations(self, data):
        punct_transcription = self.punct_model.restore_punctuation(data)
        st.write("transcription: " ,punct_transcription)
        transcription_subclips = punct_transcription.strip().split(".")        
        return transcription_subclips
        


    def translation(self, data, sr_language, tr_language):
        print("device here is :", self.device)
        st.write("Inside translate")                  
        # translate 
        self.tokenizer.src_lang = utils.language_code_mbart(sr_language)
        with st.spinner('Please wait. Processing...'):  
            encoded_data = self.tokenizer(data, return_tensors="pt").to(self.device)

            generated_tokens = self.model.generate(
                **encoded_data,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[utils.language_code_mbart(tr_language)]
            )
            translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return translated_text[0]
    

    def reverse_transcription(self, data, language): 
        with st.spinner('Please wait. Processing...'): 
            if language == "English":
                lang = "en"
            elif language == "Tamil":
                lang = "ta"
            tts = gTTS(text = data, lang=lang, slow=False)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
                temp_path = temp.name
                tts.save(temp_path)
        audio_destination_path = temp_path
        st.write("Audio File created")
        return audio_destination_path


    def speech_translate(self, audio_file, audio_input_type, sr_language, tr_language):
        with st.spinner('Please wait. Processing...'):
            if sr_language == "English":
                transcription = self.transcribe_english(audio_file, audio_input_type)
            elif sr_language == "Tamil":
                transcription = self.transcribe_tamil(audio_file, audio_input_type)
            translated_text = self.translation(transcription, sr_language, tr_language)
            audio_destination_path = self.reverse_transcription(translated_text, tr_language)
        st.text("Audio file translated")
        return audio_destination_path