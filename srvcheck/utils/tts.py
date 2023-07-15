import subprocess


class TTS:
    pass


class EspeakTTS(TTS):
    def say(self, text, file, lang="it"):
        voice = "english"
        if lang == "it":
            voice = "italian-mbrola-3"

        cmd = [
            "espeak",
            '"' + text + '"',
            "-s",
            "140",
            "-p",
            "75",
            "-v",
            voice,
            "-w",
            file,
        ]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
