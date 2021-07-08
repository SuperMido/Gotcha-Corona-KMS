import asyncio

import cv2
import numpy as np
import websockets
import base64
import json
import os

CORONA_1 = os.path.dirname(os.path.abspath(__file__)) + '/corona1.png'
CORONA_2 = os.path.dirname(os.path.abspath(__file__)) + '/corona2.png'
CORONA_3 = os.path.dirname(os.path.abspath(__file__)) + '/corona3.png'
CORONA_4 = os.path.dirname(os.path.abspath(__file__)) + '/corona4.png'
CORONA_5 = os.path.dirname(os.path.abspath(__file__)) + '/corona5.png'
CORONA_6 = os.path.dirname(os.path.abspath(__file__)) + '/corona6.png'
CORONA_7 = os.path.dirname(os.path.abspath(__file__)) + '/corona7.png'
# Not use
# CORONA_8 = os.path.dirname(os.path.abspath(__file__)) + '/corona8.png'
# CORONA_9 = os.path.dirname(os.path.abspath(__file__)) + '/corona9.png'
CORONA_10 = os.path.dirname(os.path.abspath(__file__)) + '/corona10.png'
# Queen
# CORONA_11 = os.path.dirname(os.path.abspath(__file__)) + '/corona11.png'
# CORONA_12 = os.path.dirname(os.path.abspath(__file__)) + '/corona12.png'
CORONA_SCALE_RATIO = 0.5

corona_template_image_1 = cv2.imread(CORONA_1, 0)
corona_template_image_2 = cv2.imread(CORONA_2, 0)
corona_template_image_3 = cv2.imread(CORONA_3, 0)
corona_template_image_4 = cv2.imread(CORONA_4, 0)
corona_template_image_5 = cv2.imread(CORONA_5, 0)
corona_template_image_6 = cv2.imread(CORONA_6, 0)
corona_template_image_7 = cv2.imread(CORONA_7, 0)
# Not use
# corona_template_image_8 = cv2.imread(CORONA_8, 0)
# corona_template_image_9 = cv2.imread(CORONA_9, 0)
corona_template_image_10 = cv2.imread(CORONA_10, 0)
# Queen
# corona_template_image_11 = cv2.imread(CORONA_11, 0)
# corona_template_image_12 = cv2.imread(CORONA_12, 0)

corona_template_image_1 = cv2.resize(corona_template_image_1, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_2 = cv2.resize(corona_template_image_2, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_3 = cv2.resize(corona_template_image_3, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_4 = cv2.resize(corona_template_image_4, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_5 = cv2.resize(corona_template_image_5, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_6 = cv2.resize(corona_template_image_6, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_7 = cv2.resize(corona_template_image_7, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# Not use
# corona_template_image_8 = cv2.resize(corona_template_image_8, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_9 = cv2.resize(corona_template_image_9, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
corona_template_image_10 = cv2.resize(corona_template_image_10, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# Queen
# corona_template_image_11 = cv2.resize(corona_template_image_11, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_12 = cv2.resize(corona_template_image_12, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)

corona_template = []
corona_template.append(corona_template_image_1)
corona_template.append(corona_template_image_2)
corona_template.append(corona_template_image_3)
corona_template.append(corona_template_image_4)
corona_template.append(corona_template_image_5)
corona_template.append(corona_template_image_6)
corona_template.append(corona_template_image_7)
# corona_template.append(corona_template_image_8)
# corona_template.append(corona_template_image_9)
corona_template.append(corona_template_image_10)
# Queen
# corona_template.append(corona_template_image_11)
# corona_template.append(corona_template_image_12)

def catch_corona(wave_image, threshold=0.8):
    wave_image_gray = cv2.cvtColor(wave_image, cv2.COLOR_BGR2GRAY)
    result = [[]]

    for image in corona_template:
        res = cv2.matchTemplate(wave_image_gray, image, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val < threshold:
            return []

        width, height = image.shape[::-1]
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)
        result.append([[top_left, bottom_right]])

    return result

def base64_to_image(base64_data):
    encoded_data = base64_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    return img

async def play_game(websocket, path):
    print('Corona Killer is ready to play!')
    catchings = []
    last_round_id = ''
    wave_count = 0
    
    while True:

        ### receive a socket message (wave)
        try:
            data = await websocket.recv()
        except Exception as e:
            print('Error: ' + e)
            break

        json_data = json.loads(data)

        ### check if starting a new round
        if json_data["roundId"] != last_round_id:
            print(f'> Catching corona for round {json_data["roundId"]}...')
            last_round_id = json_data["roundId"]

        ### catch corona in a wave image
        wave_image = base64_to_image(json_data['base64Image'])
        results = catch_corona(wave_image)

        ### save result image file for debugging purpose
        for result in results:
            for res in result:
                cv2.rectangle(wave_image, res[0], res[1], (0, 0, 255), 2)
            

        waves_dir = f'waves/{last_round_id}/'
        if not os.path.exists(waves_dir):
            os.makedirs(waves_dir)
            

        print(f'>>> Wave #{wave_count:03d}: {json_data["waveId"]}')
        wave_count = wave_count + 1

        ### store catching positions in the list
        for result in results:
            for res in result:
                catchings.append({
                    "positions": [
                        {
                            "x": (res[0][0] + res[1][0]) / 2, 
                            "y": (res[0][1] + res[1][1]) / 2
                        }
                    ],
                    "waveId": json_data["waveId"]
                })

        ### send result to websocket if it is the last wave
        if json_data["isLastWave"]:
            round_id = json_data["roundId"]
            print(f'> Submitting result for round {round_id}...')

            json_result = {
                "roundId": round_id,
                "catchings": catchings,
            }

            await websocket.send(json.dumps(json_result))
            print('> Submitted.')

            catchings = []
            wave_count = 0


start_server = websockets.serve(play_game, "localhost", 8765, max_size=100000000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()