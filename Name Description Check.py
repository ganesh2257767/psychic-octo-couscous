import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Column
import requests
import json
import pandas as pd
import os

uow_uat1 = 'https://ws-uat.suddenlink.com/uat1/optimum-online-order-ws/rest/OfferService/getBundles'
uow_uat = 'https://ws-uat.suddenlink.com/optimum-online-order-ws/rest/OfferService/getBundles'
dsa_uat = 'https://ws-uat.suddenlink.cequel3.com/optimum-ecomm-abstraction-ws/rest/uow/searchProductOffering'
dsa_uat1 = 'https://ws-uat.suddenlink.cequel3.com/uat1/optimum-ecomm-abstraction-ws/rest/uow/searchProductOffering'

def check(url, req, chann, data):
    try:
        if chann == 'uow':
            res = requests.post(url, json=req, auth=('unittest', 'test01')).json()
            offers = res["productOfferings"]["productOfferingResults"]
        elif chann == 'dsa':
            res = requests.post(url, json=req, verify=False).json()
            offers = res["searchProductOfferingReturn"]["productOfferingResults"]

    except:
        sg.Popup("Something went wrong, try again!")
    else:
        offer_name_desc = {}
        for offer in offers:
            offer_id = offer["matchingProductOffering"]["ID"]
            offer_name = offer["matchingProductOffering"]["title"]
            offer_desc = offer["matchingProductOffering"]["description"]

            offer_name_desc[offer_id] = [offer_name, offer_desc]
        else:
            actual_name = []
            actual_description = []
            result = []
            for oid, name, descr in zip(data['Offer ID'], data['Offer Name'], data['Offer Description']):
                if oid in offer_name_desc.keys():
                    actual_name.append(offer_name_desc[oid][0])
                    actual_description.append(offer_name_desc[oid][1])
                    if descr.strip() == offer_name_desc[oid][1] and name.strip() == offer_name_desc[oid][0]:
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

            try:
                data.to_excel(out_path + '/output.xlsx', index=False)
            except:
                sg.Popup("File already open or present in a folder without permissions!")
            else:
                sg.Popup(f'Statistics of run\nTotal runs: {len(result)}\nPassed: {result.count("Pass")}\nFailed: {result.count("Fail")}\nNA: {result.count("NA")}')
                window['-OPEN-'].update(disabled=False)


