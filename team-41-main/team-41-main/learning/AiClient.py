import json
from openai import AzureOpenAI


class AiClient:
    def __init__(self, deployment_name: str, api_key: str, display_format: str):
        self.__deployment_name = deployment_name
        self.__client = AzureOpenAI(
            api_key = api_key,
            api_version =  "2023-07-01-preview",
            azure_endpoint = "https://ai-proxy.lab.epam.com")
        self.__display_format = display_format

    def generate(self, template_name: str, **kwargs) -> object:
        content = self.generate_plain(template_name, **kwargs)
        json_content = self.__clean_response(content)
        return json.loads(json_content)

    def generate_plain(self, template_name: str, **kwargs) -> str:
        prompt = self.__get_prompt(template_name, **kwargs)
        content = self.__create(prompt)
        return content

    def __get_prompt(self, template_name: str, **kwargs) -> str:
        with open(f'prompts/{template_name}.txt', 'tr') as file:
            template = file.read()
        kwargs['display_format'] = self.__display_format
        return template.format(**kwargs)

    def __create(self, prompt: str) -> str:
        response = self.__client.chat.completions.create(
            model=self.__deployment_name,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response.choices[0].message.content

    @staticmethod
    def __clean_response(response: str) -> str:
        lines = response.split('\n')
        if lines[0].strip() == '```json' or lines[0].strip() == '```':
            lines = lines[1:]
            if lines[-1].strip() == '```':
                lines.pop()
        return '\n'.join(lines)