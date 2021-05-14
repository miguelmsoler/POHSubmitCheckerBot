import speech_recognition as sr
from moviepy.editor import AudioFileClip
from io import BytesIO
import numpy as np

# initialize the recognizer
r = sr.Recognizer()

def recognize(bytes_io):
    with sr.AudioFile(bytes_io) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        print('Speech recognition...')
        try:
            text = r.recognize_google(audio_data)
            if text == '':
                text = 'NO_SPEECH_DETECTED'
        except speech_recognition.UnknownValueError:
            text = 'NO_SPEECH_DETECTED'
        except speech_recognition.RequestError:
            text = 'SERVICE_DOWN'
        return text

def recognize_from_video(bytes_io, ext):
    filename = 'temp.' + ext
    with open('temp.' + ext, 'wb') as outfile:
        outfile.write(bytes_io.getbuffer())
        AudioFileClip(filename).write_audiofile('temp.wav')
        return recognize('temp.wav')


if __name__ == "__main__":
    # filename = "zoom-0.wav"
    # print(recognize(filename))

    with open('/home/miguelmsoler/Descargas/zoom-0.mp4', 'rb') as fh:
        buf = BytesIO(fh.read())
        print(recognize_from_video(buf, 'mp4'))

