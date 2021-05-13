#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is licensed under the MIT License.

"""
A Bot that checks images and videos for submitting as part of a Proof Of Humanity profile.

Usage:
Start the bot and send your image and video files. The bot will check some of the requirements (file size, resolution, detectable face, etc.)
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from io import BytesIO
import cv2
import numpy as np
from decouple import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set this env variable in a .env file
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')

face_cascade = cv2.CascadeClassifier('face_detector.xml')

# Handlers
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! This is bot helps you to check that your image and video files meet the requirements for submiting Proof Of Humanity profiles.')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Just send an image or video and I\'ll check it for you')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text('Just send an image or video and I\'ll check it for you')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def process_image_from_message(update, context):
  message = update.message

  message.reply_text('🔥 Please wait, I\'m analyzing your image 🔥')

  data = context.bot.get_file(update.message.photo[-1].file_id)
  f =  BytesIO(data.download_as_bytearray())
  f.seek(0)
  img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
  cv2_img = cv2.imdecode(img_array, 0)

  # Detect faces
  faces = face_cascade.detectMultiScale(cv2_img, 1.1, 4)
  faceOk = '✔️' if len(faces) == 1 else '❌'

  size = message.photo[-1]['file_size']
  width = message.photo[-1]['width']
  height = message.photo[-1]['height']

  sizeOk = '✔️' if size <= 2097152 else '❌'

  message.reply_text(faceOk + ' I can detect ' + str(len(faces)) + ' face(s) in the picture. Remember that your face should not be covered. Please, check the instructions in the submit form.')
  message.reply_text(sizeOk + ' Image Size: ' + str(size) + ' bytes (Max: 2097152 bytes)')

  message.reply_text('🔥 WARNING 🔥 Reported image file sizes are lower than real due to Telegram processing the files. Please, submit JPG files to minimize this error.')

def process_video_from_message(update, context):
    message = update.message

    message.reply_text('🔥 Please wait, I\'m analyzing your video 🔥')

    size = message.video.file_size
    file_type = message.video.mime_type.split('/')[1]
    width = message.video.width
    height = message.video.height

    sizeOk = '✔️' if size <= 7340032 else '❌'
    file_typeOk = '✔️' if file_type == 'mp4' or file_type == 'webm' else '❌'
    widthOk = '✔️' if width >= 360 else '❌'
    heightOk = '✔️' if height >= 360 else '❌'

    message.reply_text(sizeOk + ' Video Size: ' + str(size) + ' bytes (Max: 7340032 bytes)')
    message.reply_text(widthOk + ' Width: ' + str(width) + ' pixels (Min: 360 pixels)')
    message.reply_text(heightOk + ' Height: ' + str(height) + ' pixels (Min: 360 pixels)')

def not_supported(update, context):
    update.message.reply_text('You can only send text, images and videos to this Bot (i.e.: animated GIFs are not videos).')

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

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

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