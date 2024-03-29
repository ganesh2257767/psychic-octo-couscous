import PySimpleGUI as sg
import requests
import json
import os
import concurrent.futures
from threading import Thread
from queue import Queue

os.makedirs('JSON Files', exist_ok=True)
ico_path = os.getcwd()
os.chdir(os.getcwd() + '\\JSON Files')
path = os.getcwd()

url1 = 'https://ws-uat.suddenlink.cequel3.com'
url_findAddress = '/optimum-ecomm-abstraction-ws/rest/uow/findAddress'
url_createShoppingCart = '/optimum-ecomm-abstraction-ws/rest/uow/createShoppingCart'
url_searchProductOffering = '/optimum-ecomm-abstraction-ws/rest/uow/searchProductOffering'
url_updateShoppingCart = '/optimum-ecomm-abstraction-ws/rest/uow/updateShoppingCart'

def find_address(values):
    offer_list = []
    street = values['-STREET-'].upper()
    apt = values['-APT-']
    zip_code = values['-ZIP-']
    if street == "" or zip_code == "":
        sg.PopupError("Street and Zip Code are mandatory!")
    elif not zip_code.isdigit():
        sg.PopupError("Zip Code should be numeric value!")
    elif len(zip_code) > 5:
        sg.PopupError("Zip Code length should not exceed 5 digits!")
    else:
        lst = [k for k, v in values.items() if v == True]
        promo, channel, env = lst
        url_fa = url1 + env + url_findAddress


        findAddress_payload = f'''{{"address1" : "{street}", "address2": "{apt}", "zip" : "{zip_code}"}}'''
        findAddress_request = json.loads(findAddress_payload)
        try:
            findAddress_response = requests.post(url_fa, json=findAddress_request, verify=False).json()
        except:
            sg.PopupError("Network Issue or Altice VPN not connected!")
            return '', ''
        else:
            with open('findAddress_request.json', 'w+', encoding='utf-8') as fa_req:
                fa_req.write(json.dumps(findAddress_request, indent=4))

            with open('findAddress_response.json', 'w+', encoding='utf-8') as fa_res:
                fa_res.write(json.dumps(findAddress_response, indent=4))
            try:
                add_list = findAddress_response["detailedAccounts"][0]
            except IndexError:
                sg.PopupError('Invalid Address')
                return '', ''
            else:
                ftax = add_list["ftax"]
                city = add_list["service_city"]
                state = add_list["service_state"]
                cluster = add_list["clust"]
                market = add_list["mkt"]
                corp = add_list["corp"]
                house = add_list["house"]
                cust = add_list["cust"]
                try:
                    eid = add_list["eligibilityId"]
                except KeyError:
                    eid = ''
            url_csc = url1 + env + url_createShoppingCart

            createShoppingCart_payload = f'''{{"customerType":"R","isCommercialAccept":false,"serviceAddress":{{"apt":"{apt}","fta":"{ftax}","street":"{street}","city":"{city}","state":"{state}","zipcode":"{zip_code}","type":"","clusterCode":"{cluster}","mkt":"{market}","corp":"{corp}","house":"{house}","cust":"{cust}"}},"locale":"en_US"}}'''
            createShoppingCart_request = json.loads(createShoppingCart_payload)
            
            createShoppingCart_response = requests.post(url_csc, json=createShoppingCart_request, verify=False).json()

            with open('createShoppingCart_request.json', 'w+', encoding='utf-8') as csc_req:
                csc_req.write(json.dumps(createShoppingCart_request, indent=4))

            with open('createShoppingCart_response.json', 'w+', encoding='utf-8') as csc_res:
                csc_res.write(json.dumps(createShoppingCart_response, indent=4))
            try:
                response_info = createShoppingCart_response["createShoppingCartRESTReturn"]["responseInfo"]["statusCode"]
                cartID = createShoppingCart_response["createShoppingCartRESTReturn"]["cartId"]
            except:
                cartID = ''
                sg.Popup("Cart ID creation ran into trouble!\n\nCheck Create Shopping Cart Response for possible issue.", title="Error")
                return '', ''
            else:
                if response_info == "1002000013":
                    sg.Popup("Another cart submitted on this address.\nClean the cart and try again.")
                    return '', ''
                else:
                    url_prdOff = url1 + env + url_searchProductOffering

                    searchProductOffering_payload = f'''{{"salesContext":{{"localeString":"en_US","salesChannel":"{channel}"}},"searchProductOfferingFilterInfo":{{"oolAvailable":true,"ovAvailable":true,"ioAvailable":true,"includeExpiredOfferings":false,"salesRuleContext":{{"customerProfile":{{"anonymous":true}},"customerInfo":{{"customerType":"R","newCustomer":true,"orderType":"Install","isPromotion":{promo},"eligibilityID":"{eid}"}}}},"eligibilityStatus":[{{"code":"EA"}}]}},"offeringReadMask":{{"value":"SUMMARY"}},"checkCustomerProductOffering":false,"locale":"en_US","cartId":"{cartID}","serviceAddress":{{"apt":"{apt}","fta":"{ftax}","street":"{street}","city":"{city}","state":"{state}","zipcode":"{zip_code}","type":"","clusterCode":"{cluster}","mkt":"{market}","corp":"{corp}","house":"{house}","cust":"{cust}"}},"generics":false}}'''
                    searchProductOffering_request = json.loads(searchProductOffering_payload)
                    
                    searchProductOffering_response = requests.post(url_prdOff, json=searchProductOffering_request, verify=False).json()
                    offers = searchProductOffering_response["searchProductOfferingReturn"]["productOfferingResults"]

                    for x in offers:
                        offer_list.append(f'''{x["matchingProductOffering"]["ID"]:<7} - {x["matchingProductOffering"]["title"]}''')

                    with open('searchProductOffering_request.json', 'w+', encoding='utf-8') as spo_req:
                        spo_req.write(json.dumps(searchProductOffering_request, indent=4))

                    with open('searchProductOffering_response.json', 'w+', encoding='utf-8') as spo_res:
                        spo_res.write(json.dumps(searchProductOffering_response, indent=4))

                    window['offerID'].update(values = offer_list)
                    window.write_event_value('-DONE-', 'Done')
                    return offers, env, cartID, channel, zip_code, ftax, corp, city, street, market, cluster, state, house, cust

