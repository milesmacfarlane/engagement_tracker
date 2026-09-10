"""Calculation service - ported from utils.py"""

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models import Observation, Student

# Engagement Measures
ENGAGEMENT_MEASURES = [
    "Time on Task",
    "Asked/Answered/Shared",
    "Engaged with Content and Others",
    "Materials/Organized",
    "Seeks Teacher Support"
]

# Measure mapping for backward compatibility
MEASURE_MAPPING = {
    "Time on Task": "Time on Task",
    "Asked/Answered/Shared": "Asked/Answered/Shared",
    "Engaged with Content and Others": "Engaged with Content and Others",
    "Materials/Organized": "Materials/Organized",
    "Seeks Teacher Support": "Seeks Teacher Support",
    "In-class Work Completed": "Time on Task",
    "Work Completed/Ready": "Engaged with Content and Others",
    "Helping/Asking for Help": "Engaged with Content and Others",
    "Asks for Clarification": "Seeks Teacher Support",
    "Check-ins with Teacher": "Seeks Teacher Support",
    "Asks for Ways to Improve": "Seeks Teacher Support"
}

# Performance bands
PERFORMANCE_BANDS = [
    (85, 100, "Exemplary", "#00B050"),
    (75, 85, "Proficient", "#92D050"),
    (65, 75, "Developing", "#FFFF00"),
    (50, 65, "Emerging", "#FFC000"),
    (40, 50, "Beginning", "#FF9900"),
    (0, 40, "Needs Intensive Support", "#FF0000")
]

# Colors
COLORS = {
    'primary': '#1F4788',
    'success': '#00B050',
    'warning': '#FF9900',
    'error': '#FFC7CE',
    'neutral': '#D9D9D9',
    'observed': '#00B050',
    'not_observed': '#FFC7CE',
    'absent': '#D9D9D9'
}


