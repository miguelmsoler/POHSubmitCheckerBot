#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is licensed under the MIT License.

"""
A Telegram Bot that checks images and videos for submitting as part of a Proof Of Humanity profile.

Usage:
Start the bot and send your image and video files. The bot will check some of the requirements (file size, resolution, detectable face, etc.)
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from io import BytesIO
import cv2
import numpy as np
from decouple import config
from video_service import VideoService
from poh_profile_service import POHProfileService
import re
import traceback
from PIL import Image

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set this env variable in a .env file
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
UBI_ADDRESS = config('UBI_ADDRESS')
BTC_ADDRESS = config('BTC_ADDRESS')

face_cascade = cv2.CascadeClassifier('face_detector.xml')

# A regular expression for poh profile ids
p = re.compile('0x\w{40}')

# Handlers
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! This is bot helps you checking that your image and video files meet the requirements for a Proof Of Humanity profile.')
    update.message.reply_text('Please, type /help for instructions.')
    similar_faces(update, context)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Upload an image or a video and I will analyze it.')
    update.message.reply_text('You can also paste a link to a POH profile or and address of the wallet that corresponds to it.')
    update.message.reply_text('Finally, if your video does not meet the POH criteria I will send you a compressed version whenever it is possible.')
    update.message.reply_text('You just have to download that video from Telegram and use it.')


def text(update, context):
    m = p.search(update.message.text)
    if m:
        profile_id = m.group()
        disclaimer(update, context)
        update.message.reply_text('🔥 Processing profile %s... 🔥' % profile_id)
        poh_profile_service = POHProfileService(profile_id, update, context)
        poh_profile_service.process()
        update.message.reply_text('🔥 ...done. 🔥')
        photo = poh_profile_service.photo
        context.bot.send_photo(update.message.chat_id, photo=photo.data)
        try:
            process_image_from_profile(photo.data, photo.url, update, context)
        except:
            traceback.print_exc()
        video = poh_profile_service.video
        try:
            process_video(video.data, video.url, update, context)
        except:
            traceback.print_exc()
    else:
        help(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def process_image_from_message(update, context):
  message = update.message

  message.reply_text('🔥 Please wait, I\'m analyzing your image 🔥')

  
  data = context.bot.get_file(update.message.photo[-1].file_id)
  if data.file_path.split('/')[-1].split('.')[-1] != 'jpg':
      message.reply_text('⚠️ Reported image file sizes are lower than real because Telegram compress them. Please, submit JPG files to minimize this effect.')
  else:
      message.reply_text('Please remember that you should upload jpg files to this bot to get valid results.')

  f =  BytesIO(data.download_as_bytearray())
  f.seek(0)
  img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
  cv2_img = cv2.imdecode(img_array, 0)

  # Detect faces
  faces = face_cascade.detectMultiScale(cv2_img, 1.1, 4)
  faceOk = '✔️' if len(faces) == 1 else '⚠️'

  size = message.photo[-1]['file_size']
  width = message.photo[-1]['width']
  height = message.photo[-1]['height']

  sizeOk = '✔️' if size <= 2097152 else '❌'

  message.reply_text(faceOk + ' I can detect ' + str(len(faces)) + ' face(s) in the picture. Remember that your face should not be covered and that only one face should be seen in the picture. \nPlease, check the instructions in the submit form.')
  message.reply_text(sizeOk + ' Image Size: ' + str(size) + ' bytes (Max: 2097152 bytes)')

  similar_faces(update, context)
  disclaimer(update, context)

def process_image_from_profile(data, url, update, context): 
    message = update.message
    f =  BytesIO(data)
    f.seek(0)
    img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
    cv2_img = cv2.imdecode(img_array, 0)

    if url.split('/')[-1].split('.')[-1] != 'jpg':
      message.reply_text('⚠️ Reported image file sizes are lower than real because Telegram compress them. Please, submit JPG files to minimize this effect.')
    else:
        message.reply_text('Please remember that you should upload jpg files to this bot to get valid results.')

    # Detect faces
    faces = face_cascade.detectMultiScale(cv2_img, 1.1, 4)
    faceOk = '✔️' if len(faces) == 1 else '⚠️'

    img = Image.open(f)
    size = len(data)
    width = img.size[0]
    height = img.size[1]

    sizeOk = '✔️' if size <= 2097152 else '❌'

    message.reply_text(faceOk + ' I can detect ' + str(len(faces)) + ' face(s) in the picture. Remember that your face should not be covered and that only one face should be seen in the picture. \nPlease, check the instructions in the submit form.')
    message.reply_text(sizeOk + ' Image Size: ' + str(size) + ' bytes (Max: 2097152 bytes)')

    message.reply_text('⚠️ Reported image file sizes are lower than real because Telegram compress them. Please, submit JPG files to minimize this effect.')
    similar_faces(update, context)

def process_video_from_message(update, context):
    disclaimer(update, context)
    message = update.message

    size = message.video.file_size
    file_type = message.video.mime_type.split('/')[1]
    width = message.video.width
    height = message.video.height

    sizeOk = '✔️' if size <= 7340032 else '❌'
    file_typeOk = '✔️' if file_type == 'mp4' or file_type == 'webm' else '❌'
    minWidth = 360 if width < height else 640
    minHeight = 360 if width > height else 640
    widthOk = '✔️' if width >= minWidth else '❌'
    heightOk = '✔️' if height >= minHeight else '❌'

    message.reply_text(sizeOk + ' Video Size: ' + str(size) + ' bytes (Max: 7340032 bytes)')
    message.reply_text(widthOk + ' Width: ' + str(width) + ' pixels (Min: ' + str(minWidth) + ' pixels)')
    message.reply_text(heightOk + ' Height: ' + str(height) + ' pixels (Min: ' + str(minHeight) + ' pixels)')

    message.reply_text('🔥  Analyzing speech. Please wait some seconds... 🔥')
    data = context.bot.get_file(update.message.video.file_id)
    f =  BytesIO(data.download_as_bytearray())
    video_service = VideoService(f, file_type, update, context)
    video_service.process()
    text = video_service.text
    if text == 'NO_SPEECH_DETECTED':
        message.reply_text('⚠️ I could not detect any speech')
    elif text == 'SERVICE_DOWN':
        message.reply_text('It seems there is no more free Google speech recognition for today... maybe tomorrow...')
    else:
        message.reply_text('✔️ I can detect speech: "...' + text + '..."')
        print(text)

    # convert only if video is ok and there is room for reducing resolution
    if widthOk == '✔️' and heightOk == '✔️' and width > 360 and height > 360:
        message.reply_text('🔥 Making a compressed version of this video... 🔥')
        if width > height:
            video_service.convert(scale_width=True)
        else:
            video_service.convert(scale_width=False)
        message.reply_text('🔥 ...done 🔥')
        message.reply_text('You can download now this video and use it.')
    similar_faces(update, context)
    contribute(update, context)

def process_video(data, url, update, context):
    message = update.message

    size = len(data)
    file_type = url.split('/')[-1].split('.')[-1]

    f =  BytesIO(data)
    video_service = VideoService(f, file_type, update, context)
    message.reply_text('🔥  Analyzing video. Please wait some seconds... 🔥')
    video_service.process()

    width = video_service.width
    height = video_service.height

    sizeOk = '✔️' if size <= 7340032 else '❌'
    file_typeOk = '✔️' if file_type == 'mp4' or file_type == 'webm' else '❌'
    minWidth = 360 if width < height else 640
    minHeight = 360 if width > height else 640
    widthOk = '✔️' if width >= minWidth else '❌'
    heightOk = '✔️' if height >= minHeight else '❌'

    message.reply_text(sizeOk + ' Video Size: ' + str(size) + ' bytes (Max: 7340032 bytes)')
    message.reply_text(widthOk + ' Width: ' + str(width) + ' pixels (Min: ' + str(minWidth) + ' pixels)')
    message.reply_text(heightOk + ' Height: ' + str(height) + ' pixels (Min: ' + str(minHeight) + ' pixels)')

    text = video_service.text
    if text == 'NO_SPEECH_DETECTED':
        message.reply_text('⚠️ I could not detect any speech')
    elif text == 'SERVICE_DOWN':
        message.reply_text('It seems there is no more free Google speech recognition for today... maybe tomorrow...')
    else:
        message.reply_text('✔️ I can detect speech: "...' + text + '..."')
        print(text)

    # convert only if video is ok and there is room for reducing resolution
    if widthOk == '✔️' and heightOk == '✔️' and width > 360 and height > 360:
        message.reply_text('Making a compressed version of this video...')
        if width > height:
            video_service.convert(scale_width=True)
        else:
            video_service.convert(scale_width=False)
        message.reply_text('...done')
        message.reply_text('You can download now this video and use it.')
    similar_faces(update, context)
    contribute(update, context)

def not_supported(update, context):
    update.message.reply_text('You can only send text, images and videos to this Bot (i.e.: animated GIFs are not videos).')

def disclaimer(update, context):
    update.message.reply_text('DISCLAIMER: You are using this bot at your own risk. This bot is still in beta testing and may not work perfectly.')

def similar_faces(update, context):
    update.message.reply_text('You can check if this profile has been registered before in https://faces.humanity.tools/ by entering your profile address.')

def contribute(update, context):
    update.message.reply_text('PLEASE, SUPPORT THIS BOT')
    update.message.reply_text('This bot is running in a paid server and maintained by myself in my spare time. Your contribution today may help many people to get into POH tomorrow. Please consider making a small donation through UBI, ETH, or BTC to support this work. This message will be removed once the project gets funded for a year. Thank you.')
    update.message.reply_text("Crypto Addresses:\n" \
        "UBI/ETH: " + UBI_ADDRESS + "\nBTC:   " + BTC_ADDRESS)
    

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - process text message
    dp.add_handler(MessageHandler(Filters.text, text))

    dp.add_handler(MessageHandler(Filters.photo, process_image_from_message))
    dp.add_handler(MessageHandler(Filters.video, process_video_from_message))

    # on anything else...
    dp.add_handler(MessageHandler(~(Filters.text | Filters.video | Filters.photo), not_supported))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()