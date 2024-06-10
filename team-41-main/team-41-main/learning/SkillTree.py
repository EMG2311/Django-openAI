from typing import Dict, List
import AiClient as AiClient


class SkillTree:
    def __init__(self, ai_client: AiClient, target_skill: str, skills_to_dependencies: Dict[str, List[str]] = None):
        self.target_skill = target_skill
        if skills_to_dependencies:
            self.skills_to_dependencies = skills_to_dependencies
        else:
            self.skills_to_dependencies: Dict[str, List[str]] = ai_client.generate('skills', skill=target_skill)
            self.__remove_skills_without_refernces()
        self.__remove_references_to_non_existing_skills()
    
    def get_dependencies(self, skill: str) -> list:
        if skill not in self.skills_to_dependencies:
            return []
        return list(self.skills_to_dependencies[skill])
    
    def contains(self, skill: str) -> bool:
        return skill in self.skills_to_dependencies
    
    def remove_skill(self, skill: str) -> None:
        if skill in self.skills_to_dependencies:
            del self.skills_to_dependencies[skill]
        for dependencies in list(self.skills_to_dependencies.values()):
            if skill in dependencies:
                dependencies.remove(skill)
        self.__remove_skills_without_refernces()

    def ready_to_learn(self) -> list:
        return list(skill
                    for skill, dependencies
                    in self.skills_to_dependencies.items()
                    if not dependencies)
    
    def __remove_skills_without_refernces(self) -> None:
        repeat_required = False
        while repeat_required:
            skills_with_references = set()
            for dependencies in self.skills_to_dependencies.values():
                skills_with_references.update(dependencies)
            for skill in list(self.skills_to_dependencies.keys()):
                if skill == self.target_skill:
                    continue
                if skill not in skills_with_references:
                    del self.skills_to_dependencies[skill]
                    repeat_required = True
    
    def __remove_references_to_non_existing_skills(self) -> None:
        for dependencies in self.skills_to_dependencies.values():
            for skill in list(dependencies):
                if skill not in self.skills_to_dependencies:
                    dependencies.remove(skill)