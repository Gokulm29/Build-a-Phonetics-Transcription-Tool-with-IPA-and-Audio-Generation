# -*- coding: utf-8 -*-
"""Phonetics.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zhY53DZdiXA1RpBG-tWG44Lis00ZyX6G
"""

!pip install pronouncing epitran gtts gradio IPython

import pronouncing
import epitran
from gtts import gTTS
import gradio as gr
import os

# Your existing functions with adjustments
def transcribe_to_ipa(text, language):
    if language == 'en-US' or language == 'eng-Latn':  # Treat en-US as eng-Latn
        words = text.lower().split()
        transcription = []
        for word in words:
            phones = pronouncing.phones_for_word(word)
            if phones:
                ipa = arpabet_to_ipa(phones[0])
                transcription.append(ipa)
            else:
                transcription.append(f"[{word}]")
        return " ".join(transcription)
    else:
        try:
            epi = epitran.Epitran(language)
            return epi.transliterate(text)
        except Exception as e:
            return f"Error: Language '{language}' not supported by Epitran ({str(e)})"

def arpabet_to_ipa(arpabet):
    mapping = {
        'AA': 'ɑ', 'AE': 'æ', 'AH': 'ə', 'AO': 'ɔ', 'AW': 'aʊ',
        'AY': 'aɪ', 'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð',
        'EH': 'ɛ', 'ER': 'ɜr', 'EY': 'eɪ', 'F': 'f', 'G': 'ɡ',
        'HH': 'h', 'IH': 'ɪ', 'IY': 'i', 'JH': 'dʒ', 'K': 'k',
        'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'OW': 'oʊ',
        'OY': 'ɔɪ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ',
        'T': 't', 'TH': 'θ', 'UH': 'ʊ', 'UW': 'u', 'V': 'v',
        'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'
    }
    phonemes = arpabet.split()
    ipa = ""
    for phoneme in phonemes:
        if phoneme[-1].isdigit():
            sound = phoneme[:-1]
            if phoneme[-1] == '1': ipa += "ˈ"
            elif phoneme[-1] == '2': ipa += "ˌ"
        else:
            sound = phoneme
        ipa += mapping.get(sound, sound.lower())
    return ipa

def explain_phonemes(ipa):
    descriptions = {
        'k': 'voiceless velar stop', 'æ': 'near-open front vowel',
        't': 'voiceless alveolar stop', 'h': 'voiceless glottal fricative',
        'ə': 'mid-central vowel (schwa)', 'ˈ': 'primary stress',
        'l': 'alveolar lateral approximant', 'oʊ': 'diphthong (mid-back to high-back)',
        'ð': 'voiced dental fricative', 'ɡ': 'voiced velar stop',
        'r': 'alveolar approximant', 'ʌ': 'open-mid back vowel',
        'n': 'alveolar nasal', 'z': 'voiced alveolar fricative'
    }
    breakdown = []
    i = 0
    while i < len(ipa):
        if i + 1 < len(ipa) and ipa[i:i+2] in descriptions:
            char = ipa[i:i+2]
            breakdown.append(f"/{char}/: {descriptions[char]}")
            i += 2
        elif ipa[i] in descriptions:
            char = ipa[i]
            breakdown.append(f"/{char}/: {descriptions[char]}")
            i += 1
        else:
            i += 1
    return "\n".join(breakdown)

def process_input(text, language):
    # Map en-US to eng-Latn for consistency in transcription
    if language == 'en-US':
        language = 'eng-Latn'

    # Generate IPA transcription
    ipa_result = transcribe_to_ipa(text, language)

    # Generate phoneme explanation
    phoneme_explanation = explain_phonemes(ipa_result)

    # Attempt audio generation with gTTS
    audio_file = None
    gtts_lang_map = {
        'eng-Latn': 'en', 'en-US': 'en', 'spa-Latn': 'es', 'fra-Latn': 'fr', 'deu-Latn': 'de',
        'ita-Latn': 'it', 'rus-Cyrl': 'ru', 'cmn-Hans': 'zh-cn', 'cmn-Hant': 'zh-tw',
        'por-Latn': 'pt', 'jpn-Hrgn': 'ja', 'jpn-Ktkn': 'ja', 'kor-Hang': 'ko',
        'vie-Latn': 'vi', 'tur-Latn': 'tr', 'nld-Latn': 'nl', 'swe-Latn': 'sv',
        'pol-Latn': 'pl', 'tha-Thai': 'th', 'hun-Latn': 'hu', 'ces-Latn': 'cs',
        'ron-Latn': 'ro', 'ukr-Cyrl': 'uk', 'hin-Deva': 'hi', 'ben-Beng': 'bn',
        'tam-Taml': 'ta', 'tel-Telu': 'te', 'mar-Deva': 'mr', 'urd-Arab': 'ur',
        'fas-Arab': 'fa', 'ara-Arab': 'ar', 'mal-Mlym': 'ml', 'mya-Mymr': 'my'
    }

    gtts_lang = gtts_lang_map.get(language)
    if gtts_lang:
        try:
            audio_file = "output.mp3"
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(audio_file)
        except Exception as e:
            output_text = f"IPA Transcription: /{ipa_result}/\n\nPhoneme Breakdown:\n{phoneme_explanation}\n\nWarning: Audio generation failed ({str(e)})"
            return output_text, None
    else:
        output_text = f"IPA Transcription: /{ipa_result}/\n\nPhoneme Breakdown:\n{phoneme_explanation}\n\nNote: Audio not available for '{language}'"
        return output_text, None

    # Prepare text output
    output_text = f"IPA Transcription: /{ipa_result}/\n\nPhoneme Breakdown:\n{phoneme_explanation}"

    return output_text, audio_file

