from service_objects.services import Service
from service_objects import fields
from django.forms import fields as dj_fields
from django.utils.translation import gettext_lazy as _
from .__init__ import gemini, version, genai
from .models import GeminiResponse

class GeminiGenerateContent(Service):
    locales = (
        'en',
        'fr',
        'ar',
        'nl',
        'es',
    )
    
    
    # this is the data fed into the ai e.g: list of reviews, list of sites
    body = dj_fields.CharField(max_length= 100000, )
    verbosity = dj_fields.ChoiceField(
        choices=(
            #default is what gemini will do without specifiying verbosity
            ('default', 'default'),
            #extra explanations
            ('verbose', 'verbose'),
            # medium level of verbosity
            ('medium', 'medium'),
            # brief make the ai give a brief answer
            ('brief', 'brief'),
            # very short answer one line or less
            ('very short', 'short')
        )
    )
    #keep this brief its the main question that the ai answers about the data
    #this is asked after the data is given
    question = dj_fields.CharField(max_length= 2048,)
    
    #intial data descriptions etc
    starting_remarks = dj_fields.CharField(max_length= 2048)
    
    language = dj_fields.ChoiceField(
        choices=(
            ('ar', 'Arabic'),
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'french'),
            ('nl', 'dutch')
        )
    )
    
    temperature = dj_fields.FloatField(initial=0.5, required=False)
        
    def get_prompt(self, body, verbosity, question, starting_remarks, language):
        prompt = f"""
        {starting_remarks}

        Data:
        {body}
        End of Data.
        
        Task:
        {question}
        
        Below you will get two filters for your answers the level of verbosity in your answer and the language of the answer, where verbosity is either one of these, levels: default (your default response length), verbose: extra explanations, medium: less than default but still decent, brief: a brief shortened explanation, short: a very short response
        
        Verbosity:
        {verbosity}
        
        Language:
        {language}
        
        only respond with the answer, if no data is provided simply output: 'No Available Data.'.
        """        
        return prompt
        
    def process(self):
        temperature = self.cleaned_data.pop('temperature')
        prompt = self.get_prompt(**self.cleaned_data)
        genai.GenerationConfig.temperature = temperature
        response= gemini.generate_content(prompt)
        
        response_object = GeminiResponse(content= response.text, temperature= temperature, prompt= prompt, model= version)
        response_object.save()
        
        return response.text
        