class CalculationService:
    """Service for engagement tracking calculations."""

    @staticmethod
    def normalize_measure_name(measure_name: str) -> str:
        """Map old measure names to new for backward compatibility."""
        return MEASURE_MAPPING.get(measure_name, measure_name)

    @staticmethod
    def get_performance_band(percentage: float | None) -> tuple[str, str]:
        """Map percentage to performance band (name, color)."""
        if percentage is None:
            return "No Data", COLORS['neutral']

        for low, high, name, color in PERFORMANCE_BANDS:
            if low <= percentage < high or (high == 100 and percentage == 100):
                return name, color

        return "Unknown", COLORS['neutral']

    @staticmethod
    def get_band_emoji(percentage: float | None) -> str:
        """Get emoji for performance band."""
        if percentage is None:
            return "⚠️"
        elif percentage >= 85:
            return "✓"
        elif percentage >= 65:
            return "→"
        else:
            return "⚠️"

    @staticmethod
    def get_recommended_next_steps(percentage: float | None) -> str:
        """Generate recommended next steps based on performance."""
        if percentage is None:
            return "No observations recorded yet. Begin regular observations to track progress."

        if percentage >= 85:
            return ("Continue current strategies. Consider leadership opportunities for this student. "
                    "Monitor sustained performance and celebrate successes.")
        elif percentage >= 65:
            return ("Provide targeted support in focus areas. Schedule regular check-ins to monitor progress. "
                    "Celebrate strengths while addressing areas for growth.")
        else:
            return ("Immediate intervention recommended. Daily check-ins required. "
                    "Develop individualized support plan. Parent communication advised.")

    @staticmethod
    def format_percentage(percentage: float | None) -> str:
        """Format percentage for display."""
        if percentage is None:
            return "N/A"
        return f"{percentage:.1f}%"

    @staticmethod
    def validate_observation_value(value: str) -> bool:
        """Validate observation value ('1', '0', or '-')."""
        return value in ['1', '0', '-']

    @staticmethod
    async def calculate_performance(
        session: AsyncSession,
        student_id: str | None = None,
        class_code: str | None = None,
        measure: str | None = None
    ) -> tuple[float | None, int, int, int, int]:
        """
        Calculate performance % for observations.

        Returns: (percentage, ones_count, zeros_count, not_applicable_count, valid_count)
        """
        query = select(Observation)

        if student_id:
            query = query.where(Observation.student_id == student_id)
        if class_code:
            query = query.where(Observation.class_code == class_code)

        result = await session.execute(query)
        observations = result.scalars().all()

        if measure:
            normalized = CalculationService.normalize_measure_name(measure)
            observations = [
                o for o in observations
                if CalculationService.normalize_measure_name(o.measure_name) == normalized
            ]

        if not observations:
            return None, 0, 0, 0, 0

        ones = sum(1 for o in observations if o.value == '1')
        zeros = sum(1 for o in observations if o.value == '0')
        not_applicable = sum(1 for o in observations if o.value == '-')
        valid = ones + zeros

        if valid == 0:
            percentage = None
        else:
            percentage = (ones / valid) * 100

        return percentage, ones, zeros, not_applicable, valid

    @staticmethod
    async def get_days_absent(
        session: AsyncSession,
        student_id: str
    ) -> int:
        """Calculate days student was absent (all measures = '0')."""
        query = select(Observation).where(Observation.student_id == student_id)
        result = await session.execute(query)
        observations = result.scalars().all()

        if not observations:
            return 0

        dates_all_zeros = set()
        unique_dates = set(o.date for o in observations)

        for date in unique_dates:
            date_obs = [o for o in observations if o.date == date]
            if all(o.value == '0' for o in date_obs):
                dates_all_zeros.add(date)

        return len(dates_all_zeros)

    @staticmethod
    async def get_total_observation_days(
        session: AsyncSession,
        student_id: str
    ) -> int:
        """Get total unique observation dates."""
        query = select(func.count(func.distinct(Observation.date))).where(
            Observation.student_id == student_id
        )
        result = await session.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def calculate_attendance_rate(
        session: AsyncSession,
        student_id: str
    ) -> float | None:
        """Calculate attendance rate (present days / total days)."""
        total_days = await CalculationService.get_total_observation_days(session, student_id)

        if total_days == 0:
            return None

        absent_days = await CalculationService.get_days_absent(session, student_id)
        present_days = total_days - absent_days

        return (present_days / total_days) * 100

    @staticmethod
    async def get_days_since_last_observation(
        session: AsyncSession,
        student_id: str
    ) -> int | None:
        """Calculate days since last observation."""
        query = select(func.max(Observation.date)).where(
            Observation.student_id == student_id
        )
        result = await session.execute(query)
        last_date = result.scalar()

        if not last_date:
            return None

        today = datetime.now().date()
        return (today - last_date).days

    @staticmethod
    async def get_student_measure_breakdown(
        session: AsyncSession,
        student_id: str
    ) -> list[dict]:
        """Get measure-by-measure breakdown for a student."""
        breakdown = []

        for measure in ENGAGEMENT_MEASURES:
            perf, ones, zeros, not_applicable, valid = await CalculationService.calculate_performance(
                session, student_id=student_id, measure=measure
            )

            total = ones + zeros + not_applicable
            band_name, _ = CalculationService.get_performance_band(perf)

            breakdown.append({
                "measure": measure,
                "total": total,
                "ones_observed": ones,
                "zeros_not_observed": zeros,
                "not_applicable": not_applicable,
                "valid_observations": valid,
                "performance_percentage": perf,
                "band": band_name,
                "status": CalculationService.get_band_emoji(perf)
            })

        return breakdown

    @staticmethod
    def get_top_measures(
        measure_performance_dict: dict[str, float | None],
        n: int = 3
    ) -> list[tuple[str, float]]:
        """Return top N measures by performance %."""
        valid_measures = {k: v for k, v in measure_performance_dict.items() if v is not None}

        if not valid_measures:
            return []

        sorted_measures = sorted(valid_measures.items(), key=lambda x: x[1], reverse=True)
        return sorted_measures[:n]

    @staticmethod
    def get_improvement_areas(
        measure_performance_dict: dict[str, float | None],
        threshold: float = 75,
        n: int = 3
    ) -> list[tuple[str, float]]:
        """Return measures below threshold, sorted ascending."""
        below_threshold = {
            k: v for k, v in measure_performance_dict.items()
            if v is not None and v < threshold
        }

        if not below_threshold:
            return []

        sorted_measures = sorted(below_threshold.items(), key=lambda x: x[1])
        return sorted_measures[:n]
