"""
Intelligent Image Cropper Agent
Advanced cropping for product images with white backgrounds
Handles centering, sizing, and 1:1 ratio conversion
"""

from PIL import Image, ImageOps
import os
import numpy as np
from typing import Dict, Any, Optional, Tuple

class ImageCropperAgent:
    """
    Intelligent agent for cropping product images to 1:1 ratio
    Handles white backgrounds, auto-centering, and smart sizing
    """
    
    def __init__(self):
        """Initialize the intelligent image cropper agent"""
        pass
    
    def crop_to_square(self, image_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Intelligently crop product image to 1:1 ratio with auto-centering and sizing
        
        Args:
            image_path: Path to the input image
            output_path: Optional output path (if None, adds _cropped to filename)
        
        Returns:
            Dictionary containing the result
        """
        try:
            # Open the image
            image = Image.open(image_path)
            original_width, original_height = image.size
            
            # Step 1: Find the product boundaries (non-white areas)
            print("🔍 Step 1: Detecting product boundaries...")
            product_bounds = self._find_product_bounds(image)
            
            if not product_bounds:
                # If no product found, use basic cropping
                print("🔍 No product detected - using basic cropping")
                return self._basic_crop(image, image_path, output_path)
            
            print("🔍 Product detected - using intelligent cropping")
            
            # Step 2: Calculate optimal crop area
            print("🔍 Step 2: Calculating optimal crop area...")
            crop_area = self._calculate_optimal_crop(product_bounds, original_width, original_height)
            print(f"🔍 Calculated crop area: {crop_area}")
            
            # Step 3: Apply intelligent cropping
            print("🔍 Step 3: Applying intelligent crop...")
            cropped_image = self._apply_intelligent_crop(image, crop_area)
            
            # Step 4: Generate output path
            if output_path is None:
                # Create cropped_images directory
                cropped_dir = "cropped_images"
                os.makedirs(cropped_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                extension = os.path.splitext(image_path)[1]
                output_path = os.path.join(cropped_dir, f"{base_name}_cropped{extension}")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Save the cropped image
            cropped_image.save(output_path, quality=95)
            
            return {
                "success": True,
                "message": f"Intelligently cropped to 1:1 ratio",
                "output_path": output_path,
                "original_dimensions": (original_width, original_height),
                "cropped_dimensions": cropped_image.size,
                "product_bounds": product_bounds,
                "crop_area": crop_area,
                "crop_applied": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_path": None,
                "crop_applied": False
            }
    
    def _find_product_bounds(self, image: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """
        Find the bounding box of the product (non-white areas)
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (left, top, right, bottom) or None if no product found
        """
        # Convert to numpy array for processing
        img_array = np.array(image)
        
        # Convert to grayscale for easier processing
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
        
        # Debug: Print some statistics
        print(f"🔍 Debug: Image shape: {img_array.shape}")
        print(f"🔍 Debug: Gray values range: {gray.min()} to {gray.max()}")
        
        # Find non-white pixels (assuming white background)
        # Use a threshold slightly below 255 to account for compression artifacts
        non_white_mask = gray < 240
        
        print(f"🔍 Debug: Non-white pixels found: {np.sum(non_white_mask)} out of {gray.size}")
        
        if not np.any(non_white_mask):
            print("🔍 Debug: No non-white pixels found - using basic crop")
            return None
        
        # Find bounding box of non-white pixels
        rows = np.any(non_white_mask, axis=1)
        cols = np.any(non_white_mask, axis=0)
        
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        bounds = (x_min, y_min, x_max + 1, y_max + 1)
        print(f"🔍 Debug: Product bounds detected: {bounds}")
        
        return bounds
    
    def _calculate_optimal_crop(self, product_bounds: Tuple[int, int, int, int], 
                               width: int, height: int) -> Tuple[int, int, int, int]:
        """
        Calculate optimal crop area that centers the product and creates 1:1 ratio
        
        Args:
            product_bounds: Product bounding box (left, top, right, bottom)
            width: Image width
            height: Image height
            
        Returns:
            Crop area as (left, top, right, bottom)
        """
        left, top, right, bottom = product_bounds
        product_width = right - left
        product_height = bottom - top
        
        # Calculate the size of the square crop
        # Use the larger dimension to ensure the product fits
        max_dimension = max(product_width, product_height)
        
        # Add padding around the product (20% of product size)
        padding = int(max_dimension * 0.2)
        crop_size = max_dimension + (2 * padding)
        
        # Center the crop around the product
        product_center_x = (left + right) // 2
        product_center_y = (top + bottom) // 2
        
        # Calculate crop boundaries
        crop_left = max(0, product_center_x - crop_size // 2)
        crop_top = max(0, product_center_y - crop_size // 2)
        crop_right = min(width, crop_left + crop_size)
        crop_bottom = min(height, crop_top + crop_size)
        
        # Adjust if we hit image boundaries
        if crop_right - crop_left < crop_size:
            crop_left = max(0, crop_right - crop_size)
        if crop_bottom - crop_top < crop_size:
            crop_top = max(0, crop_bottom - crop_size)
        
        return (crop_left, crop_top, crop_right, crop_bottom)
    
    def _apply_intelligent_crop(self, image: Image.Image, crop_area: Tuple[int, int, int, int]) -> Image.Image:
        """
        Apply the intelligent crop and ensure 1:1 ratio
        
        Args:
            image: PIL Image object
            crop_area: Crop area as (left, top, right, bottom)
            
        Returns:
            Cropped and resized image
        """
        # Apply the crop
        cropped = image.crop(crop_area)
        
        # Ensure it's square by resizing to the smaller dimension
        width, height = cropped.size
        size = min(width, height)
        
        # Center crop to exact square
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        final_crop = cropped.crop((left, top, right, bottom))
        
        return final_crop
    
    def _basic_crop(self, image: Image.Image, image_path: str, output_path: Optional[str]) -> Dict[str, Any]:
        """
        Fallback to basic cropping if product detection fails
        
        Args:
            image: PIL Image object
            image_path: Original image path
            output_path: Output path
            
        Returns:
            Result dictionary
        """
        width, height = image.size
        
        # Basic center crop
        if width > height:
            new_size = height
            left = (width - new_size) // 2
            top = 0
            right = left + new_size
            bottom = height
        elif height > width:
            new_size = width
            left = 0
            top = (height - new_size) // 2
            right = width
            bottom = top + new_size
        else:
            # Already square
            if output_path is None:
                # Create cropped_images directory
                cropped_dir = "cropped_images"
                os.makedirs(cropped_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                extension = os.path.splitext(image_path)[1]
                output_path = os.path.join(cropped_dir, f"{base_name}_cropped{extension}")
            
            image.save(output_path, quality=95)
            return {
                "success": True,
                "message": "Image is already square (1:1 ratio)",
                "output_path": output_path,
                "original_dimensions": (width, height),
                "cropped_dimensions": (width, height),
                "crop_applied": False
            }
        
        # Apply basic crop
        cropped_image = image.crop((left, top, right, bottom))
        
        # Generate output path if not provided
        if output_path is None:
            # Create cropped_images directory
            cropped_dir = "cropped_images"
            os.makedirs(cropped_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            extension = os.path.splitext(image_path)[1]
            output_path = os.path.join(cropped_dir, f"{base_name}_cropped{extension}")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save the cropped image
        cropped_image.save(output_path, quality=95)
        
        return {
            "success": True,
            "message": f"Basic crop to 1:1 ratio ({new_size}x{new_size})",
            "output_path": output_path,
            "original_dimensions": (width, height),
            "cropped_dimensions": (new_size, new_size),
            "crop_applied": True,
            "crop_coordinates": (left, top, right, bottom)
        }
    
    def crop_multiple_images(self, image_paths: list, output_dir: str = "cropped_images") -> Dict[str, Any]:
        """
        Crop multiple images to 1:1 ratio
        
        Args:
            image_paths: List of image paths
            output_dir: Directory to save cropped images
        
        Returns:
            Dictionary containing results for all images
        """
        results = []
        successful_crops = 0
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        for i, image_path in enumerate(image_paths):
            try:
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                extension = os.path.splitext(image_path)[1]
                output_path = os.path.join(output_dir, f"{base_name}_cropped{extension}")
                
                # Crop the image
                result = self.crop_to_square(image_path, output_path)
                results.append({
                    "image_path": image_path,
                    "result": result
                })
                
                if result["success"]:
                    successful_crops += 1
                    
            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "result": {
                        "success": False,
                        "error": str(e)
                    }
                })
        
        return {
            "success": successful_crops > 0,
            "total_images": len(image_paths),
            "successful_crops": successful_crops,
            "failed_crops": len(image_paths) - successful_crops,
            "results": results,
            "output_directory": output_dir
        }
