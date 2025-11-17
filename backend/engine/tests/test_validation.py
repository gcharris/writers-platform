"""
Unit tests for validation system.

Run with:
    python3 -m pytest framework/tests/test_validation.py
or:
    python3 framework/tests/test_validation.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validation import BiLocationValidator, VoiceValidator, validate_scene


class TestBiLocationValidator:
    """Test bi-location validation."""

    def test_forbidden_jargon_detection(self):
        """Test detection of forbidden jargon."""
        validator = BiLocationValidator()

        # Test forbidden terms
        bad_text = "Mickey activated his quantum link and entered bi-location mode."
        result = validator.validate(bad_text)

        assert len(result.forbidden_jargon_found) > 0
        assert any('quantum link' in term.lower() for term in result.forbidden_jargon_found)
        assert result.validation_score < 8.0

    def test_correct_terms_detection(self):
        """Test detection of Mickey's correct terms."""
        validator = BiLocationValidator()

        good_text = """Through The Line, Noni detected corruption.
        The Tether between them transmitted patterns.
        The Shared Vein pulsed with toxicity."""

        result = validator.validate(good_text)

        assert "The Line" in result.correct_terms_used
        assert "The Tether" in result.correct_terms_used
        assert "The Shared Vein" in result.correct_terms_used
        assert result.validation_score >= 7.0

    def test_bi_location_showing(self):
        """Test detection of proper bi-location showing."""
        validator = BiLocationValidator()

        good_text = """Mickey's temples pulsed as his shadow split into three positions.
        His voice desynchronized mid-word, awareness telescoping between realities."""

        result = validator.validate(good_text)

        assert result.bi_location_shown_properly is True
        assert "Shows bi-location through physical strain" in '\n'.join(result.strengths)

    def test_technical_announcements(self):
        """Test detection of technical announcement violations."""
        validator = BiLocationValidator()

        bad_text = "Mickey split his consciousness and operated in dual consciousness mode."

        result = validator.validate(bad_text)

        assert len(result.issues) > 0
        assert any('Technical announcement' in issue for issue in result.issues)


class TestVoiceValidator:
    """Test voice authenticity validation."""

    def test_voice_markers(self):
        """Test detection of voice authenticity markers."""
        validator = VoiceValidator()

        good_text = """Tatami mats geometried themselves beneath Mickey's weight.
        His awareness refused to stay in one location, deeper than quantum
        transformation reached."""

        result = validator.validate_voice(good_text)

        assert result['voice_markers_found'] > 0
        assert result['voice_authenticity_score'] >= 7.0

    def test_anti_patterns(self):
        """Test detection of voice anti-patterns."""
        validator = VoiceValidator()

        bad_text = """It was clear that Mickey realized that he understood the situation.
        Obviously, the quantum mechanics were affecting his consciousness."""

        result = validator.validate_voice(bad_text)

        assert result['has_anti_patterns'] is True
        assert result['voice_authenticity_score'] < 7.0


class TestIntegration:
    """Integration tests for complete validation."""

    def test_complete_validation_good_scene(self):
        """Test complete validation on a good scene."""
        scene = """
        Mickey's temples pulsed—analog brain processing quantum data streams
        it wasn't designed to handle. Through The Line, Noni's morphic resonance
        detected patterns crystallizing. His shadow split into three positions
        as awareness telescoped between Pasadena and Shanghai.

        The Tether between them transmitted corruption frequency. Noni read the
        contamination like a spiritual practitioner recognizing ideological rot.
        Sleep debt accumulated across dimensions.
        """

        result = validate_scene(scene)

        assert len(result['bi_location']['forbidden_jargon_found']) == 0
        assert len(result['bi_location']['correct_terms_used']) >= 2
        assert result['bi_location']['bi_location_shown_properly'] is True
        assert result['overall_validation_score'] >= 7.0

    def test_complete_validation_bad_scene(self):
        """Test complete validation on a scene with issues."""
        scene = """
        It was clear that Mickey activated his quantum link and entered
        bi-location mode. His consciousness split between two realities as
        the quantum link enabled him to perceive both locations simultaneously.
        Obviously, this was a difficult cognitive task.
        """

        result = validate_scene(scene)

        assert len(result['bi_location']['forbidden_jargon_found']) > 0
        assert 'quantum link' in [term.lower() for term in result['bi_location']['forbidden_jargon_found']]
        assert len(result['bi_location']['issues']) > 0
        assert result['overall_validation_score'] < 5.0


def run_tests():
    """Run all tests manually (without pytest)."""
    print("Running validation tests...")
    print()

    test_classes = [TestBiLocationValidator(), TestVoiceValidator(), TestIntegration()]

    total_tests = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"Running {class_name}...")

        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    method = getattr(test_class, method_name)
                    method()
                    print(f"  ✓ {method_name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  ✗ {method_name}: {e}")
                    failed += 1
                except Exception as e:
                    print(f"  ✗ {method_name}: Unexpected error: {e}")
                    failed += 1

        print()

    print("=" * 60)
    print(f"Tests run: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
