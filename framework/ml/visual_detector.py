"""
Visual element detector using computer vision and OCR.

Provides screenshot-based element identification and visual regression testing capabilities.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - OCR functionality disabled")


class VisualDetector:
    """
    Visual element detection using computer vision.

    Features:
    - Screenshot capture and processing
    - Image similarity matching
    - OCR text extraction
    - Visual regression detection
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize visual detector.

        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        self.tesseract_path = tesseract_path

        if TESSERACT_AVAILABLE and tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def extract_text_from_image(
        self,
        image_path: Path,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> str:
        """
        Extract text from image using OCR.

        Args:
            image_path: Path to screenshot
            region: Optional (x, y, width, height) region to extract

        Returns:
            Extracted text
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract not available")

        # Load image
        image = Image.open(image_path)

        # Crop to region if specified
        if region:
            x, y, w, h = region
            image = image.crop((x, y, x + w, y + h))

        # Extract text
        text = pytesseract.image_to_string(image)

        return text.strip()

    def find_element_by_image(
        self,
        screenshot_path: Path,
        template_path: Path,
        threshold: float = 0.8
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Find element in screenshot by template matching.

        Args:
            screenshot_path: Path to full screenshot
            template_path: Path to element template image
            threshold: Matching threshold (0.0-1.0)

        Returns:
            (x, y, width, height) of matched region or None
        """
        # Load images
        screenshot = cv2.imread(str(screenshot_path))
        template = cv2.imread(str(template_path))

        if screenshot is None or template is None:
            logger.error("Failed to load images")
            return None

        # Convert to grayscale
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Template matching
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # Find best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            logger.debug(f"No match found (max confidence: {max_val:.2f})")
            return None

        # Get template size
        h, w = template_gray.shape

        # Return match location
        x, y = max_loc
        return (x, y, w, h)

    def calculate_image_similarity(
        self,
        image1_path: Path,
        image2_path: Path,
        method: str = 'ssim'
    ) -> float:
        """
        Calculate similarity between two images.

        Args:
            image1_path: First image
            image2_path: Second image
            method: Similarity method ('ssim', 'mse', 'histogram')

        Returns:
            Similarity score (0.0-1.0)
        """
        # Load images
        img1 = cv2.imread(str(image1_path))
        img2 = cv2.imread(str(image2_path))

        if img1 is None or img2 is None:
            raise ValueError("Failed to load images")

        # Resize to same dimensions
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        if method == 'mse':
            # Mean Squared Error (lower is better)
            mse = np.mean((img1 - img2) ** 2)
            # Normalize to 0-1 (1 = identical)
            max_mse = 255.0 ** 2
            similarity = 1.0 - (mse / max_mse)
            return float(similarity)

        elif method == 'histogram':
            # Histogram comparison
            hist1 = cv2.calcHist([img1], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([img2], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])

            cv2.normalize(hist1, hist1)
            cv2.normalize(hist2, hist2)

            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return float(similarity)

        elif method == 'ssim':
            # Structural Similarity Index
            try:
                from skimage.metrics import structural_similarity as ssim

                # Convert to grayscale
                gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

                similarity = ssim(gray1, gray2)
                return float(similarity)
            except ImportError:
                logger.warning("scikit-image not available, falling back to MSE")
                return self.calculate_image_similarity(image1_path, image2_path, method='mse')

        else:
            raise ValueError(f"Unknown method: {method}")

    def detect_visual_changes(
        self,
        baseline_path: Path,
        current_path: Path,
        threshold: float = 0.95
    ) -> Tuple[bool, float, Optional[np.ndarray]]:
        """
        Detect visual regression between baseline and current screenshot.

        Args:
            baseline_path: Baseline screenshot
            current_path: Current screenshot
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            (has_changes, similarity_score, diff_image)
        """
        # Calculate similarity
        similarity = self.calculate_image_similarity(baseline_path, current_path, method='ssim')

        has_changes = similarity < threshold

        # Generate diff image if changes detected
        diff_image = None
        if has_changes:
            img1 = cv2.imread(str(baseline_path))
            img2 = cv2.imread(str(current_path))

            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

            # Compute absolute difference
            diff_image = cv2.absdiff(img1, img2)

            # Threshold to highlight differences
            gray_diff = cv2.cvtColor(diff_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

            # Highlight differences in red
            diff_image[thresh > 0] = [0, 0, 255]

        return has_changes, similarity, diff_image

    def save_visual_diff(
        self,
        diff_image: np.ndarray,
        output_path: Path
    ):
        """Save visual diff image to disk."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), diff_image)
        logger.info(f"Visual diff saved to {output_path}")

    def extract_element_screenshot(
        self,
        screenshot_path: Path,
        bounds: Tuple[int, int, int, int],
        output_path: Path
    ):
        """
        Extract element region from screenshot.

        Args:
            screenshot_path: Full screenshot
            bounds: (x, y, width, height)
            output_path: Where to save extracted image
        """
        image = Image.open(screenshot_path)
        x, y, w, h = bounds
        element_image = image.crop((x, y, x + w, y + h))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        element_image.save(output_path)
        logger.debug(f"Element screenshot saved to {output_path}")
