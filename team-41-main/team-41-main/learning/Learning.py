from AiClient import AiClient
from SkillTree import SkillTree


import os
from typing import Dict, List, Optional


class Learning:
    def __init__(self, db: Dict[str, any], display_format: str = 'markdown'):
        self.db = db
        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        self.ai_client = AiClient('gpt-4', api_key, display_format)


    def create_skill_tree(self, target_skill: str) -> SkillTree:
        skill_tree = SkillTree(self.ai_client, target_skill)
        self.db['target_skill'] = target_skill
        self.db['skill_tree'] = skill_tree.skills_to_dependencies
        return skill_tree
    
    def save_known_skills(self, known_skills: List[str]) -> None:
        target_skill = self.db['target_skill']
        skill_tree = SkillTree(self.ai_client, target_skill, self.db['skill_tree'])

        for skill in list(skill_tree.skills_to_dependencies.keys()):
            if skill == target_skill:
                continue
            if skill not in known_skills:
                continue
            skill_tree.remove_skill(skill)

        self.db['skill_tree'] = skill_tree.skills_to_dependencies


    def keep_unknown_skills_only(self) -> None:
        target_skill = self.db['target_skill']
        skill_tree = SkillTree(self.ai_client, target_skill, self.db['skill_tree'])

        self.keep_unknown_skills_only_recursive(target_skill, skill_tree)

        self.db['skill_tree'] = skill_tree.skills_to_dependencies


    def keep_unknown_skills_only_recursive(self, skill: str, skill_tree: SkillTree) -> None:
        skill_dependencies = skill_tree.get_dependencies(skill)
        already_asked = set()
        for skill_dependency in skill_dependencies:
            if not skill_tree.contains(skill_dependency):
                continue

            if skill_dependency in already_asked:
                continue

            while True:
                is_known = input(f"Do you know [{skill_dependency}] well? (y/n)")
                if is_known.lower() == 'y':
                    skill_tree.remove_skill(skill_dependency)
                    break
                elif is_known.lower() == 'n':
                    self.keep_unknown_skills_only_recursive(skill_dependency, skill_tree)
                    break
                else:
                    print("Please enter 'y' or 'n'.")
            already_asked.add(skill_dependency)


    def get_roadmap(self) -> Dict[str, List[str]]:
        skills_to_dependencies: Dict[str, List[str]] = self.db['skill_tree']
        return skills_to_dependencies


    def load_from_db(self, key: str, skill: str, **kwargs) -> Optional[dict]:
        if skill not in self.db['skill_tree'].keys():
            print(f"The skill [{skill}] is not on the learning roadmap")
            return None
        if key not in self.db:
            self.db[key] = {}
        data = self.db[key]
        if skill in data:
            result = data[skill]
        else:
            result = self.ai_client.generate(key, skill=skill, **kwargs)
            data[skill] = result
            self.db[key] = data
        return result


    def load_theory(self, skill: str) -> Optional[dict]:
        return self.load_from_db('theory', skill)


    def display_theory(self, skill: str) -> None:
        theory = self.load_theory(skill)
        if not theory:
            return
        print("Here's some learning material:")
        print(theory['learning_material'])


    def quiz(self, skill: str) -> None:
        theory = self.load_theory(skill)
        if not theory:
            return
        for question in theory['questions']:
            print(question['question'])
            for i, option in enumerate(question['options']):
                print(f"{i + 1}. {option}")
            answer = input("Your answer: ")
            if answer == str(question['answer']):
                print("Correct!")
            else:
                print(f"Incorrect. The correct answer is: {question['answer']}")


    def load_task(self, skill: str, interests: str = None) -> dict:
        if not interests:
            interests = self.db['interests']
        return self.load_from_db('task', skill, interests=interests)


    def display_task(self, skill: str, interests: str) -> None:
        task = self.load_task(skill, interests)
        if not task:
            return
        print("Here's a coding task for you:")
        print(f"Title: {task['title']}")
        print(f"Description: {task['description']}")
        print(f"Requirements: {task['requirements']}")


    def feedback(self, skill: str, code_file: str) -> str:
        with open(code_file, 'r') as file:
            code = file.read()
        result = self.feedback_data(skill, code)
        return result
    

    def feedback_data(self, skill: str, code: str) -> str:
        if not self.db['skill_tree'].keys():
            print(f"The skill [{skill}] is not on the learning roadmap")
            return
        if 'task' not in self.db or skill not in self.db['task']:
            print(f"No task found for the skill [{skill}]")
            return
        task = self.db['task'][skill]

        feedback = self.ai_client.generate_plain('feedback', title=task['title'], description=task['description'], requirements=task['requirements'], code=code)
        print(feedback)
        return feedback
    

    def save_interests(self, interests: str) -> None:
        self.db['interests'] = interests