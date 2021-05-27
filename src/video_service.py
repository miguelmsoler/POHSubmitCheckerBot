import speech_recognition as sr
from moviepy.editor import AudioFileClip
from io import BytesIO
import numpy as np
import ffmpeg

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
            if text == 'SERVICE_DOWN':
                text = 'NO_SPEECH_DETECTED'
        except sr.UnknownValueError:
            text = 'NO_SPEECH_DETECTED'
        except sr.RequestError:
            text = 'SERVICE_DOWN'
        return text

class VideoService:

    def __init__(self, bytes_io, ext, update=None, context=None):
        self.bytes_io = bytes_io
        self.ext = ext
        self.text = ''
        if update:
            self.message = update.message
            self.bot = context.bot

    def process(self):
        filename = 'temp.' + self.ext
        with open(filename, 'wb') as outfile:
            outfile.write(self.bytes_io.getbuffer())
            AudioFileClip(filename).write_audiofile('temp.wav')
            self.text = recognize('temp.wav')

        # get dimensions
        probe = ffmpeg.probe(filename)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
        self.width = video_streams[0]['width']
        self.height = video_streams[0]['height']
    
    def convert(self, scale_width):
        # self.message.reply_text('🔥 Testing video conversion 🔥')
        stream = ffmpeg.input('temp.' + self.ext)
        audio_stream = stream.audio
        if scale_width:
            stream = ffmpeg.filter(stream, 'scale', 640, -1)
        else:
            stream = ffmpeg.filter(stream, 'scale', -1, 640)
        out_stream = ffmpeg.concat(stream, audio_stream, v=1, a=1)
        output_filename = 'temp.converted.' + self.ext
        out_stream = ffmpeg.output(out_stream, output_filename)
        out_stream = ffmpeg.overwrite_output(out_stream)
        ffmpeg.run(out_stream)
        self.bot.send_video(chat_id=self.message.chat_id, video=open(output_filename, 'rb'), supports_streaming=True)
        # self.message.reply_text('🔥 Testing done 🔥')


if __name__ == "__main__":
    # filename = "zoom-0.wav"
    # print(recognize(filename))

    # with open('/home/miguelmsoler/Descargas/zoom-0.mp4', 'rb') as fh:
    #     buf = BytesIO(fh.read())
    #     print(recognize_from_video(buf, 'mp4'))

    # stream = ffmpeg.input('temp.mp4')
    # audio_stream = stream.audio
    # stream = ffmpeg.filter(stream, 'scale', 360, -1)
    # stream = ffmpeg.concat(stream, audio_stream, v=1, a=1)
    # stream = ffmpeg.output(stream, 'temp.converted.mp4')
    # stream = ffmpeg.overwrite_output(stream)
    # ffmpeg.run(stream)

    with open('temp.mp4', 'rb') as fh:
        buf = BytesIO(fh.read())
        video_service = VideoService(buf, 'mp4')
        video_service.process()