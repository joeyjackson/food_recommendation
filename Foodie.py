import cv2
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from tkinter import *
from PIL import ImageTk, Image
import http.client
import json
import simplejson
import time


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
    name_to_id_map = dict()
    id_to_name_map = dict()
    for idd, name in entries:
        items.append(name)
        name_to_id_map[name] = int(idd)
        id_to_name_map[int(idd)] = name
    return items, name_to_id_map, id_to_name_map


def getCost(item_id):
    conn = http.client.HTTPSConnection("gateway-staging.ncrcloud.com")
    key = open('./keys/ncr_key').read()
    auth = open('./keys/ncr_auth').read()
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'nep-organization': "ncr-market",
        'nep-application-key': key,
        'Authorization': auth,
        'nep-enterprise-unit': '7c54465e9f5344598276ec1f941f5a3c',
        'nep-service-version': '2.2.1:2'
    }
    conn.request("GET", "/catalog/item-prices/{}/1/".format(item_id), headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    data = json.loads(data)

    return float(data['price'])


def get_transactions(cache=False):
    if cache:
        with open('transactions.json', 'r') as f:
            the_json = json.loads(f.read())
        return the_json
    conn = http.client.HTTPSConnection("gateway-staging.ncrcloud.com")
    key = open('./keys/ncr_key').read()
    auth = open('./keys/ncr_auth').read()
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'nep-organization': "ncr-market",
        'nep-application-key': key,
        'Authorization': auth,
        'nep-service-version': '2.2.0:2'
    }
    payload = json.dumps({"transactionTypes": ["SALES"]})
    conn.request("POST", "/transaction-document/transaction-documents/find/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    data = json.loads(data)
    transaction_ids = [data['pageContent'][i]['tlogId'] for i in range(len(data['pageContent']))]
    transactions = []
    for idd in transaction_ids:
        conn.request("GET", "/transaction-document/transaction-documents/{}".format(idd),
                     headers=headers)
        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        data = json.loads(data)
        transaction = set()
        for i in range(len(data['tlog']['items'])):
            item_id = data['tlog']['items'][i]['productId']
            if item_id is not None and item_id.isdigit():
                transaction.add(item_id)
        if len(transaction) > 0:
            transactions.append(list(transaction))
    the_json = {"transactions": transactions}

    # Cache
    with open('transactions.json', 'w') as outfile:
        outfile.write(simplejson.dumps(the_json, indent=4))

    return the_json


def image_resize(im, height=None, width=None):
    if height is None and width is None:
        return im.copy()
    elif width is not None and height is not None:
        return cv2.resize(im, (height, width))
    elif width is None:
        ratio = int(float(im.shape[0]) / float(im.shape[1]) * height)
        return cv2.resize(im, (height, ratio))
    else: #right is None
        ratio = int(float(im.shape[1]) / float(im.shape[0]) * width)
        return cv2.resize(im, (ratio, width))


def camera_screen():
    cv2.namedWindow("My Application")
    cv2.resizeWindow("My Application", 300, 500)
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    taken = frame
    while ret:
        cv2.imshow("My Application", image_resize(frame, width=250))
        cv2.resizeWindow("My Application", 300, 500)
        k = cv2.waitKey(20)
        if k == ord('q'):
            taken = frame
            break
        ret, frame = cap.read()
    cv2.destroyAllWindows()
    cap.release()
    return taken


def clear_window(window):
    _list = window.winfo_children()
    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())
    for item in _list:
        item.destroy()


def confirm_screen(root, im_file):
    clear_window(root)
    img = Image.open(im_file)
    img = img.resize((300, int(float(img.height) / img.width * 300)))
    img = ImageTk.PhotoImage(img)
    label = Label(image=img)
    label.image = img
    label.pack()
    # canvas = Canvas(root, width=img.width(), height=img.height())
    # canvas.pack()
    # canvas.create_image(0, 0, anchor=NW, image=img)
    b = Button(root, text='Confirm', command=lambda: tags_screen(root, im_file))
    b.pack()


