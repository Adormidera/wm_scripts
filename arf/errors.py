from typing import Optional


class ARFError(Exception):
    def __init__(self, *args, detail: str = None, solution: Optional[str] = None):
        super().__init__(*args)
        self.detail = detail
        self.solution = solution

    def explain(self) -> str:
        msg = []
        if details := self.detail or "unknown":
            msg.append(f"problem: {details}")

        if solution := self.solution or "unknown":
            msg.append(f"solution: {solution}")

        return "\n".join(msg)


class MissingDependency(ARFError):
    def __init__(self, dependency: str, *args):
        super().__init__(*args)
        self.dependency = dependency

    @property
    def detail(self):
        return f"dependency {self.dependency} is missing in this system"

    @property
    def solution(self):
        return f"install {self.dependency}"