# All languages from your list, with en-US added
languages = [
    'en-US',  # Added as the first option for default
    'aar-Latn', 'aii-Syrc', 'amh-Ethi', 'amh-Ethi-pp', 'amh-Ethi-red', 'ara-Arab',
    'ava-Cyrl', 'aze-Cyrl', 'aze-Latn', 'ben-Beng', 'ben-Beng-red', 'bxk-Latn',
    'cat-Latn', 'ceb-Latn', 'ces-Latn', 'cjy-Latn', 'cmn-Hans', 'cmn-Hant',
    'cmn-Latn', 'ckb-Arab', 'csb-Latn', 'deu-Latn', 'deu-Latn-np', 'deu-Latn-nar',
    'eng-Latn', 'epo-Latn', 'fas-Arab', 'fra-Latn', 'fra-Latn-np', 'fra-Latn-p',
    'ful-Latn', 'gan-Latn', 'got-Latn', 'hak-Latn', 'hau-Latn', 'hin-Deva',
    'hmn-Latn', 'hrv-Latn', 'hsn-Latn', 'hun-Latn', 'ilo-Latn', 'ind-Latn',
    'ita-Latn', 'jam-Latn', 'jpn-Hrgn', 'jpn-Hrgn-red', 'jpn-Ktkn', 'jpn-Ktkn-red',
    'jav-Latn', 'kaz-Cyrl', 'kaz-Cyrl-bab', 'kaz-Latn', 'kbd-Cyrl', 'khm-Khmr',
    'kin-Latn', 'kir-Arab', 'kir-Cyrl', 'kir-Latn', 'kmr-Latn', 'kmr-Latn-red',
    'kor-Hang', 'lao-Laoo', 'lij-Latn', 'lsm-Latn', 'ltc-Latn-bax', 'mal-Mlym',
    'mar-Deva', 'mlt-Latn', 'mon-Cyrl-bab', 'mri-Latn', 'msa-Latn', 'mya-Mymr',
    'nan-Latn', 'nan-Latn-tl', 'nld-Latn', 'nya-Latn', 'ood-Lat-alv', 'ood-Latn-sax',
    'ori-Orya', 'orm-Latn', 'pan-Guru', 'pol-Latn', 'por-Latn', 'quy-Latn',
    'ron-Latn', 'run-Latn', 'rus-Cyrl', 'sag-Latn', 'sin-Sinh', 'sna-Latn',
    'som-Latn', 'spa-Latn', 'spa-Latn-eu', 'sqi-Latn', 'srp-Latn', 'swa-Latn',
    'swa-Latn-red', 'swe-Latn', 'tam-Taml', 'tam-Taml-red', 'tel-Telu', 'tgk-Cyrl',
    'tgl-Latn', 'tgl-Latn-red', 'tha-Thai', 'tir-Ethi', 'tir-Ethi-pp', 'tir-Ethi-red',
    'tpi-Latn', 'tuk-Cyrl', 'tuk-Latn', 'tur-Latn', 'tur-Latn-bab', 'tur-Latn-red',
    'ukr-Cyrl', 'urd-Arab', 'uig-Arab', 'uzb-Cyrl', 'uzb-Latn', 'vie-Latn',
    'wuu-Latn', 'xho-Latn', 'yor-Latn', 'yue-Latn', 'zha-Latn', 'zul-Latn'
]

# Create Gradio interface
with gr.Blocks(title="Phonetics Tool") as demo:
    gr.Markdown("# Phonetics Transcription Tool")
    gr.Markdown("Enter text and select a language/script pair to get IPA transcription and audio (if available)")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Enter your text")
            language_dropdown = gr.Dropdown(
                choices=languages,
                value='en-US',  # Set default to en-US
                label="Select Language/Script"
            )
            submit_btn = gr.Button("Process")

        with gr.Column():
            output_text = gr.Textbox(label="Transcription and Breakdown", lines=10)
            output_audio = gr.Audio(label="Pronunciation")

    # Connect the button to the processing function
    submit_btn.click(
        fn=process_input,
        inputs=[text_input, language_dropdown],
        outputs=[output_text, output_audio]
    )

# Launch the interface
demo.launch()

