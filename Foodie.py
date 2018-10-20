import cv2
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from tkinter import *
from PIL import ImageTk, Image
import http.client
import requests
import pprint
import json

def main3():
    text1 = "orange"
    text2 = "Big round citrus fruit".replace(' ', '%20')
    token = open('./keys/dandelion_key').read()
    base = 'https://api.dandelion.eu/datatxt/sim/v1?text1={}&text2={}&token={}'.format(text1, text2, token)
    print(base)

    # s = requests.get(base)
    # print(s.json())


def get_catalog():
    conn = http.client.HTTPSConnection("gateway-staging.ncrcloud.com")

    key = open('./keys/ncr_key').read()
    auth = open('./keys/ncr_auth').read()

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'nep-organization': "ncr-market",
        'nep-application-key': key,
        'Authorization': auth,
        'nep-service-version': '2.2.1:2'
    }

    conn.request("GET", "/catalog/items/snapshot", headers=headers)

    res = conn.getresponse()

    data = res.read()
    data = data.decode("utf-8")
    data = json.loads(data)

    entries = [(data['snapshot'][i]['itemId']['itemCode'],
                data['snapshot'][i]['longDescription']['values'][0]['value'])
               for i in range(len(data['snapshot']))]

    items = []
    id_map = dict()
    for idd, name in entries:
        items.append(name)
        id_map[name] = int(idd)

    return items, id_map

def main():
    im_file = './milk_display.jpg'

    def close_element(element, trigger):
        element.destroy()
        trigger[0] = False

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    trigger = [True]
    while ret and trigger[0]:
        cv2.imshow("Camera", frame)
        k = cv2.waitKey(20)
        if k == ord('q'):
            root = Tk()
            canvas = Canvas(root, width=300, height=300)
            canvas.pack()
            img = ImageTk.PhotoImage(Image.open(im_file))
            canvas.create_image(20, 20, anchor=NW, image=img)
            b = Button(root, text='Confirm', command=lambda: close_element(root, trigger))
            b.pack()
            root.mainloop()
        ret, frame = cap.read()
    cv2.destroyAllWindows()
    cap.release()

    key = open('./keys/clarifai_key').read()
    app = ClarifaiApp(api_key=key)

    model = app.models.get('food-items-v1.0')
    # model = app.models.get('general-v1.3')
    image = ClImage(file_obj=open(im_file, 'rb'))
    resp = model.predict([image])
    tags = [(resp['outputs'][0]['data']['concepts'][i]['name'],
             resp['outputs'][0]['data']['concepts'][i]['value'])
            for i in range(len(resp['outputs'][0]['data']['concepts']))]

    def on_select(event, select_list):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        select_list.append(value)
        print(value)

    selected = []

    root = Tk()
    canvas = Canvas(root, width=300, height=300)
    canvas.pack()
    img = ImageTk.PhotoImage(Image.open(im_file))
    canvas.create_image(20, 20, anchor=NW, image=img)
    listbox = Listbox(root)
    listbox.bind('<<ListboxSelect>>', lambda x: on_select(x, selected))
    listbox.pack()
    for item in tags:
        listbox.insert(END, item[0])
    root.mainloop()

    # FILTER
    print(selected)
    tag_names = selected if len(selected) > 0 else tags[0][0]
    items, id_map = get_catalog()
    relevent = []
    for i in range(len(items)):
        for name in tag_names:
            if name in items[i]:
                relevent.append(items[i])
                continue

    root = Tk()
    canvas = Canvas(root, width=300, height=300)
    canvas.pack()
    img = ImageTk.PhotoImage(Image.open(im_file))
    canvas.create_image(20, 20, anchor=NW, image=img)
    listbox = Listbox(root, height=15, width=50, selectmode='SINGLE')
    listbox.pack()
    for item in relevent:
        listbox.insert(END, item)
    root.mainloop()

    # pp = pprint.PrettyPrinter(depth=4)
    # pp.pprint(tag_names)
    # pp.pprint(relevent)


if __name__ == '__main__':
    main()