def update_cart(offers, add_details):
    for x in offers:
        if values['offerID'].split('-')[0].strip() == x["matchingProductOffering"]["ID"]:
            spec = [y["productSpecs"][0]["ID"] for y in x["matchingProductOffering"]["productOfferingProductSpecs"]]
            offerID = x["matchingProductOffering"]["ID"]
            offerName = x["matchingProductOffering"]["title"]

            if len(spec) == 1:
                prod_to_conf = f'''{{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[0]}"}}}}'''
            if len(spec) == 2:
                prod_to_conf = f'''{{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[0]}"}}}}, {{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[1]}"}}}}'''
            if len(spec) == 3:
                prod_to_conf = f'''{{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[0]}"}}}}, {{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[1]}"}}}}, {{"productSpecIdentifier":{{"productOfferingID":"{offerID}","productSpecID":"{spec[2]}"}}}}'''

            if values['services']:
                service = json.dumps(list(values['services'].split(',')))
            else:
                service = []
            url_usc = url1 + add_details[0] + url_updateShoppingCart
            updateShoppingCart_payload = f'''{{"cartId":"{add_details[1]}","isCheckEligibility":false,"productsToConfigure":[{prod_to_conf}],"ruleExecutionContext":{{"customerInfo":{{"customerType":"R","newCustomer":true}},"customerProfile":{{"anonymous":true}},"isOffline":false,"isFullXml":true,"productInfo":{{"services":{service}}}}},"saleContext":{{"localeString":"en_US","salesChannel":"{add_details[2]}"}},"locale":"en_US","serviceAddress":{{"zipcode":"{add_details[3]}","fta":"{add_details[4]}","corp":"{add_details[5]}","city":"{add_details[6]}","street":"{add_details[7]}","mkt":"{add_details[8]}","clusterCode":"{add_details[9]}","state":"{add_details[10]}","house":"{add_details[11]}","cust":"{add_details[12]}"}}}}'''
            updateShoppingCart_request = json.loads(updateShoppingCart_payload)

            updateShoppingCart_response = requests.post(url_usc, json=updateShoppingCart_request, verify=False).json()

            with open(f'{offerID}_{offerName}_request.json', 'w+', encoding='utf-8') as usc_req:
                usc_req.write(json.dumps(updateShoppingCart_request, indent=4))

            with open(f'{offerID}_{offerName}_response.json', 'w+', encoding='utf-8') as usc_res:
                usc_res.write(json.dumps(updateShoppingCart_response, indent=4))

            window.write_event_value('-DONE1-', 'Done')


