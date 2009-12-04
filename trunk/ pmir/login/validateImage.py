# -*- coding: utf-8 -*-
from Captcha.Visual import Text, Backgrounds, Distortions, ImageCaptcha
from Captcha import Words
from Captcha.Base import randomIdentifier
from django.conf import settings
import random
import os
import time
import __builtin__

class ImageGenerator(ImageCaptcha):
    def getLayers(self):
        word = Words.defaultWordList.pick()[0:5]
        self.addSolution(word)
        return [
            random.choice([
                Backgrounds.CroppedImage(),
                Backgrounds.TiledImage(),
            ]),
            Text.TextLayer(word, borderSize=1),
            Distortions.SineWarp(),
            ]

class ImageFactory(object):
    """Creates BaseCaptcha instances on demand, and tests solutions.
       CAPTCHAs expire after a given amount of time, given in seconds.
       The default is 15 minutes.
       """
    def __init__(self, lifetime=60*15):
        self.lifetime = lifetime
        self.storedImages = {}

    def new(self):
        """Create a new instance of our assigned BaseCaptcha subclass, passing
           it any extra arguments we're given. This stores the result for
           later testing.
           """
        self.clean()
        image = ImageGenerator()
        imageId = ''
        while True:
            imageId = randomIdentifier()
            if imageId in self.storedImages:
                continue
            else:
                break
        image.id = imageId
        relative_path = '/validate_img/%s.png' % imageId
        try:
            os.makedirs(settings.VALIDATE_IMAGE_ROOT+'/validate_img')
        except:
            pass
        image.storePath = settings.VALIDATE_IMAGE_ROOT + relative_path
        self.storedImages[image.id] = image
        image.render().save(image.storePath)
        return image.solutions[0], relative_path

    def clean(self):
        """Removed expired tests"""
        expiredIds = []
        now = time.time()
        #print 'before : ', self.storedImages.keys()
        for image in self.storedImages.itervalues():
            if image.creationTime + self.lifetime < now:
                expiredIds.append(image.id)
        for id in expiredIds:
            try:
                #print 'remove png file ', self.storedImages[id].storePath
                os.remove(self.storedImages[id].storePath)
            except OSError, e:
                print 'exception'
                pass
            del self.storedImages[id]
        #print 'after : ', self.storedImages.keys()

def createFactory():
        if not hasattr(__builtin__, 'imageFactory'):
            setattr(__builtin__, 'imageFactory', ImageFactory(5))
        return getattr(__builtin__, 'imageFactory')

class ValidateImage(ImageCaptcha):
    @staticmethod
    def generate():
        imageFactory = createFactory()
        return imageFactory.new()

if __name__ == '__main__':
    solution, path = ValidateImage.generate()
    print 'solution : ', solution
    print 'storedPath : ', path
    input = raw_input()
    if input == solution:
        print 'Correct'
    else:
        print 'Incorrect'
    time.sleep(5)
    solution, path = ValidateImage.generate()
    print 'solution : ', solution
    print 'storedPath : ', path

