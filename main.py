import cv2, time, random
import numpy as np

def draw_transform():
	square = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
	C = np.array(coords).astype(np.float32)
	matrix = cv2.getPerspectiveTransform(C, np.array(square) * scale)

	img = cv2.warpPerspective(orig_img, matrix, orig_img.shape[0:2])

	'''
	# sharpening kernel
	kernel = np.array([[0, -1, 0],
					   [-1, 5,-1],
					   [0, -1, 0]])
	img = cv2.filter2D(img, -1, kernel)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	'''

	cv2.imshow('transformed', img)

def random_color():
	r = random.randint(0, 255)
	g = random.randint(0, 255)
	b = random.randint(0, 255)
	return (r, g, b)

def mouse_event(event, x, y, flags, param):
	#print('mouse event:', event, x, y, flags, param)
	# event = 1 -> mouse down
	# event = 4 -> mouse up
	if event != 4: return

	mouse = (x, y)

	# find closest
	mindist = 1e9
	closest = 0
	for coord_id in range(len(coords)):
		dist = np.linalg.norm( np.float32(coords[coord_id]) - mouse )
		if dist < mindist:
			closest = coord_id
			mindist = dist

	coords[closest] = mouse

	draw_outline()
	draw_transform()

def get_inital_outline_guess():
	out = None

	gray = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (13,13), 0)
	edged = cv2.Canny(gray, 60, 180)
	cv2.imshow('edged', edged)

	cnts = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = sorted(cnts[1], key = cv2.contourArea, reverse = True)[:3]

	for ii, cnt in enumerate(cnts):
		# P = cv2.arcLength(cnt, True)
		approx = cv2.approxPolyDP(cnt, 100, True)
		extremums = []
		for a in approx:
			npa = (a[0][0], a[0][1])
			for e in extremums:
				dist = np.linalg.norm( np.float32(npa) - np.float32(e) )
				if dist < 100: break
			else:
				extremums.append(npa)

		idk = orig_img.copy()
		cv2.drawContours(idk, [cnt], 0, random_color(), 3)
		cv2.drawContours(idk, [approx], 0, (255,0,0), 3)

		for e in extremums:
			cv2.circle(idk, (e[0], e[1]), 10, random_color(), -1)

		print(ii, len(extremums))
		if len(extremums) == 4:
			if out is None: out = extremums
			cv2.imshow('cnt' + str(ii), idk)

	return out

def draw_outline():
	'''
	idk = orig_img.copy()
	cv2.drawContours(idk, [cnt], 0, random_color, 3)
	cv2.imshow('cnt', idk)
	'''

	fdb_img = orig_img.copy()
	for ii, coord in enumerate(coords):
		cv2.circle(fdb_img, coord, 10, random_color(), -1)
		cv2.putText(fdb_img, str(ii), coord, cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,0,0))

	cv2.imshow('orig', fdb_img)

#orig_img = cv2.imread('./warranty.jpg')

#coords = [(188, 447), (655, 425), (951, 1052), (20, 1132)]

# main
'''
coords = get_inital_outline_guess()
if coords is None:
	coords = [(0, 0), (scale, 0), (scale, scale), (0, scale)]
draw_outline()
draw_transform()

cv2.setMouseCallback('orig', mouse_event)
'''

camera = cv2.VideoCapture(0)
while True:
	spam, orig_img = camera.read()
	cv2.imshow('orig', orig_img)
	scale = max(orig_img.shape[0], orig_img.shape[1])

	begin = time.time()
	coords = get_inital_outline_guess()
	try:
		draw_outline()
		draw_transform()
	except: pass
	print(f'took:{(time.time()-begin)*1000}ms')

	key = cv2.waitKey(10)
	if key == 113: break # Q
