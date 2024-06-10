from argparse import ArgumentParser
import shelve
from learning import Learning


STATE_FILE_PATH = '.state'


class CliApp:
    def __init__(self):
        self.db = shelve.open(STATE_FILE_PATH, 'n')
        self.app = Learning(self.db)
        self.process_arguments()


    def __del__(self):
        self.db.close()

    
    def process_arguments(self) -> None:
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()

        skill_parser = subparsers.add_parser('target')
        skill_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        skill_parser.set_defaults(func=lambda args: self.app.create_skill_tree(args.skill_name))

        known_skills_parser = subparsers.add_parser('known_skills')
        known_skills_parser.set_defaults(func=lambda _: self.app.keep_unknown_skills_only())

        roadmap_parser = subparsers.add_parser('roadmap')
        roadmap_parser.set_defaults(self.roadmap)

        theory_parser = subparsers.add_parser('theory')
        theory_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        theory_parser.set_defaults(func=lambda args: self.app.display_theory(args.skill_name))

        quiz_parser = subparsers.add_parser('quiz')
        quiz_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        quiz_parser.set_defaults(func=lambda args: self.app.quiz(args.skill_name))

        task_parser = subparsers.add_parser('task')
        task_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        task_parser.add_argument('interests', type=str, help='Your interests as a comma-separated list')
        task_parser.set_defaults(func=lambda args: self.app.display_task(args.skill_name, args.interests))

        feedback_parser = subparsers.add_parser('check')
        feedback_parser.add_argument('skill_name', type=str, help='The skill you want to learn')
        feedback_parser.add_argument('code_file', type=str, help='Path to the file with your code')
        feedback_parser.set_defaults(func=lambda args: self.app.feedback(args.skill_name, args.code_file))

        args = parser.parse_args()
        args.func(args)


    def roadmap(self, _) -> None:
        skills_to_dependencies = self.app.get_roadmap()
        print(skills_to_dependencies)


if __name__ == '__main__':
    CliApp()
