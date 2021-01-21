import PySimpleGUI as sg
import requests
import json
import pandas as pd
import os

url_uat_opt = "https://ws-uat.suddenlink.com:443/optimum-online-order-ws/rest/OfferService/getBundles"
url_uat_sdl = "https://ws-uat.suddenlink.com/optimum-online-order-ws/rest/OfferService/getBundles"


def check(url, req):
    print(f'URL received: {url}\nRequest received: {req}')
    res = requests.post(url, json=req, auth=('unittest', 'test01')).json()
    print(json.dumps(res, indent=4))
    try:
        offers = res["productOfferings"]["productOfferingResults"]
    except:
        sg.Popup("Something went wrong, try again!")
    else:
        offer_name_desc = {}
        for offer in offers:
            
            offer_id = offer["matchingProductOffering"]["ID"]
            offer_name = offer["matchingProductOffering"]["title"]
            # offer_bullet = offer["matchingProductOffering"]["bulletPoints"]["bulletPoint"]
            offer_desc = offer["matchingProductOffering"]["description"]

            offer_name_desc[offer_id] = [offer_name, offer_desc]
        print("Offers from API: ", offer_name_desc)
        try:
            data = pd.read_excel('input.xlsx', usecols = [0, 1, 2], names = ["Offer ID", "Offer Name", "Offer Description"])
        except:
            sg.Popup("Input file not in the same directory as code!")
        else:
            actual_name = []
            actual_description = []
            result = []
            for oid, descr in zip(data['Offer ID'], data['Offer Description']):
                if oid in offer_name_desc.keys():
                    print("Match")
                    actual_name.append(offer_name_desc[oid][0])
                    actual_description.append(offer_name_desc[oid][1])
                    if descr == offer_name_desc[oid][1]:
                        result.append('Pass')
                    else:
                        result.append('Fail')
                else:
                    actual_name.append("Not found")
                    actual_description.append("Not found")
                    result.append('NA')

            data["Actual Name"] = actual_name
            data["Actual Description"] = actual_description
            data["Result"] = result

            print(f'Statistics of run\nTotal runs: {len(result)}\nPassed: {result.count("Pass")}\nFailed: {result.count("Fail")}\nNA: {result.count("NA")}')
            try:
                data.to_excel('output.xlsx', index=False)
                print("Data written to excel")
            except:
                sg.Popup("File already open or present in folder without permissions!")
            else:
                sg.Popup("Done!")
                window['-OPEN-'].update(disabled=False)


opt_markets = ['K', 'M', 'N', 'G']
sdl_markets = ['D', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'V']
cluster = [10, 21, 91, 91, 93, 95]
layout = [
    [sg.Text("Select Area", size = (15, 1)), sg.Radio("Optimum", group_id="area", key="opt", enable_events=True, default=True), sg.Radio("Suddenlink", group_id="area", key="sdl", enable_events=True)],
    [sg.Text("Enter Corp", size = (15, 1)), sg.InputText(key='corp', size=(5, 1))],
    [sg.Text("Select Market", size = (15, 1)), sg.DropDown(values = opt_markets, key='market', size=(5, 1))],
    [sg.Text("Select Cluster", size = (15, 1)), sg.DropDown(values = cluster, key='cluster', visible=False, size=(5, 1))],
    [sg.Text("Enter FTAX", size = (15, 1)), sg.InputText(key='ftax', visible=False, size=(5, 1))],
    [sg.Text("", size = (15, 1)), sg.Submit("Go", key='-SUBMIT-',  size=(5, 1)), sg.Button('Open output file', key='-OPEN-', disabled=True)]
]

window = sg.Window('Offer Name/Description Checker', layout)


while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'sdl':
        window['market'].update(values=sdl_markets)
        window['cluster'].update(visible=True)
        window['ftax'].update(visible=True)
        payload = f'''{{"productOfferingsRequest":{{"customerInteractionId":"1228012","accountDetails":{{"clust":"{values['cluster']}","corp":"{values['corp']}","cust":"1","eligibilityId": "test","ftax":"{values['ftax']}","hfstatus":"3","house":"test","id":0,"mkt":"{values['market']}","service_housenbr":"test","servicestreetaddr":"test","service_aptn": "test","service_city":"test","service_state":"test","service_zipcode":"test","tdrop": "O"}},"newCustomer":true,"sessionId":"LDPDPJCBBH08VVL9KKY","shoppingCartId":"FTJXQYDN","footprint": "suddenlink"}}}}'''
        url = url_uat_sdl

    if event == 'opt':
        window['market'].update(values=opt_markets)
        window['cluster'].update(visible=False)
        window['ftax'].update(visible=False)
        window.refresh()
        payload = f'''{{"productOfferingsRequest":{{"customerInteractionId":"1228012","accountDetails":{{"clust":"86","corp":"{values['corp']}","cust":"1","ftax":"72","hfstatus":"3","house":"test","id":0,"mkt":"{values['market']}","service_housenbr":"test","servicestreetaddr":"test","service_aptn": "test","service_city":"test","service_state":"test","service_zipcode":"test"}},"newCustomer":true,"sessionId":"LDPDPJCBBH08VVL9KKY","shoppingCartId":"FTJXQYDN"}}}}'''
        req = json.loads(payload)
        url = url_uat_opt
        

    if event == '-SUBMIT-':
        if values['sdl']:
            payload = f'''{{"productOfferingsRequest":{{"customerInteractionId":"1228012","accountDetails":{{"clust":"{values['cluster']}","corp":"{values['corp']}","cust":"1","eligibilityId": "test","ftax":"{values['ftax']}","hfstatus":"3","house":"test","id":0,"mkt":"{values['market']}","service_housenbr":"test","servicestreetaddr":"test","service_aptn": "test","service_city":"test","service_state":"test","service_zipcode":"test","tdrop": "O"}},"newCustomer":true,"sessionId":"LDPDPJCBBH08VVL9KKY","shoppingCartId":"FTJXQYDN","footprint": "suddenlink"}}}}'''
            req = json.loads(payload)
            check(url_uat_sdl, req)
        else:
            payload = f'''{{"productOfferingsRequest":{{"customerInteractionId":"1228012","accountDetails":{{"clust":"86","corp":"{values['corp']}","cust":"1","ftax":"72","hfstatus":"3","house":"test","id":0,"mkt":"{values['market']}","service_housenbr":"test","servicestreetaddr":"test","service_aptn": "test","service_city":"test","service_state":"test","service_zipcode":"test"}},"newCustomer":true,"sessionId":"LDPDPJCBBH08VVL9KKY","shoppingCartId":"FTJXQYDN"}}}}'''
            req = json.loads(payload)
            print(json.dumps(req, indent=4))
            check(url_uat_opt, req)

    if event == '-OPEN-':
        os.startfile('output.xlsx')
        

window.close()