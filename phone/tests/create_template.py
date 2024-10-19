import cv2

# Load the original image
img = cv2.imread('right.png')

# Convert the image to grayscale (helps with template matching)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Manually select the region of interest (ROI) where the symbol is located
# Here you will need to select the coordinates (x, y, width, height) manually
# Example coordinates (you need to adjust these)
x, y, w, h = 0, 0, 330, 330  # Adjust these values based on your image

# Crop the region of interest (ROI)
arrow_template = gray[y:y+h, x:x+w]

width = arrow_template.shape[1] // 4
height = arrow_template.shape[0] // 4
arrow_template = cv2.resize(arrow_template, (width, height), interpolation=cv2.INTER_AREA)
# Save the template as an image file (e.g., 'arrow_template.png')
cv2.imwrite('right_template.png', arrow_template)

# Display the template to confirm it's correctly extracted
# cv2.imshow('Arrow Template', arrow_template)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
