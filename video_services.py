from moviepy.editor import *
from datetime import timedelta
import streamlit as st
import os
import glob
import tempfile
import srt

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import moviepy.video.fx.all as vfx
from app import speech_translation_object
from utils import highest_multiple_of_chunksize


def time_to_seconds(time_obj):
    try:
        t1 = time_obj.hours
    except:
        t1 = 0
    try:
        t2 = time_obj.minutes
    except:
        t2 = 0
    try:
        t3 = time_obj.seconds
    except:
        t3 = 0
    try:
        t4 = time_obj.milliseconds
    except:
        t4 = 0
    totalseconds = t1 * 3600 + t2 * 60 + t3 + t4 / 1000    
    return totalseconds



def create_subtitle_clips(subtitles, videosize, language, debug = False):
    subtitle_clips = []
    #for subtitle in subtitles:
    for subtitle in srt.parse(subtitles):
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time
        video_width, video_height = videosize
        if language == "English":
            text_clip = TextClip(subtitle.content, fontsize=24, font="Arial", color="yellow", bg_color = 'black',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
        elif language == "Tamil":
            text_clip = TextClip(subtitle.content, fontsize=24, font="Nirmala-UI", color="black", bg_color = 'white',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height* 2 / 5 
        text_position = (subtitle_x_position, subtitle_y_position)                    
        subtitle_clips.append(text_clip.set_position(text_position))
    return subtitle_clips

def extract_audio(video_path, originalfilename):
    audio = AudioFileClip(video_path)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_audiofilename = temp_file.name.split("\\")[-1] 
    if originalfilename.endswith(".wav"):
        temp_file_name = temp_audiofilename.split(".")[0] + "_"+ originalfilename 
    else:
        temp_file_name = temp_audiofilename.split(".")[0] + "_"+ originalfilename +"_"+ ".wav"
    extracted_audio_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data', 'ExtractedAudio',temp_file_name)
    audio.write_audiofile(extracted_audio_path)
    return extracted_audio_path


def with_movie_py(video_path: str, totaldur: float, chunksize: int) -> list[int]:
    """
    Link: https://pypi.org/project/moviepy/
    Parameters:
        video (str): Video path
        totaldur (int): total duration of video
    Returns:
        List of timestamps in ms
    """
    if video_path.endswith(".mp4"):
        vid = VideoFileClip(video_path)
    elif video_path.endswith(".wav"):
        vid = AudioFileClip(video_path)
    # timestamps = [
    #     int(tstamp * 1000) for tstamp, frame in vid.iter_frames(with_times=True)
        
    # ]
    highest_chunk_sec = highest_multiple_of_chunksize(totaldur, chunksize)
    #getting timestamps for every 5 sec intervals
    timestamps =  [k for k in range(0,highest_chunk_sec+1,chunksize)] + [totaldur]    
    return timestamps

def create_srtlines(frameno, clip_start, clip_end, bigclip,srtFilename,language): 
    startTime = str(0)+ str(timedelta(seconds=(clip_start)))+',000'
    endTime = str(0)+ str((timedelta(seconds=(clip_end))))+',000'
    frameclip = bigclip.subclip(clip_start,clip_end)
    originalfilename  = srtFilename.split(".")[0].split("\\")[-1]
    tempvideoclipfilename = "tempvideoclipfile" + "_" + originalfilename +"_" + ".mp4"
    video_file_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedClips',tempvideoclipfilename)
    frameclip.write_videofile(video_file_path)
    extracted_audio_path = extract_audio(video_file_path,originalfilename)
    audio_input_type = "Extracted Audio"
    if language == "English":
        text = speech_translation_object.transcribe_english(extracted_audio_path , audio_input_type) 
    elif language == "Tamil":
        text = speech_translation_object.transcribe_tamil(extracted_audio_path , audio_input_type) 
    new_endTime = str(endTime).split(".")[0]
    segment = f"{frameno}\n{startTime} --> {new_endTime}\n{text[1:] if text[0] is '' else text}\n\n"
    with open(srtFilename, 'a', encoding='utf-8') as srtFile:
        srtFile.write(segment)
    directory_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','ExtractedAudio') # Replace with the actual path
    pattern = "*_" +originalfilename +"_" +".wav" # Example pattern 
    matching_files = glob.glob(os.path.join(directory_path, pattern))
    for file in matching_files:
        try:
            os.remove(file)
            print(f"Removed file: {file}")  # Optional confirmation message
        except OSError as error:
            print(f"Error removing file {file}: {error}")
    
    
def create_srtfile(video_path, language):    
    bigclip = VideoFileClip(video_path)
    totaldur = bigclip.duration
    movie_py_timestamps = with_movie_py(video_path, totaldur, chunksize=5)
    VIDEO_FILENAME = video_path.split("\\")[-1].split(".")[0]
    srtFilename = os.path.join(os.path.sep, os.getcwd(),'temp_data','SrtFiles',f"{VIDEO_FILENAME}.srt")
    clip_start = 0
    for frameno in range(1, len(movie_py_timestamps)): 
        clip_end = movie_py_timestamps[frameno]
        if clip_end >= int(totaldur):
            clip_end = totaldur
            create_srtlines(frameno, clip_start, clip_end, bigclip, srtFilename,language)
            break
        else:
            create_srtlines(frameno, clip_start, clip_end, bigclip,srtFilename,language) 
        clip_start = clip_end
    return srtFilename   


def add_subtitiles(video_path, language):
    srtFilename = create_srtfile(video_path, language)
    # Load video and SRT file
    video = VideoFileClip(video_path)
    with open(srtFilename, "r",encoding = "utf-8") as f:
        subtitles = f.read()    
    video_filename= video_path.split("\\")[-1].split(".")[0]    
    output_video_file = os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedVideo', video_filename +'_subtitled'+".mp4")  
    with st.spinner('Please wait. Adding subtitles...'): 
        # Create subtitle clips
        subtitle_clips = create_subtitle_clips(subtitles,video.size, language)
        # Add subtitles to the video
        final_video = CompositeVideoClip([video] + subtitle_clips)
        # Write output video file
        final_video.write_videofile(output_video_file)
    return output_video_file


def add_translation(video_path,audio_destination_path):  
    with st.spinner('Please wait. Translating...'):  
        video_clip = VideoFileClip(video_path)
        video_dur = video_clip.duration
        video_filename= video_path.split("\\")[-1].split(".")[0] 
        output_video_file =  os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedVideo', video_filename +'_translated'+".mp4")
        audio_clip = AudioFileClip(audio_destination_path)        
        if audio_clip.duration > video_dur:
            new_audio_clip = audio_clip.set_duration(video_dur)
            final_clip = video_clip.set_audio(new_audio_clip)
        elif audio_clip.duration < video_dur:
            final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_video_file)
    return output_video_file

def get_chunk_timestamps(video_path, chunksize):
    if video_path.endswith(".mp4"):
        video_clip = VideoFileClip(video_path)
    elif video_path.endswith(".wav"):
        video_clip = AudioFileClip(video_path)
    video_dur = video_clip.duration
    #if video_dur >30:
    chunked_timestamps = with_movie_py(video_path, video_dur, chunksize=chunksize)
    return chunked_timestamps

def create_audio_chunks(audio_path,originalfilename, language):
    if audio_path.endswith(".mp4"):
        bigclip = VideoFileClip(audio_path)
        input_type = "video"
    elif audio_path.endswith(".wav"):
        bigclip = AudioFileClip(audio_path)
        input_type = "audio"

    if language == "English":
        chunksize = 30
    elif language == "Tamil":
        chunksize = 15

    chunked_timestamps = get_chunk_timestamps(audio_path, chunksize= chunksize)
    subclip_paths =[]
    for k in range(len(chunked_timestamps)-1):
        clip_start = chunked_timestamps[k]
        clip_end = chunked_timestamps[k+1]
        subclip_path = create_video_subclips(clip_start, clip_end, bigclip,originalfilename, input_type)
        subclip_paths.append(subclip_path)
    return subclip_paths


def create_video_subclips(clip_start, clip_end, bigclip,originalfilename, input_type):
    startTime = str(0)+ str(timedelta(seconds=(clip_start)))+',000'
    endTime = str(0)+ str((timedelta(seconds=(clip_end))))+',000'
    frameclip = bigclip.subclip(clip_start,clip_end)
    if input_type == "video":
        tempvideoclipfilename = originalfilename +"_" + str(clip_start)+"_"+ str(clip_end) + "_"+".mp4"
        video_file_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedClips',tempvideoclipfilename)
        frameclip.write_videofile(video_file_path)
    elif input_type == "audio":
        tempvideoclipfilename = originalfilename +"_" + str(clip_start) + "_" + str(clip_end) + "_"+".wav"
        video_file_path = os.path.join(os.path.sep, os.getcwd(), 'temp_data','SavedClips',tempvideoclipfilename)
        frameclip.write_audiofile(video_file_path)
    return video_file_path

def translate_srtfile(vfpath, sr_language, tr_language):
    srtFilename = create_srtfile(vfpath, sr_language)
    with open(srtFilename, "r",encoding = "utf-8") as f:
        subtitles = f.read()    
    extracted_text = ".".join([subtitle.content for subtitle in srt.parse(subtitles)])
    translated_text = speech_translation_object.translation(extracted_text, sr_language, tr_language)
    audio_destination_path = speech_translation_object.reverse_transcription(translated_text, tr_language)
    return audio_destination_path   


# def get_duration_wave(file_path):
#    with wave.open(file_path, 'r') as audio_file:
#       frame_rate = audio_file.getframerate()
#       n_frames = audio_file.getnframes()
#       duration = n_frames / float(frame_rate)
#       return duration
   
def video_transcribe(audio_file_path, originalfilename,language, audio_input_type):
    sublclip_paths = create_audio_chunks(audio_file_path,originalfilename, language)
    transcription_subclips =[]
    for subclip_path in sublclip_paths:
        if language == "English":                     
            transcription_subclip = speech_translation_object.transcribe_english(subclip_path, audio_input_type) 
    
        elif language == "Tamil":
            transcription_subclip = speech_translation_object.transcribe_tamil(subclip_path, audio_input_type)
            st.write("transcription_subclip:", transcription_subclip)
            #print("transcription subclip", transcription_subclip)
        transcription_subclips.append(transcription_subclip)
    #transcription = " ".join(transcription_subclips)
    return transcription_subclips

# def video_translate(audio_file_path, originalfilename,sr_language, tr_language):
#     transcription_subclips = video_transcribe(audio_file_path, originalfilename,sr_language, audio_input_type= "Extracted Audio")
#     transcription = " ".join(transcription_subclips)
#     #st.write("transcription: " ,transcription)
#     translation_subclips = []
#     for transcription_subclip in transcription_subclips:
#         translation_subclip = speech_translation_object.translation(transcription_subclip, sr_language, tr_language)
#         st.write("translation_subclip:", translation_subclip)
#         translation_subclips.append(translation_subclip)
#     translation = " ".join(translation_subclips)
#     st.write("translations: " ,translation)
#     audio_destination_path = speech_translation_object.reverse_transcription(translation, tr_language)
#     return audio_destination_path
        
def video_translate(audio_file_path, originalfilename,sr_language, tr_language):
    transcription_subclips = video_transcribe(audio_file_path, originalfilename,sr_language, audio_input_type= "Extracted Audio")
    transcription = " ".join(transcription_subclips)
    st.write("no punt", transcription)
    # from deepmultilingualpunctuation import PunctuationModel
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # punct_model = PunctuationModel(model="oliverguhr/fullstop-punctuation-multilingual-sonar-base").to(device)
   
    #punct_transcription = punct_model.restore_punctuation(transcription)
    # #punct_transcription = "முன்னாள் முதலமைச்சர் ஓ பன்னீர்செல்வம் என் டி ஏ கூட்டணியில் இருப்பதால்தான் பிரதமர் நரேந்திர மோடியை சந்தித்தார், என பாஜக மூத்த தலைவர் ஹெச் ராஜா தெரிவித்துள்ளார். திருச்சி பால்பண்ணையில் பாஜக நிர்வாகிகள்- மாவட்ட தலைவர்கள் கூட்டம் தனியார் திருமண மண்டபத்தில் நடைபெற்றது. இதில் பாஜக மாநில தலைவர் அண்ணாமலை, பாஜக மூத்த தலைவர்கள் பொன் ராதாகிருஷ்ணன், எச் ராஜா நைனார், நாகேந்திரன், மேலிடப்பொறுப்பாளர் சுதாகர் ரெட்டி உள்ளிட்டோர் கலந்து கொண்டனர். கூட்டத்தில் பேசிய பாஜக மாநில தலைவர் அண்ணாமலை 2024ஆம் ஆண்டின் முதல் கூட்டம் தமிழ்நாட்டில்தான் நடக்க வேண்டும் என்ற பிரதமர் மோடியின் விருப்பம் நிறைவேறி இருப்பதாக கூறினார். தமிழ்நாட்டிற்கு மோடி வந்ததால் உற்சாகம் அதிகமாகி இருப்பதாக ஏச் ராஜா கூறினார். அதிகமா இருக்கு. இருந்தாலும் ஒரு முதலமைச்சர் பேசும்போது நாம அதிகம் கூட கொஞ்சம் இந்த அடைக்கி வாசிச்சிருக்கலாம். சிறுவர்களோடு உற்கட்சியின் உற்சாகத்தை கட்டுப்படுத்துவது கஷ்டம்தான். சுபமுகூர்த்தத்தில் முன்னாள் அமைச்சர் பொன்முடியை உள்ளே அனுப்பி வைத்ததாகவும், அதன் பின்னர் ஒவ்வொரு அமைச்சராக சிறை செல்வார்கள், என ஹெச் ராஜா கூறினார்."
    # st.write("transcription: " ,punct_transcription)
    #transcription_subclips = punct_transcription.strip().split(".")
    transcription_subclips = speech_translation_object.add_punctuations(transcription)
    translation_subclips = []
    for transcription_subclip in transcription_subclips:
        if transcription_subclip!="":
            translation_subclip = speech_translation_object.translation(transcription_subclip, sr_language, tr_language)
            st.write("punt transcription_subclip:", transcription_subclip)
            st.write("translation_subclip:", translation_subclip)
            translation_subclips.append(translation_subclip) 
    translation = ".".join(translation_subclips)

    #translation = speech_translation_object.translation(punct_transcription, sr_language, tr_language)
    

    # transcription = "முன்னாள் முதலமைச்சர் ஓ பன்னீர்செல்வம், என் டி ஏ கூட்டணியில் இருப்பதால்தான் பிரதமர் நரேந்திர மோடியை சந்தித்தார் என, பாஜக மூத்த தலைவர் ஹெச் ராஜா தெரிவித்துள்ளார்.திருச்சி பால்பண்ணையில், பாஜக நிர்வாகிகள் மாவட்ட தலைவர்கள் கூட்டம் தனியார் திருமண மண்டபத்தில் நடைபெற்றது .இதில் பாஜக மாநில தலைவர் அண்ணாமலை ,பாஜக மூத்த தலைவர்கள் பொன் ராதாகிருஷ்ணன், எச் ராஜா, நைனார் நாகேந்திரன் ,மேலிடப்பொறுப்பாளர் சுதாகர் ரெட்டி உள்ளிட்டோர் கலந்து கொண்டனர். கூட்டத்தில் பேசிய பாஜக மாநில தலைவர் அண்ணாமலை ,2024ஆம் ஆண்டின் முதல் கூட்டம் தமிழ்நாட்டில்தான் நடக்க வேண்டும் என்ற பிரதமர் மோடியின் விருப்பம் நிறைவேறி இருப்பதாக கூறினார். தமிழ்நாட்டிற்கு மோடி வந்ததால் உற்சாகம் அதிகமாகி இருப்பதாக ஏச் ராஜா கூறினார்.சுபமுகூர்த்தத்தில் முன்னாள் அமைச்சர் பொன்முடியை உள்ளே அனுப்பி வைத்ததாகவும், அதன் பின்னர் ஒவ்வொரு அமைச்சராக சிறை செல்வார்கள் என ஹெச் ராஜா கூறினார்."
    # translation = speech_translation_object.translation(transcription, sr_language, tr_language)
    st.write("translations: " ,translation)
    audio_destination_path = speech_translation_object.reverse_transcription(translation, tr_language)
    return audio_destination_path




            



