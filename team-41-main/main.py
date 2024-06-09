from argparse import ArgumentParser
import os
import shelve
from typing import Optional
from AiClient import AiClient
from SkillTree import SkillTree


STATE_FILE_PATH = '.state'


class App:
    def __init__(self):
        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        self.ai_client = AiClient('gpt-4', api_key)
        self.process_arguments()

    
    def process_arguments(self) -> None:
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()

        skill_parser = subparsers.add_parser('target')
        skill_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        skill_parser.set_defaults(func=lambda args: self.create_skill_tree(args.skill_name))

        known_skills_parser = subparsers.add_parser('known_skills')
        known_skills_parser.set_defaults(func=self.keep_unknown_skills_only)

        roadmap_parser = subparsers.add_parser('roadmap')
        roadmap_parser.set_defaults(func=lambda _: self.display_roadmap())

        theory_parser = subparsers.add_parser('theory')
        theory_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        theory_parser.set_defaults(func=lambda args: self.display_theory(args.skill_name))

        quiz_parser = subparsers.add_parser('quiz')
        quiz_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        quiz_parser.set_defaults(func=lambda args: self.quiz(args.skill_name))

        task_parser = subparsers.add_parser('task')
        task_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        task_parser.add_argument('interests', type=str, help='Your interests as a comma-separated list')
        task_parser.set_defaults(func=lambda args: self.display_task(args.skill_name, args.interests))

        feedback_parser = subparsers.add_parser('check')
        feedback_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        feedback_parser.add_argument('code_file', type=str, help='Path to the file with your code')
        feedback_parser.set_defaults(func=lambda args: self.feedback(args.skill_name, args.code_file))

        args = parser.parse_args()
        args.func(args)


    def create_skill_tree(self, target_skill: str) -> None:
        skill_tree = SkillTree(self.ai_client, target_skill)
        with shelve.open(STATE_FILE_PATH, 'n') as db:
            db['target_skill'] = target_skill
            db['skill_tree'] = skill_tree


    def keep_unknown_skills_only(self, _) -> None:
        with shelve.open(STATE_FILE_PATH, 'r') as db:
            target_skill = db['target_skill']
            skill_tree = db['skill_tree']

        self.keep_unknown_skills_only_recursive(target_skill, skill_tree)

        with shelve.open(STATE_FILE_PATH, 'w') as db:
            db['skill_tree'] = skill_tree
    
    
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

    
    def display_roadmap(self) -> None:
        with shelve.open(STATE_FILE_PATH, 'r') as db:
            skill_tree = db['skill_tree']
            print(skill_tree.skills_to_dependencies)


    def load_from_db(self, key: str, skill: str, **kwargs) -> Optional[dict]:
        with shelve.open(STATE_FILE_PATH, 'w') as db:
            if skill not in db['skill_tree'].skills_to_dependencies.keys():
                print(f"The skill [{skill}] is not on the learning roadmap")
                return None
            if key not in db:
                db[key] = {}
            data = db[key]
            if skill in data:
                result = data[skill]
            else:
                result = self.ai_client.generate(key, skill=skill, **kwargs)
                data[skill] = result
                db[key] = data
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


    def load_task(self, skill: str, interests: str) -> dict:
        return self.load_from_db('task', skill, interests=interests)


    def display_task(self, skill: str, interests: str) -> None:
        task = self.load_task(skill, interests)
        if not task:
            return
        print("Here's a coding task for you:")
        print(f"Title: {task['title']}")
        print(f"Description: {task['description']}")
        print(f"Requirements: {task['requirements']}")

    
    def feedback(self, skill: str, code_file: str) -> None:
        with shelve.open(STATE_FILE_PATH, 'r') as db:
            if not db['skill_tree'].skills_to_dependencies.keys():
                print(f"The skill [{skill}] is not on the learning roadmap")
                return
            if 'tasks' not in db or skill not in db['tasks']:
                print(f"No task found for the skill [{skill}]")
                return
            task = db['tasks'][skill]
        with open(code_file, 'r') as file:
            code = file.read()
        
        feedback = self.ai_client.generate_plain('feedback', title=task['title'], description=task['description'], requirements=task['requirements'], code=code)
        print(feedback)


if __name__ == '__main__':
    app = App()
