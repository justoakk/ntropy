"""
Gacha Probability Calculator

Calculates realistic probabilities for obtaining desired characters
considering pity system and 50/50 mechanics.
"""

from typing import Tuple
import math


class GachaProbabilityCalculator:
    """Calculator for gacha probabilities with pity and 50/50 system."""

    # Probability constants
    BASE_RATE = 0.006  # 0.600% for pulls 1-75
    SOFT_PITY_START = 76  # Soft pity starts at pull 76
    HARD_PITY = 90  # Guaranteed 5-star at pull 90

    # Soft pity cumulative probability (pulls 76-89)
    SOFT_PITY_TOTAL = 0.324  # ~32.4%

    def __init__(self):
        """Initialize the calculator."""
        pass

    def calculate_single_5star_probability(self, pulls: int, current_pity: int = 0) -> float:
        """
        Calculate probability of getting at least one 5-star within given pulls.

        Args:
            pulls: Number of pulls available
            current_pity: Current pity counter (0-89)

        Returns:
            Probability as decimal (0.0 to 1.0)
        """
        if pulls <= 0:
            return 0.0

        # Start from current pity
        pity = current_pity
        total_pulls = pulls

        # Probability of NOT getting a 5-star
        prob_no_5star = 1.0

        for pull in range(total_pulls):
            current_pull_number = pity + pull + 1

            # Hard pity - guaranteed
            if current_pull_number >= self.HARD_PITY:
                prob_no_5star = 0.0
                break

            # Calculate probability for this single pull
            if current_pull_number < self.SOFT_PITY_START:
                # Base rate (0.6%)
                prob_5star_this_pull = self.BASE_RATE
            else:
                # Soft pity (pulls 76-89)
                # Distribute the 32.4% across 14 pulls with increasing probability
                pulls_into_soft_pity = current_pull_number - self.SOFT_PITY_START
                # Linear increase in soft pity range
                prob_5star_this_pull = self.BASE_RATE + (pulls_into_soft_pity * 0.06)

            # Compound probability of NOT getting 5-star
            prob_no_5star *= (1.0 - prob_5star_this_pull)

        # Probability of getting at least one 5-star
        prob_at_least_one = 1.0 - prob_no_5star

        return min(prob_at_least_one, 1.0)

    def calculate_desired_character_probability(
        self,
        pulls: int,
        current_pity: int = 0,
        guaranteed: bool = False
    ) -> Tuple[float, str]:
        """
        Calculate probability of getting the desired character.

        Args:
            pulls: Number of pulls available
            current_pity: Current pity counter (0-89)
            guaranteed: Whether next 5-star is guaranteed to be featured character

        Returns:
            Tuple of (probability, explanation_text)
        """
        if pulls <= 0:
            return 0.0, "Sem pulls disponíveis"

        # Calculate how many potential 5-stars we can get
        max_possible_5stars = (pulls + current_pity) // self.HARD_PITY + 1

        # If guaranteed, it's simpler
        if guaranteed:
            # Just need to get one 5-star
            prob_5star = self.calculate_single_5star_probability(pulls, current_pity)
            explanation = "Estado: GARANTIDO (próximo 5★ é o personagem desejado)"
            return prob_5star, explanation

        # Not guaranteed - need to consider 50/50
        # This is more complex - we need to account for:
        # 1. Getting a 5-star on 50/50 (50% chance it's the character we want)
        # 2. If we lose 50/50, we need another 5-star (guaranteed)

        total_probability = 0.0
        explanation_parts = []

        # Scenario 1: Win the 50/50 on first 5-star
        prob_first_5star = self.calculate_single_5star_probability(pulls, current_pity)
        prob_win_5050 = prob_first_5star * 0.5
        total_probability += prob_win_5050
        explanation_parts.append(f"Ganhar 50/50: {prob_win_5050*100:.1f}%")

        # Scenario 2: Lose 50/50, then get guaranteed
        if pulls > (self.HARD_PITY - current_pity):
            # We have enough pulls to potentially get 2 five-stars
            prob_lose_5050 = prob_first_5star * 0.5

            # After losing 50/50, calculate remaining pulls
            remaining_pulls = pulls - (self.HARD_PITY - current_pity)

            # Probability of getting second 5-star (guaranteed)
            prob_second_5star = self.calculate_single_5star_probability(remaining_pulls, 0)

            prob_lose_then_win = prob_lose_5050 * prob_second_5star
            total_probability += prob_lose_then_win
            explanation_parts.append(f"Perder 50/50 → Garantido: {prob_lose_then_win*100:.1f}%")
        else:
            explanation_parts.append("Pulls insuficientes para garantido caso perca 50/50")

        explanation = "Estado: 50/50\n" + " + ".join(explanation_parts)

        return min(total_probability, 1.0), explanation

    def calculate_pulls_for_percentage(
        self,
        target_probability: float,
        current_pity: int = 0,
        guaranteed: bool = False
    ) -> int:
        """
        Calculate how many pulls needed to reach target probability.

        Args:
            target_probability: Desired probability (0.0 to 1.0)
            current_pity: Current pity counter
            guaranteed: Whether next 5-star is guaranteed

        Returns:
            Number of pulls needed
        """
        # Binary search for the number of pulls
        low, high = 0, 360  # Max 360 pulls (2x hard pity)

        while low < high:
            mid = (low + high) // 2
            prob, _ = self.calculate_desired_character_probability(mid, current_pity, guaranteed)

            if prob < target_probability:
                low = mid + 1
            else:
                high = mid

        return low

    def get_probability_explanation(
        self,
        pulls: int,
        current_pity: int = 0,
        guaranteed: bool = False
    ) -> dict:
        """
        Get detailed probability breakdown.

        Returns:
            Dictionary with probability info and explanations
        """
        prob, explanation = self.calculate_desired_character_probability(
            pulls, current_pity, guaranteed
        )

        # Calculate pulls to 50%, 75%, 90%, 99% confidence
        milestones = {}
        for target in [0.5, 0.75, 0.9, 0.99]:
            pulls_needed = self.calculate_pulls_for_percentage(target, current_pity, guaranteed)
            milestones[f"{int(target*100)}%"] = pulls_needed

        return {
            "probability": prob,
            "percentage": prob * 100,
            "explanation": explanation,
            "milestones": milestones,
            "guaranteed_pulls": self.HARD_PITY * (1 if guaranteed else 2) - current_pity
        }


# Singleton instance
_calculator = GachaProbabilityCalculator()


def get_calculator() -> GachaProbabilityCalculator:
    """Get the singleton calculator instance."""
    return _calculator