def tags_screen(root, im_file):
    key = open('./keys/clarifai_key').read()
    app = ClarifaiApp(api_key=key)
    model = app.models.get('food-items-v1.0')
    # model = app.models.get('general-v1.3')
    image = ClImage(file_obj=open(im_file, 'rb'))
    resp = model.predict([image])
    tags = [(resp['outputs'][0]['data']['concepts'][i]['name'],
             resp['outputs'][0]['data']['concepts'][i]['value'])
            for i in range(len(resp['outputs'][0]['data']['concepts']))]
    clear_window(root)
    def on_select(event, select_set):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        select_set.add(value)
    selected = set()
    img = Image.open(im_file)
    img = img.resize((300, int(float(img.height) / img.width * 300)))
    img = ImageTk.PhotoImage(img)
    label = Label(image=img)
    label.image = img
    label.pack()
    # canvas = Canvas(root, width=img.width(), height=img.height())
    # canvas.pack()
    # canvas.create_image(0, 0, anchor=NW, image=img)
    listbox = Listbox(root)
    listbox.bind('<<ListboxSelect>>', lambda x: on_select(x, selected))
    for item in tags:
        listbox.insert(END, item[0])
    listbox.pack()
    b = Button(root, text='Done', command=lambda: catalog_screen(root, selected, tags, im_file))
    b.pack()


def catalog_screen(root, selected, tags, im_file):
    clear_window(root)
    transactions = get_transactions(cache=True)
    valid_ids = set()
    for transaction in transactions['transactions']:
        for t in transaction:
            valid_ids.add(t)
    # FILTER
    tag_names = selected if len(selected) > 0 else [tags[0][0]]
    items, name_to_id_map, id_to_name_map = get_catalog()
    relevent = []
    for i in range(len(items)):
        for name in tag_names:
            if name.lower() in items[i].lower() and str(name_to_id_map[items[i]]) in valid_ids:  # Hacky
                relevent.append(items[i])
                continue
    img = Image.open(im_file)
    img = img.resize((300, int(float(img.height) / img.width * 300)))
    img = ImageTk.PhotoImage(img)
    label = Label(image=img)
    label.image = img
    label.pack()
    # canvas = Canvas(root, width=img.width(), height=img.height())
    # canvas.pack()
    # canvas.create_image(0, 0, anchor=NW, image=img)
    if len(relevent) == 0:
        notif = Label(root, text='No Items in the Catalog Match the Tags')
        notif.pack()
    listbox = Listbox(root, height=15, width=50, selectmode='SINGLE')
    listbox.bind('<<ListboxSelect>>', lambda x: recommendation_screen(x, root, items, name_to_id_map,
                                                                      id_to_name_map, transactions))
    listbox.pack()
    for item in relevent:
        listbox.insert(END, item)


def recommendation_screen(event, root, items, name_to_id_map, id_to_name_map, transactions):
    w = event.widget
    index = int(w.curselection()[0])
    chosen_item = w.get(index)
    clear_window(root)

    chosen_id = name_to_id_map[chosen_item]

    all_idds = [name_to_id_map[item] for item in items]
    all_idds.remove(chosen_id)

    recommendations = []

    for idd in all_idds:
        a_and_b = 0.
        a_or_b = 0.
        for transaction in transactions['transactions']:
            if str(chosen_id) in transaction and str(idd) in transaction:
                a_and_b += 1.
            if str(chosen_id) in transaction or str(idd) in transaction:
                a_or_b += 1.
        a_and_b /= len(transactions)
        a_or_b /= len(transactions)
        prob = a_and_b / a_or_b if a_or_b > 0 else 0.
        if prob > 0.:
            recommendations.append((prob, id_to_name_map[idd]))
    recommendations.sort(reverse=True)
    recommendations = recommendations[0:6]
    listbox = Listbox(root, height=15, width=50)
    listbox.pack()
    for item in recommendations:
        listbox.insert(END, (item[1], '$ ' + str(getCost(name_to_id_map[item[1]]))))


def main(im_file):
    camera_screen()
    root = Tk()
    root.minsize(350, 600)
    confirm_screen(root, im_file)
    root.mainloop()


if __name__ == '__main__':
    main(im_file='fruit_display.jpg')
