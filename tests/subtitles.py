import unittest
import tempfile
import os
import codecs
from subs import AssEvent, AssScript, SrtEvent, SrtScript

SINGLE_LINE_SRT_EVENT = """228
00:14:21,960 --> 00:14:22,960
HOW DID IT END UP LIKE THIS?"""

MULTILINE_SRT_EVENT = """203
00:13:12,140 --> 00:13:14,100
APPEARANCE!
Appearrance (teisai)!
No wait, you're the worst (saitei)!"""

ASS_EVENT = r"Dialogue: 0,0:18:50.98,0:18:55.28,Default,,0,0,0,,Are you trying to (ouch) crush it (ouch)\N like a (ouch) vise (ouch, ouch)?"

ASS_COMMENT = r"Comment: 0,0:18:09.15,0:18:10.36,Default,,0,0,0,,I DON'T GET IT TOO WELL."


class SrtEventTestCase(unittest.TestCase):
    def test_simple_parsing(self):
        event = SrtEvent(SINGLE_LINE_SRT_EVENT)
        self.assertEquals(228, event.idx)
        self.assertEquals(14*60+21.960, event.start)
        self.assertEquals(14*60+22.960, event.end)
        self.assertEquals("HOW DID IT END UP LIKE THIS?", event.text)

    def test_multi_line_event_parsing(self):
        event = SrtEvent(MULTILINE_SRT_EVENT)
        self.assertEquals(203, event.idx)
        self.assertEquals(13*60+12.140, event.start)
        self.assertEquals(13*60+14.100, event.end)
        self.assertEquals("APPEARANCE!\nAppearrance (teisai)!\nNo wait, you're the worst (saitei)!", event.text)

    def test_parsing_and_printing(self):
        self.assertEquals(SINGLE_LINE_SRT_EVENT, unicode(SrtEvent(SINGLE_LINE_SRT_EVENT)))
        self.assertEquals(MULTILINE_SRT_EVENT, unicode(SrtEvent(MULTILINE_SRT_EVENT)))


class AssEventTestCase(unittest.TestCase):
    def test_simple_parsing(self):
        event = AssEvent(ASS_EVENT)
        self.assertFalse(event.is_comment)
        self.assertEquals("Dialogue", event.kind)
        self.assertEquals(18*60+50.98, event.start)
        self.assertEquals(18*60+55.28, event.end)
        self.assertEquals("0", event.layer)
        self.assertEquals("Default", event.style)
        self.assertEquals("", event.name)
        self.assertEquals("0", event.margin_left)
        self.assertEquals("0", event.margin_right)
        self.assertEquals("0", event.margin_vertical)
        self.assertEquals("", event.effect)
        self.assertEquals("Are you trying to (ouch) crush it (ouch)\N like a (ouch) vise (ouch, ouch)?", event.text)

    def test_comment_parsing(self):
        event = AssEvent(ASS_COMMENT)
        self.assertTrue(event.is_comment)
        self.assertEquals("Comment", event.kind)

    def test_parsing_and_printing(self):
        self.assertEquals(ASS_EVENT, unicode(AssEvent(ASS_EVENT)))
        self.assertEquals(ASS_COMMENT, unicode(AssEvent(ASS_COMMENT)))


class SrtScriptTestCase(unittest.TestCase):
    def test_write_to_file(self):
        _, name = tempfile.mkstemp()
        try:
            events = [SrtEvent(SINGLE_LINE_SRT_EVENT), SrtEvent(MULTILINE_SRT_EVENT)]
            SrtScript(events).save_to_file(name)
            with open(name) as script:
                text = script.read()
            self.assertEquals(SINGLE_LINE_SRT_EVENT + "\n\n" + MULTILINE_SRT_EVENT, text)
        finally:
            os.remove(name)

    def test_read_from_file(self):
        fd, name = tempfile.mkstemp(text=True)
        try:
            os.write(fd, """1
00:00:17,500 --> 00:00:18,870
Yeah, really!

2
00:00:21,250 --> 00:00:22,750
Serves you right.""")
            parsed = SrtScript.from_file(name).events
            self.assertEquals(1, parsed[0].idx)
            self.assertEquals(17.5, parsed[0].start)
            self.assertEquals(18.87, parsed[0].end)
            self.assertEquals("Yeah, really!", parsed[0].text)
            self.assertEquals(2, parsed[1].idx)
            self.assertEquals(21.25, parsed[1].start)
            self.assertEquals(22.75, parsed[1].end)
            self.assertEquals("Serves you right.", parsed[1].text)
        finally:
            os.remove(name)


class AssScriptTestCase(unittest.TestCase):
    def test_write_to_file(self):
        _, name = tempfile.mkstemp()
        try:
            styles = ["Style: Default,Open Sans Semibold,36,&H00FFFFFF,&H000000FF,&H00020713,&H00000000,-1,0,0,0,100,100,0,0,1,1.7,0,2,0,0,28,1"]
            events = [AssEvent(ASS_EVENT), AssEvent(ASS_EVENT)]
            AssScript([], styles, events).save_to_file(name)

            with codecs.open(name, encoding='utf-8-sig') as script:
                text = script.read()

            self.assertEquals("""[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Open Sans Semibold,36,&H00FFFFFF,&H000000FF,&H00020713,&H00000000,-1,0,0,0,100,100,0,0,1,1.7,0,2,0,0,28,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{0}
{0}""".format(ASS_EVENT), text)
        finally:
            os.remove(name)

    def test_read_from_file(self):
        text = """[Script Info]
; Script generated by Aegisub 3.1.1
Title: script title

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Open Sans Semibold,36,&H00FFFFFF,&H000000FF,&H00020713,&H00000000,-1,0,0,0,100,100,0,0,1,1.7,0,2,0,0,28,1
Style: Signs,Gentium Basic,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.42,0:00:03.36,Default,,0000,0000,0000,,As you already know,
Dialogue: 0,0:00:03.36,0:00:05.93,Default,,0000,0000,0000,,I'm concerned about the hair on my nipples."""

        fd, name = tempfile.mkstemp(text=True)
        try:
            os.write(fd, text)
            script = AssScript.from_file(name)
            self.assertEquals(["; Script generated by Aegisub 3.1.1", "Title: script title"], script.script_info)
            self.assertEquals(["Style: Default,Open Sans Semibold,36,&H00FFFFFF,&H000000FF,&H00020713,&H00000000,-1,0,0,0,100,100,0,0,1,1.7,0,2,0,0,28,1",
                               "Style: Signs,Gentium Basic,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1"],
                              script.styles)
            self.assertEquals([0, 1], [x.source_index for x in script.events])
            self.assertEquals(u"Dialogue: 0,0:00:01.42,0:00:03.36,Default,,0000,0000,0000,,As you already know,", unicode(script.events[0]))
            self.assertEquals(u"Dialogue: 0,0:00:03.36,0:00:05.93,Default,,0000,0000,0000,,I'm concerned about the hair on my nipples.", unicode(script.events[1]))
        finally:
            os.remove(name)
