"""Support for the Microsoft Cognitive Services text-to-speech service."""
from http.client import HTTPException
import logging

import requests
import voluptuous as vol

from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
from homeassistant.const import CONF_API_KEY, CONF_TYPE, UNIT_PERCENTAGE
import homeassistant.helpers.config_validation as cv

CONF_GENDER = "gender"
CONF_OUTPUT = "output"
CONF_RATE = "rate"
CONF_VOLUME = "volume"
CONF_PITCH = "pitch"
CONF_CONTOUR = "contour"
CONF_REGION = "region"

_LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = [
    "ar-eg",
    "ar-sa",
    "ca-es",
    "cs-cz",
    "da-dk",
    "de-at",
    "de-ch",
    "de-de",
    "el-gr",
    "en-au",
    "en-ca",
    "en-gb",
    "en-ie",
    "en-in",
    "en-us",
    "es-es",
    "es-mx",
    "fi-fi",
    "fr-ca",
    "fr-ch",
    "fr-fr",
    "he-il",
    "hi-in",
    "hu-hu",
    "id-id",
    "it-it",
    "ja-jp",
    "ko-kr",
    "nb-no",
    "nl-nl",
    "pl-pl",
    "pt-br",
    "pt-pt",
    "ro-ro",
    "ru-ru",
    "sk-sk",
    "sv-se",
    "th-th",
    "tr-tr",
    "zh-cn",
    "zh-hk",
    "zh-tw",
]

GENDERS = ["Female", "Male"]

DEFAULT_LANG = "en-us"
DEFAULT_GENDER = "Female"
DEFAULT_TYPE = "ZiraRUS"
DEFAULT_OUTPUT = "audio-16khz-128kbitrate-mono-mp3"
DEFAULT_RATE = 0
DEFAULT_VOLUME = 0
DEFAULT_PITCH = "default"
DEFAULT_CONTOUR = ""
DEFAULT_REGION = "eastus"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORTED_LANGUAGES),
        vol.Optional(CONF_GENDER, default=DEFAULT_GENDER): vol.In(GENDERS),
        vol.Optional(CONF_TYPE, default=DEFAULT_TYPE): cv.string,
        vol.Optional(CONF_RATE, default=DEFAULT_RATE): vol.All(
            vol.Coerce(int), vol.Range(-100, 100)
        ),
        vol.Optional(CONF_VOLUME, default=DEFAULT_VOLUME): vol.All(
            vol.Coerce(int), vol.Range(-100, 100)
        ),
        vol.Optional(CONF_PITCH, default=DEFAULT_PITCH): cv.string,
        vol.Optional(CONF_CONTOUR, default=DEFAULT_CONTOUR): cv.string,
        vol.Optional(CONF_REGION, default=DEFAULT_REGION): cv.string,
    }
)


def get_engine(hass, config, discovery_info=None):
    """Set up Microsoft speech component."""
    return MicrosoftProvider(
        config[CONF_API_KEY],
        config[CONF_LANG],
        config[CONF_GENDER],
        config[CONF_TYPE],
        config[CONF_RATE],
        config[CONF_VOLUME],
        config[CONF_PITCH],
        config[CONF_CONTOUR],
        config[CONF_REGION],
    )

def unicode_replacer(text):
    text = text.replace('ä', '&#228;')
    text = text.replace('ö', '&#246;')
    text = text.replace('ü', '&#252;')
    text = text.replace('Ä', '&#196;')
    text = text.replace('Ö', '&#214;')
    text = text.replace('Ü', '&#220;')

    return text

class MicrosoftProvider(Provider):
    """The Microsoft speech API provider."""

    def __init__(
        self, apikey, lang, gender, ttype, rate, volume, pitch, contour, region
    ):
        """Init Microsoft TTS service."""
        self._apikey = apikey
        self._lang = lang
        self._gender = gender
        self._type = ttype
        self._output = DEFAULT_OUTPUT
        self._rate = f"{rate}{UNIT_PERCENTAGE}"
        self._volume = f"{volume}{UNIT_PERCENTAGE}"
        self._pitch = pitch
        self._contour = contour
        self._region = region
        self.name = "Microsoft"

    @property
    def default_language(self):
        """Return the default language."""
        return self._lang

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORTED_LANGUAGES

    def get_tts_audio(self, message, language, options=None):
        """Load TTS from Microsoft."""
        if language is None:
            language = self._lang

        try:
            base_url = 'https://' + self._region + '.tts.speech.microsoft.com/'
            path = 'cognitiveservices/v1'
            constructed_url = base_url + path
            headers = {
                'Ocp-Apim-Subscription-Key': self._apikey,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-24khz-160kbitrate-mono-mp3'
            }
            body = unicode_replacer(message)
            response = requests.post(constructed_url, headers=headers, data=body)
        except HTTPException as ex:
            _LOGGER.error("Error occurred for Microsoft TTS: %s", ex)
            return (None, None)
        return ("mp3", response.content)