opt_markets = ['K', 'M', 'N', 'G']
sdl_markets = ['A', 'B', 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q', 'V']
cluster = [10, 21, 90, 91, 93, 95]

layout0 = [
    [sg.Text('Browse or enter the path to input file.')],
    [sg.In(key='input_file'), sg.FileBrowse(key='file', target='input_file')],
    [sg.Button('Upload', key='upload')]
]
layout = [
    [sg.Text("Select Area", size = (15, 1)), sg.Radio("Optimum", group_id="area", key="opt", enable_events=True, default=True), sg.Radio("Suddenlink", group_id="area", key="sdl", enable_events=True)],
    [sg.Text("Select Channel", size = (15, 1)), sg.Radio("ISA/DSA", group_id="channel", key="dsa", enable_events=True, default=True), sg.Radio("UOW", group_id="channel", key="uow", enable_events=True)],
    [sg.Text("Select Environment", size = (15, 1)), sg.Radio("UAT", group_id="env", key="uat", enable_events=True, default=True), sg.Radio("UAT1", group_id="env", key="uat1", enable_events=True)],
    [sg.Text("Enter Corp", size = (15, 1)), sg.InputText(key='corp', size=(8, 1))],
    [sg.Text("Select Market", size = (15, 1)), sg.DropDown(values = opt_markets, key='market', size=(6, 1))],
    [sg.Text("Select Cluster", size = (15, 1)), sg.DropDown(values = cluster, key='cluster', visible=False, size=(6, 1))],
    [sg.Text("Enter FTAX", size = (15, 1)), sg.InputText(key='ftax', visible=False, size=(8, 1))],
    [sg.Text("Enter EID", size = (15, 1)), sg.InputText(key='eid', visible=False, size=(8, 1))],
    [sg.Button('Upload another file', key='-ANOTHER-'), sg.Submit("Check", key='-SUBMIT-',  size=(10, 1)), sg.Button('Open output file', key='-OPEN-', disabled=True)]
]

main_layout = [
    [sg.Column(layout0, key='-COL1-'),
    sg.Column(layout, visible=False, key='-COL2-')]
]

window = sg.Window('Offer Name/Description Checker', main_layout)


while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'upload':
        if values['file']:
            path = values['file']
            out_path = '/'.join(values['file'].split('/')[:-1])
            data = pd.read_excel(path, usecols = [0, 1, 2], names = ["Offer ID", "Offer Name", "Offer Description"], dtype=str)
            window['-COL1-'].update(visible=False)
            window['-COL2-'].update(visible=True)
        else:
            sg.Popup('Please select an input file!')
    
    if event == 'sdl':
        window['market'].update(values=sdl_markets)
        window['cluster'].update(visible=True)
        window['ftax'].update(visible=True)
        if values['dsa']:
            window['eid'].update(visible=True)
        else:
            window['eid'].update(visible=False)

    if event == 'opt':
        window['market'].update(values=opt_markets)
        window['cluster'].update(visible=False)
        window['ftax'].update(visible=False)
        window['eid'].update(visible=False)

    if event == 'dsa':
        if values['sdl']:
            window['eid'].update(visible=True)

    if event == 'uow':
        window['eid'].update(visible=False)

    if event == '-SUBMIT-':
        # if all([values['market'], values['corp'], values['cluster'], values['ftax'], values['eid']]):
        if values['sdl'] and values['uow']:
            if all([values['market'], values['corp'], values['cluster'], values['ftax']]):
                if values['uat']:
                    url = uow_uat
                else:
                    url = uow_uat1
                payload = f'''{{"productOfferingsRequest":{{"customerInteractionId":"1228012","accountDetails":{{"clust":"{values['cluster']}","corp":"{values['corp']}","cust":"1","eligibilityId": "test","ftax":"{values['ftax']}","hfstatus":"3","house":"test","id":0,"mkt":"{values['market']}","service_housenbr":"test","servicestreetaddr":"test","service_aptn": "test","service_city":"test","service_state":"test","service_zipcode":"test","tdrop": "O"}},"newCustomer":true,"sessionId":"LDPDPJCBBH08VVL9KKY","shoppingCartId":"FTJXQYDN","footprint": "suddenlink"}}}}'''
                req = json.loads(payload)
                check(url, req, 'uow', data)
            else:
                sg.Popup('Enter all the values!')

        elif values['opt'] and values['uow']:
            if all([values['market'], values['corp']]):
                if values['uat']:
                    url = uow_uat
                else:
                    url = uow_uat1
                payload = f'''{{"productOfferingsRequest":{{"customerInteractionId":"1228012","accountDetails":{{"clust":"86","corp":"{values['corp']}","cust":"1","ftax":"72","hfstatus":"3","house":"test","id":0,"mkt":"{values['market']}","service_housenbr":"test","servicestreetaddr":"test","service_aptn": "test","service_city":"test","service_state":"test","service_zipcode":"test"}},"newCustomer":true,"sessionId":"LDPDPJCBBH08VVL9KKY","shoppingCartId":"FTJXQYDN"}}}}'''
                req = json.loads(payload)
                check(url, req, 'uow', data)
            else:
                sg.Popup('Enter all the values!')
        
        elif values['sdl'] and values['dsa']:
            if all([values['market'], values['corp'], values['cluster'], values['ftax'], values['eid']]):
                if values['uat']:
                    url = dsa_uat
                else:
                    url = dsa_uat1
                payload = f'''{{"salesContext":{{"localeString":"en_US","salesChannel":"DSL"}},"searchProductOfferingFilterInfo":{{"oolAvailable":true,"ovAvailable":true,"ioAvailable":true,"includeExpiredOfferings":false,"salesRuleContext":{{"customerProfile":{{"anonymous":true}},"customerInfo":{{"customerType":"R","newCustomer":true,"orderType":"Install","isPromotion":true,"eligibilityID":"{values['eid']}"}}}},"eligibilityStatus":[{{"code":"EA"}}]}},"offeringReadMask":{{"value":"SUMMARY"}},"checkCustomerProductOffering":false,"locale":"en_US","cartId":"FTJXQYDN","serviceAddress":{{"apt":"test","fta":"{values['ftax']}","street":"test","city":"test","state":"test","zipcode":"test","type":"","clusterCode":"{values['cluster']}","mkt":"{values['market']}","corp":"{values['corp']}","house":"test","cust":"1"}},"generics":false}}'''
                req = json.loads(payload)
                check(url, req, 'dsa', data)
            else:
                sg.Popup('Enter all the values!')

        elif values['opt'] and values['dsa']:
            if all([values['market'], values['corp']]):
                if values['uat']:
                    url = dsa_uat
                else:
                    url = dsa_uat1
                payload = f'''{{"salesContext":{{"localeString":"en_US","salesChannel":"DSL"}},"searchProductOfferingFilterInfo":{{"oolAvailable":true,"ovAvailable":true,"ioAvailable":true,"includeExpiredOfferings":false,"salesRuleContext":{{"customerProfile":{{"anonymous":true}},"customerInfo":{{"customerType":"R","newCustomer":true,"orderType":"Install","isPromotion":true,"eligibilityID":"test"}}}},"eligibilityStatus":[{{"code":"EA"}}]}},"offeringReadMask":{{"value":"SUMMARY"}},"checkCustomerProductOffering":false,"locale":"en_US","cartId":"FTJXQYDN","serviceAddress":{{"apt":"test","fta":"40","street":"test","city":"test","state":"test","zipcode":"test","type":"","clusterCode":"86","mkt":"{values['market']}","corp":"{values['corp']}","house":"test","cust":"1"}},"generics":false}}'''
                req = json.loads(payload)
                check(url, req, 'dsa', data)
            else:
                sg.Popup('Enter all the values!')


    if event == '-OPEN-':
        os.startfile(out_path + '/output.xlsx')

    if event == '-ANOTHER-':
        window['-COL2-'].update(visible=False)
        window['-COL1-'].update(visible=True)
        

window.close()