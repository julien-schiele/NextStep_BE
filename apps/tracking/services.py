from apps.programs.services.program_services import ProgramService
from apps.tracking.choices import Status
from apps.tracking.models import UserProgram


class UserProgramService:
    def __init__(self, user_program: UserProgram):
        self.user_program = user_program

    def user_has_completed_the_program(self) -> bool:
        program_service = ProgramService(self.user_program.program)
        sessions_to_complete = program_service.compute_number_of_sessions()

        total_completed = self.user_program.sessions.filter(
            rating__isnull=False
        ).count()

        return total_completed >= sessions_to_complete

    def update_program_status_if_needed(self):
        if (
            self.user_has_completed_the_program()
            and self.user_program.status == Status.ACTIVE
        ):
            self.user_program.status = Status.COMPLETED
            self.user_program.save()

    def next_step_in_program(self) -> dict:

        if self.user_program.status == Status.ABANDONNED or self.user_program.status == Status.COMPLETED:
            return {
                "session": None,
                "cycle": None,
            }

        sessions_qs = self.user_program.sessions.order_by(
            "cycle_count", "session_in_cycle"
        )

        if sessions_qs.count() == 0:
            return {
                "session": 1,
                "cycle": 1,
            }

        last_completed = sessions_qs.filter(rating__isnull=False).last()

        program_service = ProgramService(self.user_program.program)
        cycles = program_service.get_number_of_cycle()
        sessions_per_cycle = program_service.get_number_of_sessions_per_cycle()

        next_session = last_completed.session_in_cycle + 1
        next_cycle = last_completed.cycle_count

        if next_session > sessions_per_cycle:
            next_session = 1
            next_cycle += 1

        if next_cycle > cycles:
            return {
                "session": 0,
                "cycle": 0,
            }

        return {
            "session": next_session,
            "cycle": next_cycle,
        }

    def next_cycle(self) -> int:
        return self.next_step_in_program()["cycle"]

    def next_session(self) -> int:
        return self.next_step_in_program()["session"]
