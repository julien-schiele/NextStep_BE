from typing import Dict, Any, List
from apps.programs.models import Program, Exercise


class ProgramService:
    """
    A service for manipulating a program.
    Example: enriching content, calculating preview, etc.
    """

    def __init__(self, program: Program):
        self.program = program
        self.exercises_cache = self._fetch_exercises_cache()

    @classmethod
    def init_from_program_id(cls, program_id: str):
        try:
            program = Program.objects.get(id=program_id)
            return cls(program)
        except Program.DoesNotExist:
            raise ValueError(f"Program with id '{program_id}' not found")

    def _fetch_exercises_cache(self) -> Dict[str, Exercise]:
        """
        Preload all exercises used in program.content to avoid N+1 queries.
        """
        slugs = set()
        for session in self.program.content.get("sessions", []):
            for sequence in session.get("sequences", []):
                for item in sequence:
                    slug = item.get("exercise")
                    if slug:
                        slugs.add(slug)
        exercises = Exercise.objects.filter(slug__in=slugs)
        return {ex.slug: ex for ex in exercises}

    def enrich_exercise(self, slug: str) -> Dict[str, Any]:
        ex = self.exercises_cache.get(slug)
        if not ex:
            return {"slug": slug, "missing": True}
        return {
            "slug": slug,
            "name": ex.safe_translation_getter("name", any_language=True),
            "description": ex.safe_translation_getter("description", any_language=True),
            "resolution": ex.resolution,
            "practice_zone": ex.practice_zone,
        }

    def enrich_content(self) -> dict:
        """
        Returns the content enriched with the exercise data.
        """
        content = self.program.content.copy()
        for session in content.get("sessions", []):
            for sequence in session.get("sequences", []):
                for item in sequence:
                    slug = item.get("exercise")
                    item["exercise_data"] = self.enrich_exercise(slug)
        return content

    def compute_preview(self) -> dict:
        """
        Returns the program preview with calculation of repetitions per cycle.
        """
        content = self.program.content
        sessions = content.get("sessions", [])
        repeat = content.get("repeat", {})
        cycles = repeat.get("cycles", 1)
        progression = repeat.get("progression", {})

        preview = {"total_cycles": cycles, "cycles": []}

        for cycle_index in range(cycles):
            cycle_data = {"cycle": cycle_index + 1, "sessions": []}

            for session in sessions:
                session_data = {"session": session["session"], "sequences": []}

                for sequence in session.get("sequences", []):
                    seq_data = []

                    for item in sequence:
                        slug = item["exercise"]
                        base_value = item["value"]
                        value = base_value

                        prog = progression.get(slug)
                        if prog:
                            increment = prog.get("increment", 0)
                            per_cycle = prog.get("per_cycle", 1)
                            value += cycle_index * increment * per_cycle

                        seq_data.append({**self.enrich_exercise(slug), "value": value})
                    session_data["sequences"].append(seq_data)
                cycle_data["sessions"].append(session_data)
            preview["cycles"].append(cycle_data)

        return preview
