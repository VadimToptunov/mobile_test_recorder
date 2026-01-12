"""
Visual analyzer for mobile applications

Detects visual regressions and UI inconsistencies.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path


@dataclass
class VisualDiff:
    """Represents a visual difference"""
    screen_name: str
    baseline_image: Path
    current_image: Path
    diff_percentage: float  # 0-100
    diff_regions: List[Tuple[int, int, int, int]]  # (x, y, width, height)
    threshold: float = 0.01  # 1% default threshold

    @property
    def has_regression(self) -> bool:
        return self.diff_percentage > (self.threshold * 100)


class VisualAnalyzer:
    """
    Analyzes visual differences between app screens
    """

    def __init__(self, baseline_dir: Path):
        """
        Initialize visual analyzer

        Args:
            baseline_dir: Directory containing baseline screenshots
        """
        self.baseline_dir = baseline_dir
        self.diffs: List[VisualDiff] = []

    def compare_screenshots(
        self,
        screen_name: str,
        current_image: Path,
        threshold: float = 0.01
    ) -> Optional[VisualDiff]:
        """
        Compare current screenshot with baseline

        Args:
            screen_name: Name of the screen
            current_image: Path to current screenshot
            threshold: Difference threshold (0.01 = 1%)

        Returns:
            VisualDiff if differences found, None otherwise
        """
        baseline_image = self.baseline_dir / f"{screen_name}.png"

        if not baseline_image.exists():
            print(f"Warning: No baseline for {screen_name}, creating new baseline")
            self._create_baseline(screen_name, current_image)
            return None

        if not current_image.exists():
            print(f"Error: Current image not found: {current_image}")
            return None

        # Compare images (simplified - in production use pillow/opencv)
        diff_percentage = self._calculate_diff(baseline_image, current_image)
        diff_regions = self._find_diff_regions(baseline_image, current_image)

        diff = VisualDiff(
            screen_name=screen_name,
            baseline_image=baseline_image,
            current_image=current_image,
            diff_percentage=diff_percentage,
            diff_regions=diff_regions,
            threshold=threshold
        )

        if diff.has_regression:
            self.diffs.append(diff)

        return diff

    def _calculate_diff(self, baseline: Path, current: Path) -> float:
        """
        Calculate percentage difference between images

        Note: This is a placeholder. In production, use:
        - PIL/Pillow for image loading
        - numpy for pixel comparison
        - opencv for advanced comparison
        """
        try:
            # Simplified: compare file sizes as proxy
            baseline_size = baseline.stat().st_size
            current_size = current.stat().st_size

            if baseline_size == 0:
                return 100.0

            size_diff = abs(current_size - baseline_size) / baseline_size
            return min(size_diff * 100, 100.0)

        except Exception:
            return 0.0

    def _find_diff_regions(
        self,
        baseline: Path,
        current: Path
    ) -> List[Tuple[int, int, int, int]]:
        """
        Find regions with visual differences

        Returns:
            List of (x, y, width, height) tuples
        """
        # Placeholder - in production use image diff algorithms
        return []

    def _create_baseline(self, screen_name: str, image: Path) -> None:
        """Create new baseline image"""
        import shutil

        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        baseline_path = self.baseline_dir / f"{screen_name}.png"

        try:
            shutil.copy(image, baseline_path)
            print(f"Created baseline: {baseline_path}")
        except Exception as e:
            print(f"Error creating baseline: {e}")

    def update_baseline(self, screen_name: str, current_image: Path) -> None:
        """Update baseline with current image"""
        self._create_baseline(screen_name, current_image)

    def batch_compare(
        self,
        screenshots_dir: Path,
        threshold: float = 0.01
    ) -> List[VisualDiff]:
        """
        Compare all screenshots in directory with baselines

        Args:
            screenshots_dir: Directory containing current screenshots
            threshold: Difference threshold

        Returns:
            List of visual diffs with regressions
        """
        regressions = []

        for screenshot in screenshots_dir.glob('*.png'):
            screen_name = screenshot.stem
            diff = self.compare_screenshots(screen_name, screenshot, threshold)

            if diff and diff.has_regression:
                regressions.append(diff)

        return regressions

    def generate_report(self) -> str:
        """Generate visual regression report"""
        report = "VISUAL REGRESSION REPORT\n"
        report += "=" * 80 + "\n\n"

        if not self.diffs:
            report += "No visual regressions detected.\n"
            return report

        report += f"Found {len(self.diffs)} visual regression(s):\n\n"

        for diff in self.diffs:
            report += f"Screen: {diff.screen_name}\n"
            report += f"  Difference: {diff.diff_percentage:.2f}%\n"
            report += f"  Threshold: {diff.threshold * 100:.2f}%\n"
            report += f"  Baseline: {diff.baseline_image}\n"
            report += f"  Current: {diff.current_image}\n"
            if diff.diff_regions:
                report += f"  Changed regions: {len(diff.diff_regions)}\n"
            report += "\n"

        report += "=" * 80 + "\n"

        return report

    def export_diff_images(self, output_dir: Path) -> None:
        """
        Export visual diff images

        Args:
            output_dir: Directory to save diff images
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for diff in self.diffs:
            # In production: create visual diff image with highlighted regions
            # For now, just copy current image
            import shutil

            output_path = output_dir / f"{diff.screen_name}_diff.png"
            try:
                shutil.copy(diff.current_image, output_path)
                print(f"Exported diff: {output_path}")
            except Exception as e:
                print(f"Error exporting diff: {e}")
