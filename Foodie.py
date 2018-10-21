import cv2
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from tkinter import *
from PIL import ImageTk, Image
import http.client
import requests
import pprint
import json
import simplejson
import heapq


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

    # payload = "{\"pageNumber\":0," \
    #           "\"pageSize\":200,\"returnedFields\":[],\"tlogId\":\"String\"," \
    #           "\"receiptNumber\":\"String\",\"transactionNumber\":\"String\",\"siteInfoIds\":[\"String\"]," \
    #           "\"fromTransactionDateTimeUtc\":{\"dateTime\":\"2018-04-04T14:34:59.053Z\"," \
    #           "\"originalOffset\":\"String\"}," \
    #           "\"toTransactionDateTimeUtc\":{\"dateTime\":\"2018-04-04T14:34:59.053Z\"," \
    #           "\"originalOffset\":\"String\"},\"businessDay\":{\"dateTime\":\"2018-04-04T14:34:59.053Z\"," \
    #           "\"originalOffset\":\"String\"}," \
    #           "\"endTransactionDateTimeUtc\":{\"dateTime\":\"2018-04-04T14:34:59.053Z\"," \
    #           "\"originalOffset\":\"String\"},\"closeDateTimeUtc\":{\"dateTime\":\"2018-04-04T14:34:59.053Z\"," \
    #           "\"originalOffset\":\"String\"},\"touchPointId\":\"String\"," \
    #           "\"transactionCategories\":[\"String\"]," \
    #           "\"isTrainingMode\":false,\"employeeId\":\"String\",\"employeeName\":\"String\"," \
    #           "\"transactionTypes\":[\"SALES\"],\"isSuspended\":false,\"isResumed\":false,\"isRecalled\":false," \
    #           "\"isVoided\":false,\"grandAmount\":{\"amount\":78.3},\"tenderAmount\":{\"amount\":78.3}," \
    #           "\"tenderId\":\"String\",\"touchPointType\":\"String\",\"touchPointGroups\":[\"String\"]," \
    #           "\"linkedTransactionIds\":[\"String\"],\"dataProviderName\":\"String\"," \
    #           "\"dataProviderVersion\":\"String\",\"tenderTypes\":[\"GENERIC\"],\"sourceAccount\":\"String\"," \
    #           "\"destinationAccount\":\"String\",\"itemProductIds\":[\"String\"],\"isItemReturn\":false," \
    #           "\"isItemReturnAffectsInventory\":false,\"isItemVoided\":false," \
    #           "\"itemRegularUnitPrice\":{\"amount\":78.3},\"itemActualUnitPrice\":{\"amount\":78.3}," \
    #           "\"itemDepartmentIds\":[\"String\"],\"customerId\":\"String\",\"customerEmail\":\"String\"," \
    #           "\"customerPhoneNumber\":\"String\",\"customerName\":\"String\"," \
    #           "\"loyaltyCardNumbers\":[\"String\"]," \
    #           "\"itemDiscountIds\":[\"String\"],\"discountIds\":[\"String\"],\"promotionIds\":[\"String\"]," \
    #           "\"itemPromotionIds\":[\"String\"],\"couponIds\":[\"String\"]}"

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
            img = Image.open(im_file)
            img = img.resize((300, int(float(img.height) / img.width * 300)))
            img = ImageTk.PhotoImage(img)
            canvas = Canvas(root, width=img.width(), height=img.height())
            canvas.pack()
            canvas.create_image(0, 0, anchor=NW, image=img)
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

    def on_select(event, select_set):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        select_set.add(value)

    selected = set()

    root = Tk()
    img = Image.open(im_file)
    img = img.resize((300, int(float(img.height) / img.width * 300)))
    img = ImageTk.PhotoImage(img)
    canvas = Canvas(root, width=img.width(), height=img.height())
    canvas.pack()
    canvas.create_image(0, 0, anchor=NW, image=img)
    listbox = Listbox(root)
    listbox.bind('<<ListboxSelect>>', lambda x: on_select(x, selected))
    listbox.pack()
    for item in tags:
        listbox.insert(END, item[0])
    root.mainloop()

    # FILTER
    tag_names = selected if len(selected) > 0 else [tags[0][0]]
    items, name_to_id_map, id_to_name_map = get_catalog()
    relevent = []
    for i in range(len(items)):
        for name in tag_names:
            if name in items[i]:
                relevent.append(items[i])
                continue

    def choose(event, chosen_option, root):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        chosen_option[0] = value
        root.destroy()

    chosen_item = [None]

    root = Tk()
    img = Image.open(im_file)
    img = img.resize((300, int(float(img.height) / img.width * 300)))
    img = ImageTk.PhotoImage(img)
    canvas = Canvas(root, width=img.width(), height=img.height())
    canvas.pack()
    canvas.create_image(0, 0, anchor=NW, image=img)
    listbox = Listbox(root, height=15, width=50, selectmode='SINGLE')
    listbox.bind('<<ListboxSelect>>', lambda x: choose(x, chosen_item, root))
    listbox.pack()
    for item in relevent:
        listbox.insert(END, item)
    root.mainloop()

    chosen_item = chosen_item[0]
    chosen_id = name_to_id_map[chosen_item]

    print(chosen_item, chosen_id)

    transactions = get_transactions(cache=True)

    all_idds = [name_to_id_map[item] for item in items]
    all_idds.remove(chosen_id)

    recommendations = []

    for idd in all_idds:
        a_and_b = 0.
        a_or_b = 0.
        for transaction in transactions['transactions']:
            if chosen_id in transaction and str(idd) in transaction:
                a_and_b += 1.
            if chosen_id in transaction or str(idd) in transaction:
                a_or_b += 1.
        a_and_b /= len(transactions)
        a_or_b /= len(transactions)
        recommendations.append(a_and_b/a_or_b if a_or_b > 0 else 0.)
    recommendations.sort()

    pp = pprint.PrettyPrinter(depth=4)
    pp.pprint(recommendations)



if __name__ == '__main__':
    # main()
    tran = get_transactions(cache=True)

    items, name_to_id_map, id_to_name_map = get_catalog()

    common_items = dict()

    for t in tran['transactions']:
        items = [id_to_name_map[int(idd)] for idd in t]
        for item in items:
            if item not in common_items:
                common_items[item] = 1
            else:
                common_items[item] += 1
    list_common_items = []
    for name, count in common_items.items():
        list_common_items.append((count, name))
    list_common_items.sort(reverse=True)
    pp = pprint.PrettyPrinter(depth=4)
    pp.pprint(list_common_items)
    # print(id_to_name_map[33120])