layout1 = [
    [sg.Text('Street Name*', size=(11, 1)), sg.InputText(key='-STREET-', size=(25, 1))],
    [sg.Text('Apt Num', size=(11, 1)), sg.InputText(key='-APT-', size=(25, 1))],
    [sg.Text('Zip Code*', size=(11, 1)), sg.InputText(key='-ZIP-', size=(25, 1))],
    [sg.Text('Promotion', size=(11, 1)), sg.Radio('TRUE', group_id=1, default=True, key='true', size=(5, 1)), sg.Radio('FALSE', group_id=1, key='false', size=(5, 1))],
    [sg.Text('Channel', size=(11, 1)), sg.Radio('DSA', group_id=2, default=True, key='DSL', size=(5, 1)), sg.Radio('ISA', group_id=2, key='ISA', size=(5, 1))],
    [sg.Text('Environment', size=(11, 1)), sg.Radio('UAT', group_id=3, default=True, key='', size=(5, 1)), sg.Radio('UAT1', group_id=3, key='/uat1', size=(5, 1)), sg.Radio('UAT2', group_id=3, key='/uat2', size=(5, 1))],
    [sg.Text(size=(1, 1)), sg.Button('Submit', key='-SUBMIT-', size=(15, 1)), sg.Button('Update Shopping Cart?', key='-UPDATECART-', disabled=True)],
    [sg.Text(size=(9, 1)), sg.Button('Open Folder', key='-FOLD-', size=(15, 1))]

]

layout2 = [
    [sg.Text('Select Offer', size=(11, 1)), sg.Combo([], key='offerID', size=(50, 1))],
    [sg.Text('Enter Services', size=(11, 1)), sg.InputText(key='services', size=(25, 1)), sg.Text('((?))', tooltip='Enter comma-separated, non-spaced Rate Codes.\nDo this if you want any of the Rate Code to be "isAssigned: true" in the EPC response.\nLeave this blank if not sure.')],
    [sg.Text(size=(11, 1)), sg.Button('Back', key='-BACK-', size=(12, 1)), sg.Button('Update Cart', key='-UPDATE-', size=(12, 1)), sg.Button('Open Folder', key='-FOLD1-', size=(12, 1))]
]

layout = [
    [sg.Column(layout1, key='-COL1-'),
    sg.Column(layout2, key='-COL2-', visible=False)]
]

window = sg.Window('Request Reponse', layout, icon=ico_path+'\\req.ico', resizable=True)



while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    
    if event == '-SUBMIT-':
        q1 = Queue()
        Thread(target=lambda q, a: q.put(find_address(a)), args=(q1, values), daemon=True).start()
    
    if event == '-DONE-':
        offers, *add_details = q1.get()
        sg.PopupOK('Done, request response files created.', title='Success')
        window['-UPDATECART-'].update(disabled=False)
                
    if event in ('-FOLD-', '-FOLD1-'):
        os.startfile(path)


    if event == '-UPDATECART-':
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)

    if event == '-BACK-':
        window['-COL1-'].update(visible=True)
        window['-COL2-'].update(visible=False)


    if event == '-UPDATE-':
        Thread(target=lambda q, a, b: q.put(update_cart(a, b)), args=(q1, offers, add_details), daemon=True).start()

    if event == '-DONE1-':
        sg.PopupOK('Done, Shopping cart updated.', title='Success')

window.close()