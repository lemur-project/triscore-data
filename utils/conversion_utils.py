import os
import random
import cv2
import numpy as np
import verovio
from cairosvg import svg2png
import glob
import re
from math import ceil
import os

def clean_kern_file(kern_file, remove_intruments=False):
	with open(kern_file, 'r') as f:
		kern = f.read()
    
	# Use regex to find and remove lines containing LO:TX:a:t=PT&colon;N (N being a float)
	cleaned_kern = re.sub(r'!LO:TX:a:t=PT&colon;[\d\.]+', '!', kern)
	# Remove lines starting with '!!!'
	cleaned_kern = "\n".join(line for line in cleaned_kern.splitlines() if not line.startswith("!!!"))

	if remove_intruments:
		# remove any line that contain the mark *I (for instrument)
		# split by lines, and then by tabs, and then check if any of the elements in the line starts with *I
		cleaned_kern = "\n".join(
			line for line in cleaned_kern.splitlines() if not any(
				element.startswith('*I') for element in line.split('\t')
			)
		)

	# Write the cleaned kern file
	with open(kern_file, 'w') as f:
		f.write(cleaned_kern)
	return cleaned_kern


def find_image_cut(sample, margin_bot=40, margin_right=40):
	cut_height = None
	cut_width = None

	height, width = sample.shape[:2]

	for y in range(height - 1, -1, -1):
		if [0, 0, 0] in sample[y]:
			cut_height = y + margin_bot
			break

	for x in range(width - 1, -1, -1):
		if [0, 0, 0] in sample[:, x]:
			cut_width = x + margin_right
			break

	return cut_height, cut_width


def rfloat(start, end):
	return round(random.uniform(start, end), 2)


def krn2image(kern_file, image_folder, log_dir, debug=False):
	log_file = os.path.join(log_dir, 'krn2image.log')
	kern_file = str(kern_file)

	if debug:
		print(f'Rendering {kern_file}')
	
	filename = os.path.splitext(kern_file)[0] + '.png'
	if os.path.split(kern_file)[1][:1] == '.':
		print('Skipped')
		return filename + '\t skipped'
	
	# clean the kern file
	clean_kern_file(kern_file)

	vtk = verovio.toolkit()

	width = 10000
	height = ceil(width * 1.414)  # A4 aspect ratio
	vtk.setOptions({
		"pageWidth": width,
		"pageHeight": height,
		"scale": 60,
		"footer": 'none',
		'barLineWidth': rfloat(0.3, 0.8),
		'beamMaxSlope': rfloat(10, 20),
		'staffLineWidth': rfloat(0.1, 0.3),
		'spacingStaff': rfloat(4, 12)
	})

	try:
		vtk.loadFile(kern_file)
		svg_content = vtk.renderToSVG()
		svg_content = svg_content.replace("overflow=\"inherit\"", "overflow=\"visible\"")

		png_content = svg2png(bytestring=svg_content, background_color='white', dpi=300)
		png_data = np.frombuffer(png_content, np.uint8)
		png_img = cv2.imdecode(png_data, cv2.IMREAD_UNCHANGED)

		cut_height, cut_width = find_image_cut(png_img)
		if cut_height is not None:
			png_img = png_img[:cut_height, :]
		if cut_width is not None:
			png_img = png_img[:, :cut_width]

		image_filename = os.path.basename(filename)
		image_path = os.path.join(image_folder, image_filename)
		cv2.imwrite(image_path, png_img)
	except Exception as err:
		print(f'File {kern_file} raised unexpected error.')
		with open(log_file, 'a') as f:
			f.write(filename + '\t ERR ' + str(type(err)) + ': ' + str(err)[:100] + '\n')
		return filename + '\t ERR'

	print("Rendered successfully", kern_file)

	return png_img


def convert_dataset(ds_dir: str, log_dir: str):
	# convert all the krn files in the dataset folder
	kern_files = glob.glob(os.path.join(ds_dir, '**/*.krn'), recursive=True)
	for kern_file in kern_files:
		# get the dir of the krn file
		score_dir = os.path.dirname(kern_file)
		
		# convert to image
		krn2image(kern_file, score_dir, log_dir=log_dir)

	return log_dir