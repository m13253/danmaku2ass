Danmaku2ASS
===========

What is it?
-----------

Danmaku2ASS converts comments from Niconico/Acfun/Bilibili to ASS format so that you can play it with any media player supporting ASS subtitle.

This software is free software released under GPL 3 license. There is no warranty to the extent permitted by law.

How to use it?
--------------

First, you will have to get the XML or JSON file from Niconico/Acfun/Bilibili, many software can help you get it. For example, [you-get](https://github.com/soimort/you-get) and [nicovideo-dl](http://sourceforge.jp/projects/nicovideo-dl/).

Then, execute `danmaku2ass`. You can see further instructions below.

Example usage
-------------

```sh
./danmaku2ass -o foo.ass -s 1920x1080 -fn "MS PGothic" -fs 48 -a 0.8 -l 5 foo.xml
```

Name the output file with same basename but different extension (.ass) as the video. Put them into the same directory and most media players will automatically load them.

Make sure that the width/height ratio passed to `danmaku2ass` matches the one of your original video, or text deformation may be experienced.

You can also pass multiple XML/JSON files and they will be merged into one ASS file. This is useful when watching danmakus from different website at the same time.

Command line reference
----------------------

```
usage: danmaku2ass.py [-h] [-o OUTPUT] -s WIDTHxHEIGHT [-fn FONT] [-fs SIZE]
                      [-a ALPHA] [-l SECONDS] [-p HEIGHT] [-r]
                      FILE [FILE ...]

positional arguments:
  FILE                  Comment file to be processed

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s WIDTHxHEIGHT, --size WIDTHxHEIGHT
                        Stage size in pixels
  -fn FONT, --font FONT
                        Specify font face
  -fs SIZE, --fontsize SIZE
                        Default font size
  -a ALPHA, --alpha ALPHA
                        Text opaque
  -l SECONDS, --lifetime SECONDS
                        Duration of comment display
  -p HEIGHT, --protect HEIGHT
                        Reserve blank on the bottom of the stage
  -r, --reduce          Reduce the amount of danmakus if stage is full
```

FAQ
---

### The text is moving laggy. / The text is slightly blurred.

Most ASS renderers render ASS subtitles at the same resolution as the video. This is probably because the video is at low resolution or framerate.

### I would like to render the danmakus into the video.

Use `ffmpeg`:

```sh
ffmpeg -i foo.flv -vf ass=foo.ass -vcodec libx264 -acodec copy foo-with-danmaku.flv
```

Change the parameters as you like.

### Danmaku2ASS gave me some warnings of 'Invalid comment'.

This is probably because of comment styles that are not recognized by Danmaku2ASS. This is mostly normal. However, if you think that Danmaku2ASS missed some important things, please feel free to submit an issue.

### Is there a GUI?

Currently no. But there will soon be one made of Gtk+ 3. If you would like to help me, please contact with me.

Contributing
------------

Any contribution is welcome. Any donation is welcome as well.

